"""Helper utility functions for DuelBot."""
import discord


def format_time(seconds: float) -> str:
    """Format time in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def calculate_level(experience: int) -> int:
    """Calculate user level based on experience."""
    # Simple level calculation: 100 exp per level
    return max(1, experience // 100 + 1)

def get_user_mention(user_id: int) -> str:
    """Get user mention string."""
    return f"<@{user_id}>"

def format_win_rate(wins: int, total: int) -> str:
    """Format win rate as percentage."""
    if total == 0:
        return "0.0%"
    return f"{(wins / total) * 100:.1f}%"

def format_damage(damage: int) -> str:
    """Format damage with appropriate emoji."""
    if damage == 0:
        return "0"
    elif damage < 10:
        return f"💢 {damage}"
    elif damage < 20:
        return f"💥 {damage}"
    else:
        return f"💀 {damage}"

def format_hp(current: int, max_hp: int = 100) -> str:
    """Format HP with visual bar."""
    percentage = (current / max_hp) * 100
    bar_length = 10
    filled_length = int((percentage / 100) * bar_length)
    
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    if percentage > 75:
        color = "🟢"
    elif percentage > 50:
        color = "🟡"
    elif percentage > 25:
        color = "🟠"
    else:
        color = "🔴"
    
    return f"{color} {bar} {current}/{max_hp}"

def get_duel_emoji(status: str) -> str:
    """Get emoji for duel status."""
    emojis = {
        "pending": "⏳",
        "active": "⚔️",
        "completed": "✅",
        "cancelled": "❌",
        "timeout": "⏰"
    }
    return emojis.get(status, "❓")

def format_duel_status(status: str) -> str:
    """Format duel status with emoji."""
    emoji = get_duel_emoji(status)
    status_text = status.replace("_", " ").title()
    return f"{emoji} {status_text}"

def is_valid_duel_target(user: discord.Member, author: discord.Member) -> tuple[bool, str]:
    """Validate if a user can be challenged to a duel."""
    if user == author:
        return False, "You can't duel yourself!"
    
    if user.bot:
        return False, "You can't duel a bot!"
    
    # Only prevent dueling if the user is actually offline
    # Allow online, idle, dnd (busy), and do_not_disturb statuses
    if user.status == discord.Status.offline:
        return False, "You can't duel someone who is offline!"
    
    return True, ""

def get_move_emoji(move_type: str) -> str:
    """Get emoji for move type."""
    emojis = {
        "attack": "⚔️",
        "defend": "🛡️",
        "heal": "💚",
        "special": "✨"
    }
    return emojis.get(move_type, "❓")

def format_move_description(move_type: str, damage: int = 0, healing: int = 0) -> str:
    """Format move description with emojis and effects."""
    emoji = get_move_emoji(move_type)
    
    if move_type == "attack":
        return f"{emoji} Attacks for {damage} damage!"
    elif move_type == "defend":
        return f"{emoji} Defends, reducing incoming damage!"
    elif move_type == "heal":
        return f"{emoji} Heals for {healing} HP!"
    elif move_type == "special":
        if damage > 0:
            return f"{emoji} Special attack hits for {damage} damage!"
        else:
            return f"{emoji} Special attack misses!"
    
    return f"{emoji} Unknown move!"

def calculate_experience_gain(duel_result: str, user_level: int, opponent_level: int) -> int:
    """Calculate experience gain from a duel."""
    base_exp = 10
    
    # Level difference bonus/penalty
    level_diff = opponent_level - user_level
    level_bonus = level_diff * 2
    
    # Result bonus
    if duel_result == "win":
        result_bonus = 5
    elif duel_result == "draw":
        result_bonus = 2
    else:  # loss
        result_bonus = 1
    
    total_exp = base_exp + level_bonus + result_bonus
    return max(1, total_exp)  # Minimum 1 exp
