"""User controller for handling user-related commands."""
import logging
from typing import Optional

import discord
from discord.ext import commands

from services import UserService

logger = logging.getLogger(__name__)

class UserController:
    """Controller for user-related commands."""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    async def get_profile(self, ctx: commands.Context, target_user: Optional[discord.Member] = None) -> discord.Embed:
        """Handle profile command."""
        user = target_user or ctx.author
        
        try:
            # Ensure user exists in database
            await self.user_service.get_or_create_user(
                user.id, user.name, user.display_name, ctx.guild.id
            )
            
            stats = await self.user_service.get_user_profile(user.id, ctx.guild.id)
            
            if not stats:
                return self._create_error_embed("User profile not found!")
            
            embed = discord.Embed(
                title=f"👤 {stats.user.display_name_or_username}'s Profile",
                color=discord.Color.blue()
            )
            
            # Basic stats
            embed.add_field(
                name="📊 Statistics",
                value=f"**Level**: {stats.user.level}\n**Experience**: {stats.user.experience}\n**Duels Played**: {stats.user.duels_played}",
                inline=True
            )
            
            # Combat stats
            embed.add_field(
                name="⚔️ Combat Record",
                value=f"**Wins**: {stats.user.wins}\n**Losses**: {stats.user.losses}\n**Draws**: {stats.user.draws}",
                inline=True
            )
            
            # Performance stats
            win_rate = stats.win_rate
            embed.add_field(
                name="📈 Performance",
                value=f"**Win Rate**: {win_rate:.1f}%\n**Current Streak**: {stats.user.win_streak}\n**Best Streak**: {stats.user.best_win_streak}",
                inline=True
            )
            
            # Damage stats
            embed.add_field(
                name="💥 Damage",
                value=f"**Dealt**: {stats.user.total_damage_dealt}\n**Taken**: {stats.user.total_damage_taken}",
                inline=True
            )
            
            embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
            embed.set_footer(text=f"User ID: {user.id}")
            
            return embed
            
        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return self._create_error_embed("An error occurred while getting the profile.")
    
    async def get_leaderboard(self, ctx: commands.Context, limit: int = 10) -> discord.Embed:
        """Handle leaderboard command."""
        try:
            users = await self.user_service.get_leaderboard(ctx.guild.id, limit)
            
            if not users:
                return self._create_info_embed("Leaderboard", "No users found on the leaderboard.")
            
            embed = discord.Embed(
                title="🏆 Guild Leaderboard",
                description=f"Top {len(users)} duelers in {ctx.guild.name}",
                color=discord.Color.gold()
            )
            
            leaderboard_text = ""
            for i, user in enumerate(users, 1):
                win_rate = user.win_rate
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                
                leaderboard_text += f"{medal} **{user.display_name_or_username}**\n"
                leaderboard_text += f"   Level {user.level} | {user.wins}W-{user.losses}L ({win_rate:.1f}%)\n"
                leaderboard_text += f"   Streak: {user.win_streak} | Best: {user.best_win_streak}\n\n"
            
            embed.add_field(
                name="Rankings",
                value=leaderboard_text,
                inline=False
            )
            
            embed.set_footer(text=f"Showing top {len(users)} players")
            
            return embed
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return self._create_error_embed("An error occurred while getting the leaderboard.")
    
    async def get_stats(self, ctx: commands.Context) -> discord.Embed:
        """Handle stats command (shorthand for profile)."""
        return await self.get_profile(ctx)
    
    def _create_error_embed(self, message: str) -> discord.Embed:
        """Create an error embed."""
        return discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.red()
        )
    
    def _create_info_embed(self, title: str, message: str) -> discord.Embed:
        """Create an info embed."""
        return discord.Embed(
            title=title,
            description=message,
            color=discord.Color.blue()
        )
