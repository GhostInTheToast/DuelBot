"""Database management for DuelBot."""
import logging
from typing import Any, Dict, List, Optional

import asyncpg

from config import Config

logger = logging.getLogger(__name__)

class Database:
    """Database connection and operations manager."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool."""
        try:
            # Build connection string
            if Config.DATABASE_URL and Config.DATABASE_URL != 'postgresql://localhost/duelbot':
                connection_string = Config.DATABASE_URL
            else:
                # Use default PostgreSQL connection for local development
                connection_string = f"postgresql://{Config.DB_USER or 'gost'}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
            
            self.pool = await asyncpg.create_pool(
                connection_string,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created successfully")
            
            # Initialize database schema
            await self._init_schema()
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def _init_schema(self):
        """Initialize database schema."""
        async with self.pool.acquire() as conn:
            # Drop existing tables if they exist (for schema updates)
            await conn.execute("DROP TABLE IF EXISTS duel_moves CASCADE")
            await conn.execute("DROP TABLE IF EXISTS duels CASCADE")
            await conn.execute("DROP TABLE IF EXISTS users CASCADE")
            # Create users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255),
                    guild_id BIGINT NOT NULL,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    win_streak INTEGER DEFAULT 0,
                    best_win_streak INTEGER DEFAULT 0,
                    total_damage_dealt INTEGER DEFAULT 0,
                    total_damage_taken INTEGER DEFAULT 0,
                    duels_played INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            
            # Create duels table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS duels (
                    duel_id SERIAL PRIMARY KEY,
                    challenger_id BIGINT NOT NULL,
                    challenged_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    winner_id BIGINT,
                    challenger_hp INTEGER DEFAULT 100,
                    challenged_hp INTEGER DEFAULT 100,
                    challenger_attack INTEGER DEFAULT 10,
                    challenged_attack INTEGER DEFAULT 10,
                    challenger_defense INTEGER DEFAULT 5,
                    challenged_defense INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    ended_at TIMESTAMP
                )
            """)
            
            # Create duel_moves table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS duel_moves (
                    move_id SERIAL PRIMARY KEY,
                    duel_id INTEGER REFERENCES duels(duel_id),
                    user_id BIGINT NOT NULL,
                    move_type VARCHAR(20) NOT NULL,
                    damage INTEGER DEFAULT 0,
                    healing INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_guild_id ON users(guild_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_duels_guild_id ON duels(guild_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_duels_status ON duels(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_duel_moves_duel_id ON duel_moves(duel_id)")
            
            logger.info("Database schema initialized successfully")
    
    async def get_user(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from database."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2",
                user_id, guild_id
            )
            return dict(row) if row else None
    
    async def create_user(self, user_id: int, username: str, display_name: str, guild_id: int) -> Dict[str, Any]:
        """Create a new user in the database."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO users (user_id, username, display_name, guild_id)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, guild_id) 
                DO UPDATE SET 
                    username = EXCLUDED.username,
                    display_name = EXCLUDED.display_name,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING *
            """, user_id, username, display_name, guild_id)
            return dict(row)
    
    async def update_user_stats(self, user_id: int, guild_id: int, **kwargs) -> Dict[str, Any]:
        """Update user statistics."""
        # Build dynamic update query
        set_clauses = []
        values = []
        param_count = 1
        
        for key, value in kwargs.items():
            set_clauses.append(f"{key} = ${param_count}")
            values.append(value)
            param_count += 1
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.extend([user_id, guild_id])
        
        query = f"""
            UPDATE users 
            SET {', '.join(set_clauses)}
            WHERE user_id = ${param_count} AND guild_id = ${param_count + 1}
            RETURNING *
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else None
    
    async def create_duel(self, challenger_id: int, challenged_id: int, guild_id: int) -> Dict[str, Any]:
        """Create a new duel."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO duels (challenger_id, challenged_id, guild_id)
                VALUES ($1, $2, $3)
                RETURNING *
            """, challenger_id, challenged_id, guild_id)
            return dict(row)
    
    async def get_duel(self, duel_id: int) -> Optional[Dict[str, Any]]:
        """Get duel by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM duels WHERE duel_id = $1", duel_id)
            return dict(row) if row else None
    
    async def get_pending_duel(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get pending duel for a user."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM duels 
                WHERE guild_id = $1 AND status = 'pending' 
                AND (challenger_id = $2 OR challenged_id = $2)
                ORDER BY created_at DESC
                LIMIT 1
            """, guild_id, user_id)
            return dict(row) if row else None
    
    async def update_duel(self, duel_id: int, **kwargs) -> Dict[str, Any]:
        """Update duel data."""
        set_clauses = []
        values = []
        param_count = 1
        
        for key, value in kwargs.items():
            set_clauses.append(f"{key} = ${param_count}")
            values.append(value)
            param_count += 1
        
        values.append(duel_id)
        
        query = f"""
            UPDATE duels 
            SET {', '.join(set_clauses)}
            WHERE duel_id = ${param_count}
            RETURNING *
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else None
    
    async def add_duel_move(self, duel_id: int, user_id: int, move_type: str, damage: int = 0, healing: int = 0) -> Dict[str, Any]:
        """Add a move to a duel."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO duel_moves (duel_id, user_id, move_type, damage, healing)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            """, duel_id, user_id, move_type, damage, healing)
            return dict(row)
    
    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get guild leaderboard."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, username, display_name, level, wins, losses, draws, 
                       win_streak, best_win_streak, duels_played
                FROM users 
                WHERE guild_id = $1 AND duels_played > 0
                ORDER BY wins DESC, win_streak DESC, level DESC
                LIMIT $2
            """, guild_id, limit)
            return [dict(row) for row in rows]
    
    async def get_user_stats(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed user statistics."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT u.*, 
                       COALESCE(duel_stats.duels_won, 0) as duels_won,
                       COALESCE(duel_stats.duels_lost, 0) as duels_lost,
                       COALESCE(duel_stats.duels_drawn, 0) as duels_drawn
                FROM users u
                LEFT JOIN (
                    SELECT 
                        CASE WHEN winner_id = $1 THEN challenger_id ELSE challenged_id END as user_id,
                        COUNT(CASE WHEN winner_id = $1 THEN 1 END) as duels_won,
                        COUNT(CASE WHEN winner_id != $1 AND winner_id IS NOT NULL THEN 1 END) as duels_lost,
                        COUNT(CASE WHEN winner_id IS NULL AND status = 'completed' THEN 1 END) as duels_drawn
                    FROM duels 
                    WHERE (challenger_id = $1 OR challenged_id = $1) 
                    AND guild_id = $2 
                    AND status = 'completed'
                    GROUP BY user_id
                ) duel_stats ON u.user_id = duel_stats.user_id
                WHERE u.user_id = $1 AND u.guild_id = $2
            """, user_id, guild_id)
            return dict(row) if row else None

# Global database instance
db = Database()
