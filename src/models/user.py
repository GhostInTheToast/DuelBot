"""User data models."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User model representing a Discord user in a guild."""
    user_id: int
    username: str
    display_name: Optional[str]
    guild_id: int
    level: int = 1
    experience: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    win_streak: int = 0
    best_win_streak: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    duels_played: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.duels_played == 0:
            return 0.0
        return (self.wins / self.duels_played) * 100
    
    @property
    def display_name_or_username(self) -> str:
        """Get display name or fallback to username."""
        return self.display_name or self.username
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'display_name': self.display_name,
            'guild_id': self.guild_id,
            'level': self.level,
            'experience': self.experience,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'win_streak': self.win_streak,
            'best_win_streak': self.best_win_streak,
            'total_damage_dealt': self.total_damage_dealt,
            'total_damage_taken': self.total_damage_taken,
            'duels_played': self.duels_played
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create User from dictionary."""
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            display_name=data.get('display_name'),
            guild_id=data['guild_id'],
            level=data.get('level', 1),
            experience=data.get('experience', 0),
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            draws=data.get('draws', 0),
            win_streak=data.get('win_streak', 0),
            best_win_streak=data.get('best_win_streak', 0),
            total_damage_dealt=data.get('total_damage_dealt', 0),
            total_damage_taken=data.get('total_damage_taken', 0),
            duels_played=data.get('duels_played', 0),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

@dataclass
class UserStats:
    """Extended user statistics."""
    user: User
    duels_won: int = 0
    duels_lost: int = 0
    duels_drawn: int = 0
    
    @property
    def total_duels(self) -> int:
        """Total number of duels."""
        return self.duels_won + self.duels_lost + self.duels_drawn
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_duels == 0:
            return 0.0
        return (self.duels_won / self.total_duels) * 100
