"""
Tournament Commands Cog
Provides tournament management for competitive gaming
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Optional, List
import random

class Tournament(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tournaments = {}  # {guild_id: {tournament_id: tournament_data}}
        
    @app_commands.command(name="createtournament", description="Create a new tournament")
    @app_commands.describe(
        name="Tournament name",
        game="Game being played",
        max_players="Maximum players (must be power of 2: 4, 8, 16, 32, 64)",
        description="Tournament description"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def create_tournament(
        self,
        interaction: discord.Interaction,
        name: str,
        game: str,
        max_players: int,
        description: Optional[str] = "No description provided"
    ):
        """Create a new tournament"""
        # Validate max_players is power of 2
        if max_players not in [4, 8, 16, 32, 64]:
            await interaction.response.send_message(
                "❌ Max players must be 4, 8, 16, 32, or 64!",
                ephemeral=True
            )
            return
        
        guild_id = interaction.guild.id
        
        if guild_id not in self.tournaments:
            self.tournaments[guild_id] = {}
        
        # Generate tournament ID
        tournament_id = len(self.tournaments[guild_id]) + 1
        
        # Create tournament data
        tournament = {
            'id': tournament_id,
            'name': name,
            'game': game,
            'max_players': max_players,
            'description': description,
            'host': interaction.user.id,
            'players': [],
            'status': 'registration',  # registration, active, completed
            'bracket': None,
            'created_at': datetime.utcnow()
        }
        
        self.tournaments[guild_id][tournament_id] = tournament
        
        embed = discord.Embed(
            title="🏆 Tournament Created!",
            description=f"**{name}**\n{description}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🎮 Game", value=game, inline=True)
        embed.add_field(name="👥 Max Players", value=max_players, inline=True)
        embed.add_field(name="🆔 Tournament ID", value=tournament_id, inline=True)
        embed.add_field(name="📋 Status", value="Registration Open", inline=False)
        embed.add_field(name="🎯 How to Join", value=f"Use `/jointournament {tournament_id}`", inline=False)
        
        embed.set_footer(text=f"Hosted by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="jointournament", description="Join a tournament")
    @app_commands.describe(tournament_id="Tournament ID")
    async def join_tournament(self, interaction: discord.Interaction, tournament_id: int):
        """Join an active tournament"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.tournaments or tournament_id not in self.tournaments[guild_id]:
            await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
            return
        
        tournament = self.tournaments[guild_id][tournament_id]
        
        if tournament['status'] != 'registration':
            await interaction.response.send_message("❌ Tournament registration is closed!", ephemeral=True)
            return
        
        user_id = interaction.user.id
        
        if user_id in tournament['players']:
            await interaction.response.send_message("❌ You're already registered!", ephemeral=True)
            return
        
        if len(tournament['players']) >= tournament['max_players']:
            await interaction.response.send_message("❌ Tournament is full!", ephemeral=True)
            return
        
        tournament['players'].append(user_id)
        
        embed = discord.Embed(
            title="✅ Joined Tournament!",
            description=f"**{tournament['name']}**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 Players",
            value=f"{len(tournament['players'])}/{tournament['max_players']} registered"
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Auto-start if full
        if len(tournament['players']) == tournament['max_players']:
            await interaction.channel.send(
                f"🚨 **{tournament['name']}** is now full! Starting soon..."
            )
    
    @app_commands.command(name="leavetournament", description="Leave a tournament")
    @app_commands.describe(tournament_id="Tournament ID")
    async def leave_tournament(self, interaction: discord.Interaction, tournament_id: int):
        """Leave a tournament"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.tournaments or tournament_id not in self.tournaments[guild_id]:
            await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
            return
        
        tournament = self.tournaments[guild_id][tournament_id]
        user_id = interaction.user.id
        
        if user_id not in tournament['players']:
            await interaction.response.send_message("❌ You're not in this tournament!", ephemeral=True)
            return
        
        if tournament['status'] != 'registration':
            await interaction.response.send_message("❌ Can't leave after tournament has started!", ephemeral=True)
            return
        
        tournament['players'].remove(user_id)
        
        await interaction.response.send_message("✅ Left tournament!", ephemeral=True)
    
    @app_commands.command(name="tournamentinfo", description="View tournament information")
    @app_commands.describe(tournament_id="Tournament ID")
    async def tournament_info(self, interaction: discord.Interaction, tournament_id: int):
        """Display tournament information"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.tournaments or tournament_id not in self.tournaments[guild_id]:
            await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
            return
        
        tournament = self.tournaments[guild_id][tournament_id]
        host = interaction.guild.get_member(tournament['host'])
        
        status_text = {
            'registration': '📋 Registration Open',
            'active': '🎮 In Progress',
            'completed': '✅ Completed'
        }
        
        embed = discord.Embed(
            title=f"🏆 {tournament['name']}",
            description=tournament['description'],
            color=discord.Color.gold()
        )
        
        embed.add_field(name="🎮 Game", value=tournament['game'], inline=True)
        embed.add_field(name="📊 Status", value=status_text[tournament['status']], inline=True)
        embed.add_field(name="🆔 ID", value=tournament['id'], inline=True)
        
        embed.add_field(
            name="👥 Players",
            value=f"{len(tournament['players'])}/{tournament['max_players']}",
            inline=True
        )
        
        if host:
            embed.add_field(name="🎯 Host", value=host.mention, inline=True)
        
        embed.add_field(
            name="📅 Created",
            value=f"<t:{int(tournament['created_at'].timestamp())}:R>",
            inline=True
        )
        
        # List players
        if tournament['players']:
            player_list = []
            for i, player_id in enumerate(tournament['players'][:10], 1):
                member = interaction.guild.get_member(player_id)
                if member:
                    player_list.append(f"{i}. {member.mention}")
            
            if len(tournament['players']) > 10:
                player_list.append(f"... and {len(tournament['players']) - 10} more")
            
            embed.add_field(
                name="👤 Registered Players",
                value="\n".join(player_list),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="starttournament", description="Start a tournament")
    @app_commands.describe(tournament_id="Tournament ID")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def start_tournament(self, interaction: discord.Interaction, tournament_id: int):
        """Start a tournament and generate bracket"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.tournaments or tournament_id not in self.tournaments[guild_id]:
            await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
            return
        
        tournament = self.tournaments[guild_id][tournament_id]
        
        if tournament['status'] != 'registration':
            await interaction.response.send_message("❌ Tournament already started!", ephemeral=True)
            return
        
        if len(tournament['players']) < 2:
            await interaction.response.send_message("❌ Need at least 2 players!", ephemeral=True)
            return
        
        # Generate bracket
        players = tournament['players'].copy()
        random.shuffle(players)
        
        # Pad with byes if needed
        next_power = 2
        while next_power < len(players):
            next_power *= 2
        
        while len(players) < next_power:
            players.append(None)  # Bye
        
        # Create bracket
        bracket = self._generate_bracket(players)
        tournament['bracket'] = bracket
        tournament['status'] = 'active'
        
        embed = discord.Embed(
            title=f"🏆 {tournament['name']} - STARTED!",
            description="Tournament has begun! Good luck to all players!",
            color=discord.Color.green()
        )
        
        # Show first round matchups
        embed.add_field(
            name="⚔️ Round 1 Matchups",
            value=self._format_round(bracket[0], interaction.guild),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    def _generate_bracket(self, players: List[int]) -> List[List[tuple]]:
        """Generate tournament bracket"""
        bracket = []
        current_round = [(players[i], players[i+1]) for i in range(0, len(players), 2)]
        bracket.append(current_round)
        
        # Generate subsequent rounds
        while len(current_round) > 1:
            current_round = [(None, None) for _ in range(len(current_round) // 2)]
            bracket.append(current_round)
        
        return bracket
    
    def _format_round(self, round_matchups: List[tuple], guild: discord.Guild) -> str:
        """Format round matchups for display"""
        lines = []
        for i, (p1, p2) in enumerate(round_matchups[:8], 1):  # Show max 8 matches
            member1 = guild.get_member(p1) if p1 else None
            member2 = guild.get_member(p2) if p2 else None
            
            name1 = member1.display_name if member1 else "BYE"
            name2 = member2.display_name if member2 else "BYE"
            
            lines.append(f"**Match {i}:** {name1} vs {name2}")
        
        if len(round_matchups) > 8:
            lines.append(f"... and {len(round_matchups) - 8} more matches")
        
        return "\n".join(lines)
    
    @app_commands.command(name="listtournaments", description="List all tournaments")
    async def list_tournaments(self, interaction: discord.Interaction):
        """List all tournaments in the server"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.tournaments or not self.tournaments[guild_id]:
            await interaction.response.send_message("❌ No tournaments found!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🏆 Server Tournaments",
            color=discord.Color.gold()
        )
        
        for tournament in self.tournaments[guild_id].values():
            status_emoji = {
                'registration': '📋',
                'active': '🎮',
                'completed': '✅'
            }
            
            embed.add_field(
                name=f"{status_emoji[tournament['status']]} {tournament['name']} (ID: {tournament['id']})",
                value=f"**Game:** {tournament['game']}\n**Players:** {len(tournament['players'])}/{tournament['max_players']}\n**Status:** {tournament['status'].title()}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="deletetournament", description="Delete a tournament")
    @app_commands.describe(tournament_id="Tournament ID")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def delete_tournament(self, interaction: discord.Interaction, tournament_id: int):
        """Delete a tournament"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.tournaments or tournament_id not in self.tournaments[guild_id]:
            await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
            return
        
        tournament_name = self.tournaments[guild_id][tournament_id]['name']
        del self.tournaments[guild_id][tournament_id]
        
        embed = discord.Embed(
            title="🗑️ Tournament Deleted",
            description=f"**{tournament_name}** has been deleted.",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Tournament(bot))
