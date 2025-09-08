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
    
    async def update_user_after_duel(self, user_id: int, guild_id: int, won: bool, damage_dealt: int, damage_taken: int):
        """Update user statistics after a duel."""
        updates = {
            'duels_played': 1,  # This should be incremented, not set to 1
            'total_damage_dealt': damage_dealt,
            'total_damage_taken': damage_taken
        }
        
        if won:
            updates['wins'] = 1  # This should be incremented
            updates['win_streak'] = 1  # This should be incremented
        else:
            updates['losses'] = 1  # This should be incremented
            updates['win_streak'] = 0  # Reset win streak
        
        # Get current user to calculate proper increments
        user = await self.db.get_user(user_id, guild_id)
        if user:
            updates['duels_played'] = user.duels_played + 1
            updates['total_damage_dealt'] = user.total_damage_dealt + damage_dealt
            updates['total_damage_taken'] = user.total_damage_taken + damage_taken
            
            if won:
                updates['wins'] = user.wins + 1
                updates['win_streak'] = user.win_streak + 1
                updates['best_win_streak'] = max(user.best_win_streak, user.win_streak + 1)
            else:
                updates['losses'] = user.losses + 1
                updates['win_streak'] = 0
        
        await self.db.update_user_stats(user_id, guild_id, **updates)
        logger.info(f"Updated user {user_id} stats after duel")
    
    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[User]:
        """Get guild leaderboard."""
        return await self.db.get_leaderboard(guild_id, limit)
    
    async def calculate_level(self, experience: int) -> int:
        """Calculate user level based on experience."""
        # Simple level calculation: 100 exp per level
        return max(1, experience // 100 + 1)
    
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
