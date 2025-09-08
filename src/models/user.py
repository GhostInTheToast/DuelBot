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
    duels_today: int = 0
    last_duel_date: Optional[datetime] = None
    is_outlaw: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        total_duels = self.wins + self.losses + self.draws
        if total_duels == 0:
            return 0.0
        return (self.wins / total_duels) * 100
    
    @property
    def display_name_or_username(self) -> str:
        """Get display name or fallback to username."""
        return self.display_name or self.username
    
    def calculate_xp_gain(self, won: bool, damage_dealt: int, opponent_level: int, is_first_duel_today: bool = False, opponent_is_outlaw: bool = False) -> int:
        """Calculate XP gain for a duel with anti-farming measures."""
        
        # Base XP (much lower)
        base_xp = 10 if won else 5
        
        # Quality bonuses (reduced)
        damage_bonus = min(damage_dealt // 20, 10)  # Max 10 bonus for high damage (1 XP per 20 damage)
        streak_bonus = min(self.win_streak, 5) if won else 0  # Win streak bonus (max 5)
        
        # First duel of the day bonus (reduced)
        first_duel_bonus = 5 if is_first_duel_today else 0
        
        # Damage dealt bonus (much lower)
        damage_xp_bonus = damage_dealt // 10  # 1 XP per 10 damage dealt
        
        # Level difference multiplier
        level_diff = opponent_level - self.level
        if level_diff > 0:
            # Fighting higher level opponent - 2x XP multiplier
            level_multiplier = 2.0
        elif level_diff < 0:
            # Fighting lower level opponent - 0.5x XP multiplier
            level_multiplier = 0.5
        else:
            # Same level - normal XP
            level_multiplier = 1.0
        
        # Outlaw bounty multiplier (2x XP for defeating an outlaw)
        outlaw_multiplier = 2.0 if opponent_is_outlaw else 1.0
        
        # Diminishing returns based on duels today
        diminishing_factor = 1.0
        if self.duels_today >= 10:
            diminishing_factor = 0.1  # 90% reduction after 10 duels
        elif self.duels_today >= 5:
            diminishing_factor = 0.5  # 50% reduction after 5 duels
        elif self.duels_today >= 3:
            diminishing_factor = 0.8  # 20% reduction after 3 duels
        
        # Calculate total XP with all multipliers
        total_xp = int((base_xp + damage_bonus + streak_bonus + first_duel_bonus + damage_xp_bonus) * level_multiplier * outlaw_multiplier * diminishing_factor)
        
        return max(1, total_xp)  # Minimum 1 XP
    
    def get_xp_for_next_level(self) -> int:
        """Get XP required for next level using grindy formula."""
        if self.level >= 99:
            return 0  # Max level reached
        
        # Much more grindy formula: XP required = level^3 * 10 + level * 100
        next_level = self.level + 1
        return int((next_level ** 3) * 10) + (next_level * 100)
    
    def get_xp_progress(self) -> tuple[int, int, int]:
        """Get XP progress for current level (current, required, percentage)."""
        if self.level >= 99:
            return 0, 0, 100  # Max level reached
        
        # Calculate XP required for current level (level 1 starts at 0 XP)
        if self.level == 1:
            current_level_xp_required = 0
        else:
            current_level_xp_required = int(((self.level - 1) ** 3) * 10) + ((self.level - 1) * 100)
        
        # Calculate XP required for next level
        next_level_xp_required = self.get_xp_for_next_level()
        
        # Current level XP is the difference between total XP and current level requirement
        current_level_xp = max(0, self.experience - current_level_xp_required)
        required_xp = next_level_xp_required - current_level_xp_required
        
        percentage = int((current_level_xp / required_xp) * 100) if required_xp > 0 else 100
        
        return current_level_xp, required_xp, percentage
    
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
            'duels_played': self.duels_played,
            'duels_today': self.duels_today,
            'last_duel_date': self.last_duel_date,
            'is_outlaw': self.is_outlaw
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
            duels_today=data.get('duels_today', 0),
            last_duel_date=data.get('last_duel_date'),
            is_outlaw=data.get('is_outlaw', False),
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
