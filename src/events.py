"""Event handlers for the Discord bot."""
import logging

import discord
from discord.ext import commands

from config import Config

logger = logging.getLogger(__name__)

def setup_events(bot):
    """Setup all bot event handlers."""
    
    @bot.event
    async def on_ready():
        """Event triggered when bot is ready and connected to Discord."""
        logger.info(f'{bot.user} has connected to Discord!')
        logger.info(f'Bot is in {len(bot.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=Config.BOT_ACTIVITY
        )
        await bot.change_presence(activity=activity)
    
    @bot.event
    async def on_guild_join(guild):
        """Event triggered when bot joins a new guild."""
        logger.info(f'Joined new guild: {guild.name} (ID: {guild.id})')
    
    @bot.event
    async def on_guild_remove(guild):
        """Event triggered when bot leaves a guild."""
        logger.info(f'Left guild: {guild.name} (ID: {guild.id})')
    
    @bot.event
    async def on_message(message):
        """Event triggered when a message is sent in a channel the bot can see."""
        # Ignore messages from the bot itself
        if message.author == bot.user:
            return
        
        # Process commands
        await bot.process_commands(message)
    
    @bot.event
    async def on_command_error(ctx, error):
        """Event triggered when a command raises an error."""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        logger.error(f'Error in command {ctx.command}: {error}')
        
        # Send user-friendly error message
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument provided.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permission to execute this command.")
        else:
            await ctx.send(f"An error occurred: {error}")
    
    @bot.event
    async def on_command_completion(ctx):
        """Event triggered when a command completes successfully."""
        logger.info(f"Command '{ctx.command}' used by {ctx.author} in {ctx.guild}")
