"""Error handling middleware for DuelBot."""
import logging
import traceback

from discord import Embed
from discord.ext import commands

logger = logging.getLogger(__name__)

class ErrorMiddleware:
    """Middleware for handling errors and providing user-friendly messages."""
    
    @staticmethod
    async def handle_command_error(ctx: commands.Context, error: commands.CommandError):
        """Handle command errors with user-friendly messages."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = Embed(
                title="❌ Missing Argument",
                description=f"Missing required argument: `{error.param.name}`",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.BadArgument):
            embed = Embed(
                title="❌ Invalid Argument",
                description="Invalid argument provided. Please check your input.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            embed = Embed(
                title="⏰ Command on Cooldown",
                description=f"Please wait {error.retry_after:.1f} seconds before using this command again.",
                color=0xffa500
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.MissingPermissions):
            embed = Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to use this command.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            embed = Embed(
                title="❌ Bot Missing Permissions",
                description="I don't have permission to execute this command.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.NotOwner):
            embed = Embed(
                title="❌ Owner Only",
                description="This command can only be used by the bot owner.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Log unexpected errors
        logger.error(f"Unexpected error in command {ctx.command}: {error}")
        logger.error(traceback.format_exc())
        
        # Send generic error message
        embed = Embed(
            title="❌ An Error Occurred",
            description="An unexpected error occurred. Please try again later.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @staticmethod
    async def handle_general_error(error: Exception, context: str = ""):
        """Handle general errors with logging."""
        logger.error(f"Error in {context}: {error}")
        logger.error(traceback.format_exc())
