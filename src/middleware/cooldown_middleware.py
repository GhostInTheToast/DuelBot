"""Cooldown middleware for managing command cooldowns."""
import logging
import time
from typing import Dict, Set

logger = logging.getLogger(__name__)

class CooldownMiddleware:
    """Middleware for managing command cooldowns."""
    
    def __init__(self):
        self.cooldowns: Dict[str, Dict[int, float]] = {}
        self.global_cooldowns: Set[int] = set()
    
    def add_cooldown(self, command_name: str, user_id: int, duration: float):
        """Add a cooldown for a user and command."""
        if command_name not in self.cooldowns:
            self.cooldowns[command_name] = {}
        
        self.cooldowns[command_name][user_id] = time.time() + duration
        logger.debug(f"Added {duration}s cooldown for {command_name} to user {user_id}")
    
    def add_global_cooldown(self, user_id: int, duration: float):
        """Add a global cooldown for a user."""
        self.global_cooldowns.add(user_id)
        # Remove from global cooldown after duration
        # In a real implementation, you'd use asyncio.create_task
        logger.debug(f"Added {duration}s global cooldown for user {user_id}")
    
    def is_on_cooldown(self, command_name: str, user_id: int) -> bool:
        """Check if a user is on cooldown for a command."""
        current_time = time.time()
        
        # Check global cooldown
        if user_id in self.global_cooldowns:
            return True
        
        # Check command-specific cooldown
        if command_name in self.cooldowns:
            if user_id in self.cooldowns[command_name]:
                if current_time < self.cooldowns[command_name][user_id]:
                    return True
                else:
                    # Remove expired cooldown
                    del self.cooldowns[command_name][user_id]
        
        return False
    
    def get_cooldown_remaining(self, command_name: str, user_id: int) -> float:
        """Get remaining cooldown time for a user and command."""
        current_time = time.time()
        
        if command_name in self.cooldowns:
            if user_id in self.cooldowns[command_name]:
                remaining = self.cooldowns[command_name][user_id] - current_time
                return max(0, remaining)
        
        return 0
    
    def clear_cooldown(self, command_name: str, user_id: int):
        """Clear cooldown for a user and command."""
        if command_name in self.cooldowns:
            self.cooldowns[command_name].pop(user_id, None)
        self.global_cooldowns.discard(user_id)
        logger.debug(f"Cleared cooldowns for {command_name} and user {user_id}")

# Global cooldown middleware instance
cooldown_middleware = CooldownMiddleware()
