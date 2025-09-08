"""Configuration management for the Discord bot."""
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration class."""
    
    # Discord Bot Configuration
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    
    # Bot Settings
    BOT_NAME = os.getenv('BOT_NAME', 'DuelBot')
    BOT_ACTIVITY = os.getenv('BOT_ACTIVITY', 'for commands')
    
    # Error Handling
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.DISCORD_BOT_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN is required but not found in environment variables")
        return True
