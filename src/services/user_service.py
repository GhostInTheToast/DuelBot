"""User service for handling user-related business logic."""
import logging
from typing import List, Optional

from models import User, UserStats

from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class UserService:
    """Service for user-related operations."""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    async def get_or_create_user(self, user_id: int, username: str, display_name: str, guild_id: int) -> User:
        """Get existing user or create new one."""
        user = await self.db.get_user(user_id, guild_id)
        if not user:
            user = await self.db.create_user(user_id, username, display_name, guild_id)
            logger.info(f"Created new user: {username} in guild {guild_id}")
        return user
    
    async def get_user_profile(self, user_id: int, guild_id: int) -> Optional[UserStats]:
        """Get detailed user profile with statistics."""
        return await self.db.get_user_stats(user_id, guild_id)
    
    async def update_user_after_duel(self, user_id: int, guild_id: int, won: bool, damage_dealt: int, damage_taken: int, opponent_level: int = 1, opponent_is_outlaw: bool = False):
        """Update user statistics after a duel with XP and leveling."""
        from datetime import date, datetime

        # Get current user to calculate proper increments
        user = await self.db.get_user(user_id, guild_id)
        if not user:
            logger.error(f"User {user_id} not found in guild {guild_id}")
            return

        # Check if this is the first duel today
        today = date.today()
        is_first_duel_today = user.last_duel_date is None or user.last_duel_date.date() != today

        # Reset duels_today if it's a new day
        new_duels_today = 1 if is_first_duel_today else user.duels_today + 1

        # Calculate XP gain
        xp_gained = user.calculate_xp_gain(won, damage_dealt, opponent_level, is_first_duel_today, opponent_is_outlaw)
        new_experience = user.experience + xp_gained

        # Calculate new level
        new_level = await self.calculate_level(new_experience)
        level_up = new_level > user.level

        # Calculate new values
        new_duels_played = user.duels_played + 1
        new_total_damage_dealt = user.total_damage_dealt + damage_dealt
        new_total_damage_taken = user.total_damage_taken + damage_taken

        updates = {
            'duels_played': new_duels_played,
            'duels_today': new_duels_today,
            'last_duel_date': datetime.now(),
            'total_damage_dealt': new_total_damage_dealt,
            'total_damage_taken': new_total_damage_taken,
            'experience': new_experience,
            'level': new_level
        }

        if won:
            new_wins = user.wins + 1
            new_win_streak = user.win_streak + 1
            new_best_win_streak = max(user.best_win_streak, new_win_streak)
            
            # Check if user becomes an outlaw (5+ win streak)
            new_is_outlaw = new_win_streak >= 5

            updates.update({
                'wins': new_wins,
                'win_streak': new_win_streak,
                'best_win_streak': new_best_win_streak,
                'is_outlaw': new_is_outlaw
            })
        else:
            # Reset outlaw status when losing
            updates.update({
                'losses': user.losses + 1,
                'win_streak': 0,
                'is_outlaw': False
            })

        await self.db.update_user_stats(user_id, guild_id, **updates)
        logger.info(f"Updated user {user_id} stats after duel: {updates}")

        return {
            'xp_gained': xp_gained,
            'level_up': level_up,
            'new_level': new_level,
            'duels_today': new_duels_today,
            'is_outlaw': updates.get('is_outlaw', False)
        }
    
    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[User]:
        """Get guild leaderboard."""
        return await self.db.get_leaderboard(guild_id, limit)
    
    async def calculate_level(self, experience: int) -> int:
        """Calculate user level based on experience using grindy formula."""
        if experience <= 0:
            return 1
        
        # Much more grindy formula: level^3 * 10 + level * 100
        # Level 1 starts at 0 XP, level 2 requires 170 XP, etc.
        level = 1
        while level < 99:
            # Calculate XP required for the NEXT level (level + 1)
            next_level = level + 1
            required_xp = int((next_level ** 3) * 10) + (next_level * 100)
            if experience < required_xp:
                break
            level += 1
        
        return min(level, 99)  # Cap at 99
    
    async def add_experience(self, user_id: int, guild_id: int, exp_amount: int) -> User:
        """Add experience to user and update level."""
        user = await self.db.get_user(user_id, guild_id)
        if not user:
            return None
        
        new_experience = user.experience + exp_amount
        new_level = await self.calculate_level(new_experience)
        
        updates = {
            'experience': new_experience,
            'level': new_level
        }
        
        updated_user = await self.db.update_user_stats(user_id, guild_id, **updates)
        return updated_user
