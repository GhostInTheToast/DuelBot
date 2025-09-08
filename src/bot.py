"""Main bot class and setup."""
import logging

import discord
from discord.ext import commands

from .commands import setup_commands
from .config import Config
from .events import setup_events

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DuelBot:
    """Main bot class."""
    
    def __init__(self):
        """Initialize the bot with proper intents and configuration."""
        # Set up intents
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.members = True
        
        # Create bot instance
        self.bot = commands.Bot(
            command_prefix=Config.COMMAND_PREFIX,
            intents=self.intents,
            help_command=None  # We'll create a custom help command
        )
        
        # Setup events and commands
        self._setup_bot()
    
    def _setup_bot(self):
        """Setup bot events and commands."""
        setup_events(self.bot)
        setup_commands(self.bot)
    
    async def start(self):
        """Start the bot."""
        try:
            Config.validate()
            logger.info(f"Starting {Config.BOT_NAME}...")
            await self.bot.start(Config.DISCORD_BOT_TOKEN)
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        except discord.LoginFailure:
            logger.error("Invalid bot token!")
            raise
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    def run(self):
        """Run the bot (blocking)."""
        try:
            Config.validate()
            logger.info(f"Starting {Config.BOT_NAME}...")
            self.bot.run(Config.DISCORD_BOT_TOKEN)
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
        except discord.LoginFailure:
            logger.error("Invalid bot token!")
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
