"""Commands package for the Discord bot."""
from .admin import setup_admin_commands
from .basic import setup_basic_commands


def setup_commands(bot):
    """Setup all bot commands."""
    setup_basic_commands(bot)
    setup_admin_commands(bot)
