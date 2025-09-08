"""Validation utility functions for DuelBot."""
from typing import Optional, Tuple

import discord

from models import MoveType


def validate_duel_target(target: discord.Member, challenger: discord.Member) -> Tuple[bool, Optional[str]]:
    """Validate if a user can be challenged to a duel."""
    if target == challenger:
        return False, "You can't duel yourself!"
    
    if target.bot:
        return False, "You can't duel a bot!"
    
    # Only prevent dueling if the user is actually offline
    # Allow online, idle, dnd (busy), and do_not_disturb statuses
    if target.status == discord.Status.offline:
        return False, "You can't duel someone who is offline!"
    
    return True, None

def validate_move_type(move_str: str) -> Tuple[bool, Optional[MoveType]]:
    """Validate and convert move type string to enum."""
    move_str = move_str.lower().strip()
    
    move_mapping = {
        "attack": MoveType.ATTACK,
        "defend": MoveType.DEFEND,
        "heal": MoveType.HEAL,
        "special": MoveType.SPECIAL
    }
    
    if move_str in move_mapping:
        return True, move_mapping[move_str]
    
    return False, None

def validate_user_permissions(user: discord.Member, required_permissions: list = None) -> Tuple[bool, Optional[str]]:
    """Validate if user has required permissions."""
    if required_permissions is None:
        required_permissions = []
    
    missing_permissions = []
    for permission in required_permissions:
        if not getattr(user.guild_permissions, permission, False):
            missing_permissions.append(permission)
    
    if missing_permissions:
        return False, f"Missing permissions: {', '.join(missing_permissions)}"
    
    return True, None

def validate_duel_acceptance(duel, user_id: int) -> Tuple[bool, Optional[str]]:
    """Validate if a user can accept a duel."""
    if not duel:
        return False, "No pending duel found!"
    
    if duel.challenged_id != user_id:
        return False, "You can only accept duels you were challenged to!"
    
    if duel.status.value != "pending":
        return False, "This duel is no longer pending!"
    
    return True, None

def validate_duel_cancellation(duel, user_id: int) -> Tuple[bool, Optional[str]]:
    """Validate if a user can cancel a duel."""
    if not duel:
        return False, "No pending duel found!"
    
    if duel.challenger_id != user_id:
        return False, "You can only cancel duels you started!"
    
    if duel.status.value != "pending":
        return False, "This duel is no longer pending!"
    
    return True, None

def validate_move_execution(duel, user_id: int) -> Tuple[bool, Optional[str]]:
    """Validate if a user can make a move in a duel."""
    if not duel:
        return False, "No active duel found!"
    
    if user_id not in [duel.challenger_id, duel.challenged_id]:
        return False, "You're not part of this duel!"
    
    if duel.status.value != "active":
        return False, "This duel is not active!"
    
    return True, None

def validate_leaderboard_limit(limit: int) -> Tuple[bool, Optional[str]]:
    """Validate leaderboard limit parameter."""
    if limit < 1:
        return False, "Limit must be at least 1!"
    
    if limit > 50:
        return False, "Limit cannot exceed 50!"
    
    return True, None

def validate_experience_amount(amount: int) -> Tuple[bool, Optional[str]]:
    """Validate experience amount."""
    if amount < 0:
        return False, "Experience amount cannot be negative!"
    
    if amount > 1000:
        return False, "Experience amount cannot exceed 1000!"
    
    return True, None
