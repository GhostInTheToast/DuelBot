"""Duel data models."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DuelStatus(Enum):
    """Duel status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class MoveType(Enum):
    """Duel move types."""
    ATTACK = "attack"
    DEFEND = "defend"
    HEAL = "heal"
    SPECIAL = "special"

@dataclass
class Duel:
    """Duel model representing a duel between two users."""
    duel_id: int
    challenger_id: int
    challenged_id: int
    guild_id: int
    status: DuelStatus
    winner_id: Optional[int] = None
    challenger_hp: int = 100
    challenged_hp: int = 100
    challenger_attack: int = 10
    challenged_attack: int = 10
    challenger_defense: int = 5
    challenged_defense: int = 5
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    @property
    def is_active(self) -> bool:
        """Check if duel is currently active."""
        return self.status == DuelStatus.ACTIVE
    
    @property
    def is_pending(self) -> bool:
        """Check if duel is pending acceptance."""
        return self.status == DuelStatus.PENDING
    
    @property
    def is_completed(self) -> bool:
        """Check if duel is completed."""
        return self.status == DuelStatus.COMPLETED
    
    def get_user_hp(self, user_id: int) -> int:
        """Get HP for a specific user."""
        if user_id == self.challenger_id:
            return self.challenger_hp
        elif user_id == self.challenged_id:
            return self.challenged_hp
        return 0
    
    def get_user_attack(self, user_id: int) -> int:
        """Get attack power for a specific user."""
        if user_id == self.challenger_id:
            return self.challenger_attack
        elif user_id == self.challenged_id:
            return self.challenged_attack
        return 0
    
    def get_user_defense(self, user_id: int) -> int:
        """Get defense for a specific user."""
        if user_id == self.challenger_id:
            return self.challenger_defense
        elif user_id == self.challenged_id:
            return self.challenged_defense
        return 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'duel_id': self.duel_id,
            'challenger_id': self.challenger_id,
            'challenged_id': self.challenged_id,
            'guild_id': self.guild_id,
            'status': self.status.value,
            'winner_id': self.winner_id,
            'challenger_hp': self.challenger_hp,
            'challenged_hp': self.challenged_hp,
            'challenger_attack': self.challenger_attack,
            'challenged_attack': self.challenged_attack,
            'challenger_defense': self.challenger_defense,
            'challenged_defense': self.challenged_defense,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'ended_at': self.ended_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Duel':
        """Create Duel from dictionary."""
        return cls(
            duel_id=data['duel_id'],
            challenger_id=data['challenger_id'],
            challenged_id=data['challenged_id'],
            guild_id=data['guild_id'],
            status=DuelStatus(data['status']),
            winner_id=data.get('winner_id'),
            challenger_hp=data.get('challenger_hp', 100),
            challenged_hp=data.get('challenged_hp', 100),
            challenger_attack=data.get('challenger_attack', 10),
            challenged_attack=data.get('challenged_attack', 10),
            challenger_defense=data.get('challenger_defense', 5),
            challenged_defense=data.get('challenged_defense', 5),
            created_at=data.get('created_at'),
            started_at=data.get('started_at'),
            ended_at=data.get('ended_at')
        )

@dataclass
class DuelMove:
    """Duel move model representing a move made during a duel."""
    move_id: int
    duel_id: int
    user_id: int
    move_type: MoveType
    damage: int = 0
    healing: int = 0
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'move_id': self.move_id,
            'duel_id': self.duel_id,
            'user_id': self.user_id,
            'move_type': self.move_type.value,
            'damage': self.damage,
            'healing': self.healing,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DuelMove':
        """Create DuelMove from dictionary."""
        return cls(
            move_id=data['move_id'],
            duel_id=data['duel_id'],
            user_id=data['user_id'],
            move_type=MoveType(data['move_type']),
            damage=data.get('damage', 0),
            healing=data.get('healing', 0),
            created_at=data.get('created_at')
        )
