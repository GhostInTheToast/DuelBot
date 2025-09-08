"""Duel service for handling duel-related business logic."""
import logging
import random
from datetime import datetime
from typing import Optional, Tuple

from models import Duel, DuelStatus, MoveType

from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class DuelService:
    """Service for duel-related operations."""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    async def create_duel(self, challenger_id: int, challenged_id: int, guild_id: int) -> Duel:
        """Create a new duel challenge."""
        # Check if either user has a pending duel
        challenger_pending = await self.db.get_pending_duel(challenger_id, guild_id)
        challenged_pending = await self.db.get_pending_duel(challenged_id, guild_id)
        
        if challenger_pending:
            raise ValueError("You already have a pending duel!")
        if challenged_pending:
            raise ValueError("The challenged user already has a pending duel!")
        
        duel = await self.db.create_duel(challenger_id, challenged_id, guild_id)
        logger.info(f"Created duel {duel.duel_id} between {challenger_id} and {challenged_id}")
        return duel
    
    async def accept_duel(self, user_id: int, guild_id: int) -> Optional[Duel]:
        """Accept a pending duel."""
        duel = await self.db.get_pending_duel(user_id, guild_id)
        if not duel:
            return None
        
        if duel.challenged_id != user_id:
            raise ValueError("You can only accept duels you were challenged to!")
        
        # Start the duel
        await self.db.update_duel(
            duel.duel_id,
            status=DuelStatus.ACTIVE,
            started_at=datetime.utcnow()
        )
        
        updated_duel = await self.db.get_duel(duel.duel_id)
        logger.info(f"Duel {duel.duel_id} accepted and started")
        return updated_duel
    
    async def decline_duel(self, user_id: int, guild_id: int) -> bool:
        """Decline a pending duel."""
        duel = await self.db.get_pending_duel(user_id, guild_id)
        if not duel:
            return False
        
        if duel.challenged_id != user_id:
            raise ValueError("You can only decline duels you were challenged to!")
        
        await self.db.update_duel(
            duel.duel_id,
            status=DuelStatus.CANCELLED,
            ended_at=datetime.utcnow()
        )
        
        logger.info(f"Duel {duel.duel_id} declined")
        return True
    
    async def cancel_duel(self, user_id: int, guild_id: int) -> bool:
        """Cancel a pending duel (challenger only)."""
        duel = await self.db.get_pending_duel(user_id, guild_id)
        if not duel:
            return False
        
        if duel.challenger_id != user_id:
            raise ValueError("You can only cancel duels you started!")
        
        await self.db.update_duel(
            duel.duel_id,
            status=DuelStatus.CANCELLED,
            ended_at=datetime.utcnow()
        )
        
        logger.info(f"Duel {duel.duel_id} cancelled by challenger")
        return True
    
    async def make_move(self, user_id: int, guild_id: int, move_type: MoveType) -> Tuple[Duel, str]:
        """Make a move in an active duel."""
        duel = await self.db.get_pending_duel(user_id, guild_id)
        if not duel or not duel.is_active:
            raise ValueError("You don't have an active duel!")
        
        if user_id not in [duel.challenger_id, duel.challenged_id]:
            raise ValueError("You're not part of this duel!")
        
        # Calculate move effects
        damage, healing, message = await self._calculate_move_effects(duel, user_id, move_type)
        
        # Apply effects
        if user_id == duel.challenger_id:
            new_hp = max(0, duel.challenged_hp - damage)
            await self.db.update_duel(duel.duel_id, challenged_hp=new_hp)
        else:
            new_hp = max(0, duel.challenger_hp - damage)
            await self.db.update_duel(duel.duel_id, challenger_hp=new_hp)
        
        # Add healing
        if healing > 0:
            if user_id == duel.challenger_id:
                current_hp = await self._get_user_hp(duel, user_id)
                new_hp = min(100, current_hp + healing)
                await self.db.update_duel(duel.duel_id, challenger_hp=new_hp)
            else:
                current_hp = await self._get_user_hp(duel, user_id)
                new_hp = min(100, current_hp + healing)
                await self.db.update_duel(duel.duel_id, challenged_hp=new_hp)
        
        # Record the move
        await self.db.add_duel_move(duel.duel_id, user_id, move_type, damage, healing)
        
        # Check for duel end
        updated_duel = await self.db.get_duel(duel.duel_id)
        winner = await self._check_duel_end(updated_duel)
        
        if winner:
            await self._end_duel(updated_duel, winner)
        
        return updated_duel, message
    
    async def _calculate_move_effects(self, duel: Duel, user_id: int, move_type: MoveType) -> Tuple[int, int, str]:
        """Calculate the effects of a move."""
        attack_power = duel.get_user_attack(user_id)
        defense = duel.get_user_defense(user_id)
        
        if move_type == MoveType.ATTACK:
            # Base damage with some randomness
            base_damage = attack_power + random.randint(-2, 3)
            damage = max(1, base_damage)
            return damage, 0, f"attacks for {damage} damage!"
        
        elif move_type == MoveType.DEFEND:
            # Defend reduces incoming damage next turn
            return 0, 0, "defends, reducing incoming damage!"
        
        elif move_type == MoveType.HEAL:
            # Heal for a percentage of max HP
            heal_amount = random.randint(5, 15)
            return 0, heal_amount, f"heals for {heal_amount} HP!"
        
        elif move_type == MoveType.SPECIAL:
            # Special move with higher damage but less accuracy
            if random.random() < 0.7:  # 70% accuracy
                damage = attack_power * 2 + random.randint(0, 5)
                return damage, 0, f"uses a special attack for {damage} damage!"
            else:
                return 0, 0, "tries a special attack but misses!"
        
        return 0, 0, "does nothing!"
    
    async def _get_user_hp(self, duel: Duel, user_id: int) -> int:
        """Get current HP for a user in a duel."""
        updated_duel = await self.db.get_duel(duel.duel_id)
        return updated_duel.get_user_hp(user_id)
    
    async def _check_duel_end(self, duel: Duel) -> Optional[int]:
        """Check if duel should end and return winner ID."""
        if duel.challenger_hp <= 0 and duel.challenged_hp <= 0:
            return None  # Draw
        elif duel.challenger_hp <= 0:
            return duel.challenged_id
        elif duel.challenged_hp <= 0:
            return duel.challenger_id
        return None
    
    async def _end_duel(self, duel: Duel, winner_id: Optional[int]):
        """End the duel and update user statistics."""
        status = DuelStatus.COMPLETED if winner_id else DuelStatus.COMPLETED
        await self.db.update_duel(
            duel.duel_id,
            status=status,
            winner_id=winner_id,
            ended_at=datetime.utcnow()
        )
        
        # Update user statistics
        challenger_won = winner_id == duel.challenger_id
        challenged_won = winner_id == duel.challenged_id
        
        # This would need to be implemented with proper damage tracking
        # For now, just update basic win/loss stats
        # await self.user_service.update_user_after_duel(...)
        
        logger.info(f"Duel {duel.duel_id} ended. Winner: {winner_id or 'Draw'}")
    
    async def get_duel_status(self, user_id: int, guild_id: int) -> Optional[Duel]:
        """Get current duel status for a user."""
        return await self.db.get_pending_duel(user_id, guild_id)
