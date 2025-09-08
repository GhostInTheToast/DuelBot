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
            import asyncio
            import random

            # Ensure both users exist in database
            await self.user_service.get_or_create_user(
                ctx.author.id, ctx.author.name, ctx.author.display_name, ctx.guild.id
            )
            await self.user_service.get_or_create_user(
                target.id, target.name, target.display_name, ctx.guild.id
            )
            
            # Start the dramatic duel
            await ctx.send(f"⚔️ **{ctx.author.display_name}** challenges **{target.display_name}** to a duel!")
            await asyncio.sleep(2)
            
            await ctx.send("🎲 The dice are rolling...")
            await asyncio.sleep(2)
            
            await ctx.send("⚡ The tension builds...")
            await asyncio.sleep(2)
            
            await ctx.send("🔥 **FIGHT!**")
            await asyncio.sleep(1)
            
            # Get user objects for level information
            challenger_user = await self.user_service.get_or_create_user(
                ctx.author.id, ctx.author.name, ctx.author.display_name, ctx.guild.id
            )
            target_user = await self.user_service.get_or_create_user(
                target.id, target.name, target.display_name, ctx.guild.id
            )
            
            # Both start with 250 HP
            challenger_hp = 250
            target_hp = 250
            round_num = 1
            total_challenger_damage = 0
            total_target_damage = 0
            
            # Create initial duel embed
            duel_embed = discord.Embed(
                title="⚔️ Duel in Progress",
                color=discord.Color.red()
            )
            duel_embed.add_field(
                name="Fighters",
                value=f"**{ctx.author.display_name}** (Lv.{challenger_user.level}) vs **{target.display_name}** (Lv.{target_user.level})",
                inline=False
            )
            duel_embed.add_field(
                name="Status",
                value="🎲 Rolling dice...",
                inline=False
            )
            
            # Send initial embed
            duel_message = await ctx.send(embed=duel_embed)
            
            # Fight until someone dies
            while challenger_hp > 0 and target_hp > 0:
                # Roll dice (0-100) + level bonus - this is damage dealt this round
                challenger_base_damage = random.randint(0, 100)
                target_base_damage = random.randint(0, 100)
                
                # Add level bonus (1 damage per level)
                challenger_damage = challenger_base_damage + challenger_user.level
                target_damage = target_base_damage + target_user.level
                
                # Deal damage
                challenger_hp -= target_damage
                target_hp -= challenger_damage
                
                # Ensure HP doesn't go below 0
                challenger_hp = max(0, challenger_hp)
                target_hp = max(0, target_hp)
                
                # Add to total damage
                total_challenger_damage += challenger_damage
                total_target_damage += target_damage
                
                # Update embed with round results
                duel_embed.clear_fields()
                duel_embed.add_field(
                    name="Fighters",
                    value=f"**{ctx.author.display_name}** (Lv.{challenger_user.level}) vs **{target.display_name}** (Lv.{target_user.level})",
                    inline=False
                )
                
                # Round results
                round_text = f"**Round {round_num}:**\n"
                round_text += f"🎲 **{ctx.author.display_name}** deals **{challenger_damage}** damage! ({challenger_base_damage} + {challenger_user.level} level bonus)\n"
                round_text += f"🎲 **{target.display_name}** deals **{target_damage}** damage! ({target_base_damage} + {target_user.level} level bonus)"
                
                duel_embed.add_field(
                    name="Round Results",
                    value=round_text,
                    inline=False
                )
                
                # HP status
                hp_text = f"**{ctx.author.display_name}**: {challenger_hp} HP\n"
                hp_text += f"**{target.display_name}**: {target_hp} HP"
                
                duel_embed.add_field(
                    name="Health Status",
                    value=hp_text,
                    inline=False
                )
                
                # Update the message
                await duel_message.edit(embed=duel_embed)
                
                # Check if fight is over
                if challenger_hp <= 0 or target_hp <= 0:
                    break
                
                round_num += 1
                await asyncio.sleep(2)  # 2 second delay between rounds
            
            # Determine winner
            if challenger_hp <= 0 and target_hp <= 0:
                # Both died - draw
                await self.user_service.update_user_after_duel(ctx.author.id, ctx.guild.id, False, total_challenger_damage, total_target_damage, target_user.level, target_user.is_outlaw)
                await self.user_service.update_user_after_duel(target.id, ctx.guild.id, False, total_target_damage, total_challenger_damage, challenger_user.level, challenger_user.is_outlaw)
                
                # Update embed for draw result
                duel_embed.clear_fields()
                duel_embed.title = "💀 MUTUAL DESTRUCTION!"
                duel_embed.color = discord.Color.dark_gray()
                
                duel_embed.add_field(
                    name="Final Results",
                    value=f"**{ctx.author.display_name}** dealt **{total_challenger_damage}** total damage (HP: 0)\n**{target.display_name}** dealt **{total_target_damage}** total damage (HP: 0)",
                    inline=False
                )
                duel_embed.add_field(
                    name="Outcome",
                    value="*It's a mutual destruction!*",
                    inline=False
                )
                
                await duel_message.edit(embed=duel_embed)
                return
            elif challenger_hp <= 0:
                # Challenger died
                winner = target
                winner_user = target_user
                loser = ctx.author
                loser_user = challenger_user
                winner_total_damage = total_target_damage
                loser_total_damage = total_challenger_damage
                winner_hp = target_hp
                loser_hp = 0
            else:
                # Target died
                winner = ctx.author
                winner_user = challenger_user
                loser = target
                loser_user = target_user
                winner_total_damage = total_challenger_damage
                loser_total_damage = total_target_damage
                winner_hp = challenger_hp
                loser_hp = 0
            
            # Update stats with XP and leveling
            winner_result = await self.user_service.update_user_after_duel(winner.id, ctx.guild.id, True, winner_total_damage, loser_total_damage, loser_user.level, loser_user.is_outlaw)
            loser_result = await self.user_service.update_user_after_duel(loser.id, ctx.guild.id, False, loser_total_damage, winner_total_damage, winner_user.level, winner_user.is_outlaw)
            
            # Update embed with final result
            winner_title = f"🏆 {winner.display_name} WINS!"
            if winner_result and winner_result.get('is_outlaw'):
                winner_title += " 🏴‍☠️ OUTLAW!"
            
            duel_embed.clear_fields()
            duel_embed.title = winner_title
            duel_embed.color = discord.Color.gold()
            
            # Final results
            duel_embed.add_field(
                name="Final Results",
                value=f"**{winner.display_name}** dealt **{winner_total_damage}** total damage (HP: {winner_hp})\n**{loser.display_name}** dealt **{loser_total_damage}** total damage (HP: {loser_hp})",
                inline=False
            )
            
            duel_embed.add_field(
                name="Outcome",
                value=f"💀 **{loser.display_name}** has been defeated in {round_num} rounds!",
                inline=False
            )
            
            # Add XP and level up information
            if winner_result and loser_result:
                # Calculate level differences for display
                winner_level_diff = loser_user.level - winner_user.level
                loser_level_diff = winner_user.level - loser_user.level
                
                winner_level_text = ""
                if winner_level_diff > 0:
                    winner_level_text = f" 🏆 **+{winner_level_diff} level advantage!**"
                elif winner_level_diff < 0:
                    winner_level_text = f" ⚠️ **-{abs(winner_level_diff)} level disadvantage**"
                else:
                    winner_level_text = " (same level)"
                
                # Add outlaw bounty info for winner
                if winner_result.get('is_outlaw'):
                    winner_level_text += " 🏴‍☠️ **OUTLAW!**"
                
                loser_level_text = ""
                if loser_level_diff > 0:
                    loser_level_text = f" 🏆 **+{loser_level_diff} level advantage!**"
                elif loser_level_diff < 0:
                    loser_level_text = f" ⚠️ **-{abs(loser_level_diff)} level disadvantage**"
                else:
                    loser_level_text = " (same level)"
                
                # Add outlaw bounty info for loser
                if loser_result.get('is_outlaw'):
                    loser_level_text += " 🏴‍☠️ **OUTLAW!**"
                
                xp_text = f"**{winner.display_name}**: +{winner_result['xp_gained']} XP{winner_level_text}"
                if winner_result['level_up']:
                    xp_text += f" 🎉 **LEVEL UP!** (Level {winner_result['new_level']})"
                xp_text += f" (dealt {winner_total_damage} damage)\n"
                
                xp_text += f"**{loser.display_name}**: +{loser_result['xp_gained']} XP{loser_level_text}"
                if loser_result['level_up']:
                    xp_text += f" 🎉 **LEVEL UP!** (Level {loser_result['new_level']})"
                xp_text += f" (dealt {loser_total_damage} damage)"
                
                duel_embed.add_field(
                    name="📈 Experience Gained",
                    value=xp_text,
                    inline=False
                )
                
                # Show daily duel count
                duel_embed.add_field(
                    name="📅 Daily Activity",
                    value=f"**Duels Today**: {winner_result['duels_today']} / {loser_result['duels_today']}",
                    inline=False
                )
            
            await duel_message.edit(embed=duel_embed)
            
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
    
    @commands.command(name='outlaws', help='View current outlaws (5+ win streak)')
    async def outlaws(self, ctx):
        """View current outlaws in the guild."""
        try:
            # Get all users and filter for outlaws
            users = await self.user_service.get_leaderboard(ctx.guild.id, 50)  # Get more users to find outlaws
            outlaws = [user for user in users if user.is_outlaw]
            
            if not outlaws:
                embed = discord.Embed(
                    title="🏴‍☠️ Outlaws",
                    description="No outlaws currently in the guild. Win 5+ duels in a row to become an outlaw!",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏴‍☠️ Current Outlaws",
                description="These players have 5+ win streaks and are worth 2x XP when defeated!",
                color=discord.Color.red()
            )
            
            outlaw_text = ""
            for i, outlaw in enumerate(outlaws, 1):
                outlaw_text += f"**{i}.** {outlaw.display_name_or_username} (Level {outlaw.level})\n"
                outlaw_text += f"   Win Streak: {outlaw.win_streak} | Best: {outlaw.best_win_streak}\n"
                outlaw_text += "   Worth: **2x XP** when defeated! 🎯\n\n"
            
            embed.add_field(
                name="Wanted List",
                value=outlaw_text,
                inline=False
            )
            
            embed.set_footer(text="Defeat an outlaw to claim the bounty!")
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in outlaws command: {e}")
            await ctx.send("❌ An error occurred while getting outlaw information.")
    
    @commands.command(name='levels', help='View level requirements table')
    async def levels(self, ctx):
        """View level requirements table."""
        embed = discord.Embed(
            title="📊 Level Requirements (RuneScape Formula)",
            description="XP required for each level",
            color=discord.Color.blue()
        )
        
        # Show key levels
        key_levels = [1, 5, 10, 25, 50, 75, 90, 95, 98, 99]
        level_text = ""
        
        for level in key_levels:
            if level == 1:
                xp_required = 0
            else:
                xp_required = int((level ** 3) * 10) + (level * 100)
            
            if level == 99:
                level_text += f"**Level {level}**: {xp_required:,} XP 🏆 **MAX LEVEL**\n"
            else:
                level_text += f"**Level {level}**: {xp_required:,} XP\n"
        
        embed.add_field(
            name="Key Levels",
            value=level_text,
            inline=False
        )
        
        embed.add_field(
            name="Formula",
            value="`XP = (Level³ × 10) + (Level × 100)`",
            inline=False
        )
        
        embed.set_footer(text="Use $level to see your personal progress")
        await ctx.send(embed=embed)
    
    @commands.command(name='level', help='View detailed leveling information')
    async def level(self, ctx, target: discord.Member = None):
        """View detailed leveling information."""
        user = target or ctx.author
        
        try:
            # Ensure user exists in database
            await self.user_service.get_or_create_user(
                user.id, user.name, user.display_name, ctx.guild.id
            )
            
            stats = await self.user_service.get_user_profile(user.id, ctx.guild.id)
            if not stats:
                await ctx.send("❌ User profile not found!")
                return
            
            current_xp, required_xp, xp_percentage = stats.user.get_xp_progress()
            
            # Create title with level and percentage
            title_text = f"📈 {stats.user.display_name_or_username}'s Level Progress"
            if stats.user.level < 99:
                title_text += f" - Level {stats.user.level} ({xp_percentage}% to {stats.user.level + 1})"
            else:
                title_text += f" - Level {stats.user.level} 🏆 MAX LEVEL!"
            
            embed = discord.Embed(
                title=title_text,
                color=discord.Color.gold()
            )
            
            # Level and XP info
            level_text = f"**Level {stats.user.level}**"
            if stats.user.level >= 99:
                level_text += " 🏆 **MAX LEVEL!**"
            embed.add_field(
                name="🎯 Current Level",
                value=f"{level_text}\n**Total Experience**: {stats.user.experience:,}",
                inline=True
            )
            
            # Progress bar
            if stats.user.level >= 99:
                embed.add_field(
                    name="📊 Progress to Next Level",
                    value="🏆 **MAX LEVEL REACHED!**\nYou've achieved the highest level possible!",
                    inline=False
                )
            else:
                progress_bar = "█" * (xp_percentage // 5) + "░" * (20 - (xp_percentage // 5))
                embed.add_field(
                    name="📊 Progress to Next Level",
                    value=f"```{progress_bar}```\n**{current_xp}/{required_xp}** XP ({xp_percentage}%)\n**{required_xp - current_xp}** XP needed",
                    inline=False
                )
            
            # Daily stats
            embed.add_field(
                name="📅 Daily Activity",
                value=f"**Duels Today**: {stats.user.duels_today}\n**Last Duel**: {stats.user.last_duel_date.strftime('%Y-%m-%d %H:%M') if stats.user.last_duel_date else 'Never'}",
                inline=True
            )
            
            # XP sources
            embed.add_field(
                name="💡 XP Sources",
                value="""• **Win**: 10 XP base
• **Loss**: 5 XP base
• **Damage Bonus**: +1 XP per 20 damage (max 10)
• **Damage XP**: +1 XP per 10 damage dealt
• **Streak Bonus**: +1 XP per win streak (max 5)
• **First Duel**: +5 XP bonus

**Level Multipliers:**
• **Higher Level Opponent**: 2x XP 🏆
• **Same Level**: 1x XP
• **Lower Level Opponent**: 0.5x XP ⚠️

**Outlaw Bounty:**
• **Defeating Outlaw**: 2x XP 🏴‍☠️
• **Becoming Outlaw**: 5+ win streak
• **Outlaw Status**: Resets on loss

**Grindy Formula**: Level 99 = 9,702,100 XP total""",
                inline=False
            )
            
            # Anti-farming info
            diminishing_info = ""
            if stats.user.duels_today >= 10:
                diminishing_info = "⚠️ **90% XP reduction** (10+ duels today)"
            elif stats.user.duels_today >= 5:
                diminishing_info = "⚠️ **50% XP reduction** (5+ duels today)"
            elif stats.user.duels_today >= 3:
                diminishing_info = "⚠️ **20% XP reduction** (3+ duels today)"
            else:
                diminishing_info = "✅ **Full XP** (Normal rate)"
            
            embed.add_field(
                name="🛡️ Anti-Farming Status",
                value=diminishing_info,
                inline=False
            )
            
            embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
            embed.set_footer(text=f"User ID: {user.id}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in level command: {e}")
            await ctx.send("❌ An error occurred while getting level information.")
    
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
                value="""`$duel @user` - Challenge a user to a multi-round HP duel (250 HP, 0-100 + level damage per round)""",
                inline=False
            )
            
            # User Commands
            embed.add_field(
                name="👤 User Commands",
                value="""`$profile [@user]` - View your or another user's profile
`$stats [@user]` - View stats (alias for profile)
`$level [@user]` - View detailed leveling information
`$levels` - View level requirements table
`$outlaws` - View current outlaws (5+ win streak)
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
2. Watch the dramatic buildup and fight begins
3. Multiple rounds of dice rolling (0-100 damage each)
4. First to lose all 250 HP dies!
5. Check your stats with `$profile`""",
                inline=False
            )
            
            # Tips
            embed.add_field(
                name="💡 Tips",
                value="""• No cooldown - duel as much as you want!
• Roll 0-100 + level bonus damage per round
• Higher level = more damage dealt!
• Fight higher levels for 2x XP! 🏆
• Fighting lower levels gives 0.5x XP ⚠️
• Both start with 250 HP
• Level up to deal more damage!""",
                inline=False
            )
            
            embed.set_footer(text="Use $help <command> for detailed information about a specific command")
            await ctx.send(embed=embed)
        
        except discord.Forbidden:
            # Fallback to plain text if embeds are not allowed
            help_text = """**⚔️ DuelBot Commands Help**

**🎯 Duel Commands:**
`$duel @user` - Challenge a user to a multi-round HP duel (250 HP, 0-100 + level damage per round)

**👤 User Commands:**
`$profile [@user]` - View your or another user's profile
`$stats [@user]` - View stats (alias for profile)
`$level [@user]` - View detailed leveling information
`$levels` - View level requirements table
`$leaderboard [limit]` - View the guild leaderboard

**🔧 Basic Commands:**
`$ping` - Check bot latency
`$hello` - Say hello to the bot
`$info` - Get bot information
`$help` - Show general help

**🎮 How to Duel:**
1. Use `$duel @user` to challenge someone
2. Watch the dramatic buildup and fight begins
3. Multiple rounds of dice rolling (0-100 + level damage each)
4. First to lose all 250 HP dies!
5. Check your stats with `$profile`

**💡 Tips:**
• No cooldown - duel as much as you want!
• Roll 0-100 + level bonus damage per round
• Higher level = more damage dealt!
• Both start with 250 HP
• Multiple rounds until someone dies
• Level up to deal more damage!

Use `$help <command>` for detailed information about a specific command"""
            
            await ctx.send(help_text)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(DuelCommands(bot))
