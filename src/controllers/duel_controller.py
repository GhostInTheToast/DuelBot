"""Duel controller for handling duel-related commands."""
import logging

import discord
from discord.ext import commands

from models import DuelStatus, MoveType
from services import DuelService, UserService

logger = logging.getLogger(__name__)

class DuelController:
    """Controller for duel-related commands."""
    
    def __init__(self, duel_service: DuelService, user_service: UserService):
        self.duel_service = duel_service
        self.user_service = user_service
    
    async def challenge_user(self, ctx: commands.Context, target_user: discord.Member) -> discord.Embed:
        """Handle duel challenge command."""
        if target_user == ctx.author:
            return self._create_error_embed("You can't duel yourself!")
        
        if target_user.bot:
            return self._create_error_embed("You can't duel a bot!")
        
        try:
            # Ensure both users exist in database
            await self.user_service.get_or_create_user(
                ctx.author.id, ctx.author.name, ctx.author.display_name, ctx.guild.id
            )
            await self.user_service.get_or_create_user(
                target_user.id, target_user.name, target_user.display_name, ctx.guild.id
            )
            
            # Create duel
            duel = await self.duel_service.create_duel(
                ctx.author.id, target_user.id, ctx.guild.id
            )
            
            embed = discord.Embed(
                title="⚔️ Duel Challenge!",
                description=f"{ctx.author.mention} has challenged {target_user.mention} to a duel!",
                color=discord.Color.red()
            )
            embed.add_field(
                name="How to respond:",
                value="`$accept` - Accept the challenge\n`$decline` - Decline the challenge",
                inline=False
            )
            embed.add_field(
                name="Time limit:",
                value="60 seconds to respond",
                inline=False
            )
            embed.set_footer(text=f"Duel ID: {duel.duel_id}")
            
            return embed
            
        except ValueError as e:
            return self._create_error_embed(str(e))
        except Exception as e:
            logger.error(f"Error creating duel: {e}")
            return self._create_error_embed("An error occurred while creating the duel.")
    
    async def accept_duel(self, ctx: commands.Context) -> discord.Embed:
        """Handle duel acceptance command."""
        try:
            duel = await self.duel_service.accept_duel(ctx.author.id, ctx.guild.id)
            
            if not duel:
                return self._create_error_embed("You don't have any pending duels!")
            
            # Get challenger info
            challenger = ctx.guild.get_member(duel.challenger_id)
            challenger_name = challenger.display_name if challenger else "Unknown"
            
            embed = discord.Embed(
                title="⚔️ Duel Started!",
                description=f"{ctx.author.mention} accepted {challenger_name}'s challenge!",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Duel Commands:",
                value="`$attack` - Attack your opponent\n`$defend` - Defend (reduces damage)\n`$heal` - Heal yourself\n`$special` - Special attack (risky but powerful)",
                inline=False
            )
            embed.add_field(
                name="Current HP:",
                value=f"**{challenger_name}**: {duel.challenger_hp} HP\n**{ctx.author.display_name}**: {duel.challenged_hp} HP",
                inline=False
            )
            embed.set_footer(text=f"Duel ID: {duel.duel_id}")
            
            return embed
            
        except ValueError as e:
            return self._create_error_embed(str(e))
        except Exception as e:
            logger.error(f"Error accepting duel: {e}")
            return self._create_error_embed("An error occurred while accepting the duel.")
    
    async def decline_duel(self, ctx: commands.Context) -> discord.Embed:
        """Handle duel decline command."""
        try:
            success = await self.duel_service.decline_duel(ctx.author.id, ctx.guild.id)
            
            if not success:
                return self._create_error_embed("You don't have any pending duels!")
            
            embed = discord.Embed(
                title="❌ Duel Declined",
                description=f"{ctx.author.mention} declined the duel challenge.",
                color=discord.Color.orange()
            )
            
            return embed
            
        except ValueError as e:
            return self._create_error_embed(str(e))
        except Exception as e:
            logger.error(f"Error declining duel: {e}")
            return self._create_error_embed("An error occurred while declining the duel.")
    
    async def cancel_duel(self, ctx: commands.Context) -> discord.Embed:
        """Handle duel cancellation command."""
        try:
            success = await self.duel_service.cancel_duel(ctx.author.id, ctx.guild.id)
            
            if not success:
                return self._create_error_embed("You don't have any pending duels to cancel!")
            
            embed = discord.Embed(
                title="❌ Duel Cancelled",
                description=f"{ctx.author.mention} cancelled their duel challenge.",
                color=discord.Color.orange()
            )
            
            return embed
            
        except ValueError as e:
            return self._create_error_embed(str(e))
        except Exception as e:
            logger.error(f"Error cancelling duel: {e}")
            return self._create_error_embed("An error occurred while cancelling the duel.")
    
    async def make_move(self, ctx: commands.Context, move_type: MoveType) -> discord.Embed:
        """Handle duel move command."""
        try:
            duel, message = await self.duel_service.make_move(
                ctx.author.id, ctx.guild.id, move_type
            )
            
            if not duel:
                return self._create_error_embed("You don't have an active duel!")
            
            # Get opponent info
            opponent_id = duel.challenged_id if ctx.author.id == duel.challenger_id else duel.challenger_id
            opponent = ctx.guild.get_member(opponent_id)
            opponent_name = opponent.display_name if opponent else "Unknown"
            
            embed = discord.Embed(
                title="⚔️ Duel Move",
                description=f"{ctx.author.display_name} {message}",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Current HP:",
                value=f"**{ctx.author.display_name}**: {duel.get_user_hp(ctx.author.id)} HP\n**{opponent_name}**: {duel.get_user_hp(opponent_id)} HP",
                inline=False
            )
            
            # Check if duel ended
            if duel.is_completed:
                winner_id = duel.winner_id
                if winner_id:
                    winner = ctx.guild.get_member(winner_id)
                    winner_name = winner.display_name if winner else "Unknown"
                    embed.add_field(
                        name="🏆 Winner!",
                        value=f"{winner_name} wins the duel!",
                        inline=False
                    )
                    embed.color = discord.Color.gold()
                else:
                    embed.add_field(
                        name="🤝 Draw!",
                        value="The duel ended in a draw!",
                        inline=False
                    )
                    embed.color = discord.Color.grey()
            
            embed.set_footer(text=f"Duel ID: {duel.duel_id}")
            
            return embed
            
        except ValueError as e:
            return self._create_error_embed(str(e))
        except Exception as e:
            logger.error(f"Error making move: {e}")
            return self._create_error_embed("An error occurred while making the move.")
    
    async def get_duel_status(self, ctx: commands.Context) -> discord.Embed:
        """Handle duel status command."""
        try:
            duel = await self.duel_service.get_duel_status(ctx.author.id, ctx.guild.id)
            
            if not duel:
                return self._create_info_embed("No active duel", "You don't have any active or pending duels.")
            
            # Get opponent info
            opponent_id = duel.challenged_id if ctx.author.id == duel.challenger_id else duel.challenger_id
            opponent = ctx.guild.get_member(opponent_id)
            opponent_name = opponent.display_name if opponent else "Unknown"
            
            status_text = {
                DuelStatus.PENDING: "⏳ Pending",
                DuelStatus.ACTIVE: "⚔️ Active",
                DuelStatus.COMPLETED: "✅ Completed",
                DuelStatus.CANCELLED: "❌ Cancelled"
            }.get(duel.status, "Unknown")
            
            embed = discord.Embed(
                title="⚔️ Duel Status",
                description=f"**Status**: {status_text}\n**Opponent**: {opponent_name}",
                color=discord.Color.blue()
            )
            
            if duel.is_active:
                embed.add_field(
                    name="Current HP:",
                    value=f"**{ctx.author.display_name}**: {duel.get_user_hp(ctx.author.id)} HP\n**{opponent_name}**: {duel.get_user_hp(opponent_id)} HP",
                    inline=False
                )
                embed.add_field(
                    name="Available Moves:",
                    value="`$attack`, `$defend`, `$heal`, `$special`",
                    inline=False
                )
            
            embed.set_footer(text=f"Duel ID: {duel.duel_id}")
            
            return embed
            
        except Exception as e:
            logger.error(f"Error getting duel status: {e}")
            return self._create_error_embed("An error occurred while getting duel status.")
    
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
