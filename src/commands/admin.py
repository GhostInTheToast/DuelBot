"""Admin commands for the Discord bot."""
import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

def setup_admin_commands(bot):
    """Setup admin bot commands."""
    
    @bot.command(name='shutdown', help='Shutdown the bot (owner only)')
    @commands.is_owner()
    async def shutdown(ctx):
        """Shutdown the bot (owner only)."""
        embed = discord.Embed(
            title="🔌 Shutting Down",
            description="Bot is shutting down...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        logger.info("Bot shutdown requested by owner")
        await bot.close()
    
    @bot.command(name='reload', help='Reload a command (owner only)')
    @commands.is_owner()
    async def reload(ctx, *, module: str):
        """Reload a command module (owner only)."""
        try:
            bot.reload_extension(f'src.commands.{module}')
            embed = discord.Embed(
                title="🔄 Reloaded",
                description=f"Successfully reloaded {module}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            logger.info(f"Reloaded module: {module}")
        except Exception as e:
            embed = discord.Embed(
                title="❌ Reload Failed",
                description=f"Failed to reload {module}: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.error(f"Failed to reload {module}: {e}")
    
    @bot.command(name='guilds', help='List all guilds the bot is in (owner only)')
    @commands.is_owner()
    async def guilds(ctx):
        """List all guilds the bot is in (owner only)."""
        if not bot.guilds:
            await ctx.send("Bot is not in any guilds.")
            return
        
        embed = discord.Embed(
            title="🏰 Guilds",
            description=f"Bot is in {len(bot.guilds)} guilds:",
            color=discord.Color.blue()
        )
        
        guild_list = []
        for guild in bot.guilds:
            guild_list.append(f"**{guild.name}** (ID: {guild.id}) - {guild.member_count} members")
        
        # Split into chunks if too long
        if len('\n'.join(guild_list)) > 2000:
            chunks = [guild_list[i:i+10] for i in range(0, len(guild_list), 10)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    embed.add_field(name="Guilds", value='\n'.join(chunk), inline=False)
                else:
                    embed.add_field(name=f"Guilds (continued {i+1})", value='\n'.join(chunk), inline=False)
        else:
            embed.add_field(name="Guilds", value='\n'.join(guild_list), inline=False)
        
        await ctx.send(embed=embed)
    
    @bot.command(name='status', help='Set bot status (owner only)')
    @commands.is_owner()
    async def status(ctx, activity_type: str, *, status_text: str):
        """Set bot status (owner only)."""
        activity_types = {
            'playing': discord.ActivityType.playing,
            'watching': discord.ActivityType.watching,
            'listening': discord.ActivityType.listening,
            'streaming': discord.ActivityType.streaming
        }
        
        if activity_type.lower() not in activity_types:
            await ctx.send(f"Invalid activity type. Use: {', '.join(activity_types.keys())}")
            return
        
        activity = discord.Activity(
            type=activity_types[activity_type.lower()],
            name=status_text
        )
        
        await bot.change_presence(activity=activity)
        
        embed = discord.Embed(
            title="✅ Status Updated",
            description=f"Bot status changed to {activity_type} {status_text}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        logger.info(f"Bot status changed to {activity_type} {status_text}")
    
    # Error handlers for admin commands
    @shutdown.error
    async def shutdown_error(ctx, error):
        """Error handler for shutdown command."""
        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ This command can only be used by the bot owner.")
        else:
            logger.error(f"Error in shutdown command: {error}")
            await ctx.send("An error occurred while shutting down!")
    
    @reload.error
    async def reload_error(ctx, error):
        """Error handler for reload command."""
        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ This command can only be used by the bot owner.")
        else:
            logger.error(f"Error in reload command: {error}")
            await ctx.send("An error occurred while reloading!")
    
    @guilds.error
    async def guilds_error(ctx, error):
        """Error handler for guilds command."""
        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ This command can only be used by the bot owner.")
        else:
            logger.error(f"Error in guilds command: {error}")
            await ctx.send("An error occurred while getting guild list!")
    
    @status.error
    async def status_error(ctx, error):
        """Error handler for status command."""
        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ This command can only be used by the bot owner.")
        else:
            logger.error(f"Error in status command: {error}")
            await ctx.send("An error occurred while updating status!")
