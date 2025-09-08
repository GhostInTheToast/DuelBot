"""Database service for handling all database operations."""
import logging
from typing import List, Optional

from database import db
from models import Duel, DuelMove, MoveType, User, UserStats

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        self.db = db
    
    async def initialize(self):
        """Initialize database connection."""
        await self.db.connect()
    
    async def close(self):
        """Close database connection."""
        await self.db.close()
    
    # User operations
    async def get_user(self, user_id: int, guild_id: int) -> Optional[User]:
        """Get user by ID and guild."""
        data = await self.db.get_user(user_id, guild_id)
        return User.from_dict(data) if data else None
    
    async def create_user(self, user_id: int, username: str, display_name: str, guild_id: int) -> User:
        """Create or update user."""
        data = await self.db.create_user(user_id, username, display_name, guild_id)
        return User.from_dict(data)
    
    async def update_user_stats(self, user_id: int, guild_id: int, **kwargs) -> Optional[User]:
        """Update user statistics."""
        data = await self.db.update_user_stats(user_id, guild_id, **kwargs)
        return User.from_dict(data) if data else None
    
    async def get_user_stats(self, user_id: int, guild_id: int) -> Optional[UserStats]:
        """Get detailed user statistics."""
        data = await self.db.get_user_stats(user_id, guild_id)
        if not data:
            return None
        
        user = User.from_dict(data)
        return UserStats(
            user=user,
            duels_won=data.get('duels_won', 0),
            duels_lost=data.get('duels_lost', 0),
            duels_drawn=data.get('duels_drawn', 0)
        )
    
    # Duel operations
    async def create_duel(self, challenger_id: int, challenged_id: int, guild_id: int) -> Duel:
        """Create a new duel."""
        data = await self.db.create_duel(challenger_id, challenged_id, guild_id)
        return Duel.from_dict(data)
    
    async def get_duel(self, duel_id: int) -> Optional[Duel]:
        """Get duel by ID."""
        data = await self.db.get_duel(duel_id)
        return Duel.from_dict(data) if data else None
    
    async def get_pending_duel(self, user_id: int, guild_id: int) -> Optional[Duel]:
        """Get pending duel for a user."""
        data = await self.db.get_pending_duel(user_id, guild_id)
        return Duel.from_dict(data) if data else None
    
    async def update_duel(self, duel_id: int, **kwargs) -> Optional[Duel]:
        """Update duel data."""
        # Convert DuelStatus enum to string if present
        if 'status' in kwargs and hasattr(kwargs['status'], 'value'):
            kwargs['status'] = kwargs['status'].value
        
        data = await self.db.update_duel(duel_id, **kwargs)
        return Duel.from_dict(data) if data else None
    
    async def add_duel_move(self, duel_id: int, user_id: int, move_type: MoveType, damage: int = 0, healing: int = 0) -> DuelMove:
        """Add a move to a duel."""
        data = await self.db.add_duel_move(duel_id, user_id, move_type.value, damage, healing)
        return DuelMove.from_dict(data)
    
    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[User]:
        """Get guild leaderboard."""
        data_list = await self.db.get_leaderboard(guild_id, limit)
        return [User.from_dict(data) for data in data_list]
    
    async def get_duel_moves(self, duel_id: int) -> List[DuelMove]:
        """Get all moves for a duel."""
        # This would need to be implemented in the database module
        # For now, return empty list
        return []
