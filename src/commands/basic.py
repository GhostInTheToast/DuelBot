"""Basic commands for the Discord bot."""
import logging

import discord

logger = logging.getLogger(__name__)

def setup_basic_commands(bot):
    """Setup basic bot commands."""
    
    @bot.command(name='ping', help='Check bot latency')
    async def ping(ctx):
        """Simple ping command to check bot responsiveness."""
        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: {latency}ms",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @bot.command(name='hello', help='Say hello to the bot')
    async def hello(ctx):
        """Simple hello command."""
        embed = discord.Embed(
            title="👋 Hello!",
            description=f"Hello {ctx.author.mention}! Nice to meet you!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @bot.command(name='info', help='Get bot information')
    async def info(ctx):
        """Display bot information."""
        embed = discord.Embed(
            title="🤖 Bot Information",
            description="A Discord bot built with discord.py",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
        embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
        embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Commands", value=len(bot.commands), inline=True)
        embed.add_field(name="Uptime", value="Online", inline=True)
        
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=embed)
    
    @bot.command(name='help', help='Show this help message')
    async def help_command(ctx, command_name: str = None):
        """Custom help command."""
        if command_name:
            # Show help for specific command
            command = bot.get_command(command_name)
            if not command:
                await ctx.send(f"Command '{command_name}' not found.")
                return
            
            embed = discord.Embed(
                title=f"Help: {command.name}",
                description=command.help or "No description available",
                color=discord.Color.blue()
            )
            
            if command.aliases:
                embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
            
            await ctx.send(embed=embed)
        else:
            # Show general help
            embed = discord.Embed(
                title="🤖 Bot Commands",
                description="Here are all available commands:",
                color=discord.Color.blue()
            )
            
            # Group commands by category
            basic_commands = [cmd for cmd in bot.commands if not hasattr(cmd, 'category') or cmd.category is None]
            
            if basic_commands:
                command_list = []
                for cmd in basic_commands:
                    command_list.append(f"`{cmd.name}` - {cmd.help or 'No description'}")
            embed.add_field(
                name="Basic Commands",
                value="\n".join(command_list),
                inline=False
            )
            
            # Add duel help reference
            embed.add_field(
                name="⚔️ Duel System",
                value="Use `$duelhelp` for comprehensive duel commands and gameplay guide!",
                inline=False
            )
            
            embed.set_footer(text="Use !help <command> for detailed information about a specific command")
            await ctx.send(embed=embed)
    
    # Error handlers for basic commands
    @ping.error
    async def ping_error(ctx, error):
        """Error handler for ping command."""
        logger.error(f"Error in ping command: {error}")
        await ctx.send("An error occurred while checking ping!")
    
    @hello.error
    async def hello_error(ctx, error):
        """Error handler for hello command."""
        logger.error(f"Error in hello command: {error}")
        await ctx.send("An error occurred while saying hello!")
    
    @info.error
    async def info_error(ctx, error):
        """Error handler for info command."""
        logger.error(f"Error in info command: {error}")
        await ctx.send("An error occurred while getting bot info!")
