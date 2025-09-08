"""Duel commands for DuelBot."""
import logging

import discord
from discord.ext import commands

from controllers import DuelController, UserController
from services import DatabaseService, DuelService, UserService
from utils import validate_duel_target

logger = logging.getLogger(__name__)

class DuelCommands(commands.Cog):
    """Duel-related commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_service = DatabaseService()
        self.user_service = UserService(self.db_service)
        self.duel_service = DuelService(self.db_service)
        self.duel_controller = DuelController(self.duel_service, self.user_service)
        self.user_controller = UserController(self.user_service)
    
    async def cog_load(self):
        """Initialize services when cog loads."""
        await self.db_service.initialize()
    
    async def cog_unload(self):
        """Cleanup when cog unloads."""
        await self.db_service.close()
    
    @commands.command(name='duel', help='Challenge a user to a duel')
    async def duel(self, ctx, target: discord.Member):
        """Challenge a user to a duel."""
        # Validate target
        is_valid, error_msg = validate_duel_target(target, ctx.author)
        if not is_valid:
            await ctx.send(f"❌ {error_msg}")
            return
        
        
        try:
            # Create instant duel - 50/50 RNG
            import random

            # Ensure both users exist in database
            await self.user_service.get_or_create_user(
                ctx.author.id, ctx.author.name, ctx.author.display_name, ctx.guild.id
            )
            await self.user_service.get_or_create_user(
                target.id, target.name, target.display_name, ctx.guild.id
            )
            
            # 50/50 coin flip
            winner = ctx.author if random.random() < 0.5 else target
            loser = target if winner == ctx.author else ctx.author
            
            # Update stats
            await self.user_service.update_user_after_duel(winner.id, ctx.guild.id, True, 0, 0)
            await self.user_service.update_user_after_duel(loser.id, ctx.guild.id, False, 0, 0)
            
            # Send result
            result_text = "⚔️ **Duel Result**\n\n"
            result_text += f"**{ctx.author.display_name}** vs **{target.display_name}**\n\n"
            result_text += f"🏆 **Winner: {winner.display_name}**\n"
            result_text += f"💀 **Loser: {loser.display_name}**\n\n"
            result_text += "*It was a 50/50 coin flip!*"
            
            await ctx.send(result_text)
            
        except Exception as e:
            logger.error(f"Error in duel command: {e}")
            await ctx.send("❌ An error occurred while creating the duel.")
    
    
    @commands.command(name='profile', help='View your or another user\'s profile')
    async def profile(self, ctx, target: discord.Member = None):
        """View your or another user's profile."""
        try:
            embed = await self.user_controller.get_profile(ctx, target)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in profile command: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while getting the profile.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='stats', help='View your stats (alias for profile)')
    async def stats(self, ctx):
        """View your stats (alias for profile)."""
        await self.profile(ctx)
    
    @commands.command(name='leaderboard', help='View the guild leaderboard')
    async def leaderboard(self, ctx, limit: int = 10):
        """View the guild leaderboard."""
        if limit < 1 or limit > 50:
            embed = discord.Embed(
                title="❌ Invalid Limit",
                description="Limit must be between 1 and 50.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            embed = await self.user_controller.get_leaderboard(ctx, limit)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in leaderboard command: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while getting the leaderboard.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='debugstatus', help='Debug user status (admin only)')
    async def debug_status(self, ctx, target: discord.Member):
        """Debug user status for troubleshooting."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ This command is for administrators only.")
            return
        
        status_info = f"""
**User Status Debug:**
**User**: {target.display_name}
**Status**: {target.status}
**Status Value**: {target.status.value}
**Is Online**: {target.status != discord.Status.offline}
**Can Duel**: {target.status != discord.Status.offline and not target.bot and target != ctx.author}
"""
        await ctx.send(status_info)
    
    @commands.command(name='teststats', help='Test stats saving (admin only)')
    async def test_stats(self, ctx):
        """Test if stats are being saved properly."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ This command is for administrators only.")
            return
        
        try:
            # Get current stats
            stats = await self.user_service.get_user_profile(ctx.author.id, ctx.guild.id)
            if stats:
                await ctx.send(f"**Current Stats:**\nWins: {stats.user.wins}\nLosses: {stats.user.losses}\nDuels: {stats.user.duels_played}")
            else:
                await ctx.send("❌ No stats found for this user.")
        except Exception as e:
            await ctx.send(f"❌ Error getting stats: {e}")
    
    @commands.command(name='duelhelp', help='Show help for duel commands')
    async def duel_help(self, ctx):
        """Show comprehensive help for duel commands."""
        try:
            embed = discord.Embed(
                title="⚔️ DuelBot Commands Help",
                description="Here are all available commands for the duel system:",
                color=discord.Color.blue()
            )
            
            # Duel Commands
            embed.add_field(
                name="🎯 Duel Commands",
                value="""`$duel @user` - Challenge a user to an instant 50/50 duel""",
                inline=False
            )
            
            # User Commands
            embed.add_field(
                name="👤 User Commands",
                value="""`$profile [@user]` - View your or another user's profile
`$stats [@user]` - View stats (alias for profile)
`$leaderboard [limit]` - View the guild leaderboard""",
                inline=False
            )
            
            # Basic Commands
            embed.add_field(
                name="🔧 Basic Commands",
                value="""`$ping` - Check bot latency
`$hello` - Say hello to the bot
`$info` - Get bot information
`$help` - Show general help""",
                inline=False
            )
            
            # How to Duel
            embed.add_field(
                name="🎮 How to Duel",
                value="""1. Use `$duel @user` to challenge someone
2. The duel happens instantly with a 50/50 coin flip
3. Winner gets a win, loser gets a loss
4. Check your stats with `$profile`""",
                inline=False
            )
            
            # Tips
            embed.add_field(
                name="💡 Tips",
                value="""• No cooldown - duel as much as you want!
• It's pure 50/50 luck - no skill involved!
• Check your stats with `$profile`
• View the leaderboard with `$leaderboard`
• You can't duel yourself or bots""",
                inline=False
            )
            
            embed.set_footer(text="Use $help <command> for detailed information about a specific command")
            await ctx.send(embed=embed)
        
        except discord.Forbidden:
            # Fallback to plain text if embeds are not allowed
            help_text = """**⚔️ DuelBot Commands Help**

**🎯 Duel Commands:**
`$duel @user` - Challenge a user to an instant 50/50 duel

**👤 User Commands:**
`$profile [@user]` - View your or another user's profile
`$stats [@user]` - View stats (alias for profile)
`$leaderboard [limit]` - View the guild leaderboard

**🔧 Basic Commands:**
`$ping` - Check bot latency
`$hello` - Say hello to the bot
`$info` - Get bot information
`$help` - Show general help

**🎮 How to Duel:**
1. Use `$duel @user` to challenge someone
2. They can `$accept` or `$decline` your challenge
3. Once accepted, use combat commands to fight
4. First to 0 HP loses, or it's a draw if both reach 0

**💡 Tips:**
• Each duel has a 5-minute cooldown
• You can only have one pending duel at a time
• Use `$defend` to reduce incoming damage
• `$special` is risky but powerful
• Check `$duelstatus` to see your current duel

Use `$help <command>` for detailed information about a specific command"""
            
            await ctx.send(help_text)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(DuelCommands(bot))
