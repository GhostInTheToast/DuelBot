"""Configuration management for the Discord bot."""
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration class."""
    
    # Discord Bot Configuration
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '$')
    
    # Bot Settings
    BOT_NAME = os.getenv('BOT_NAME', 'DuelBot')
    BOT_ACTIVITY = os.getenv('BOT_ACTIVITY', 'for duels')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/duelbot')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'duelbot')
    DB_USER = os.getenv('DB_USER', 'gost')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Duel Settings
    DUEL_COOLDOWN = int(os.getenv('DUEL_COOLDOWN', '300'))  # 5 minutes
    DUEL_TIMEOUT = int(os.getenv('DUEL_TIMEOUT', '60'))     # 1 minute to accept
    MAX_DUEL_DURATION = int(os.getenv('MAX_DUEL_DURATION', '300'))  # 5 minutes max
    
    # Error Handling
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.DISCORD_BOT_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN is required but not found in environment variables")
        return True
