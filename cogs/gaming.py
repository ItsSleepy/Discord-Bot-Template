import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from config import Config
import logging

logger = logging.getLogger('MegaBot.Gaming')

class Gaming(commands.Cog):
    """Gaming-related commands including Steam integration"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="steam", description="View Steam profile information")
    @app_commands.describe(username="Steam username or Steam ID (64-bit Steam ID)")
    async def steam_profile(self, interaction: discord.Interaction, username: str):
        """Display Steam profile information"""
        await interaction.response.defer()
        
        if not Config.STEAM_API_KEY:
            embed = discord.Embed(
                title=f"{Config.EMOJI_ERROR} Steam API Not Configured",
                description="Steam API key is not configured. Ask the bot owner to add it!",
                color=Config.COLOR_ERROR
            )
            await interaction.followup.send(embed=embed)
            return
        
        try:
            # Determine if input is Steam ID or vanity URL
            steam_id = username
            if not username.isdigit() or len(username) != 17:
                # Try to resolve vanity URL to Steam ID
                steam_id = await self._resolve_vanity_url(username)
                if not steam_id:
                    embed = discord.Embed(
                        title=f"{Config.EMOJI_ERROR} User Not Found",
                        description=f"Could not find Steam user: **{username}**\n\nMake sure you're using:\n• Your Steam vanity URL name\n• Your 64-bit Steam ID",
                        color=Config.COLOR_ERROR
                    )
                    await interaction.followup.send(embed=embed)
                    return
            
            # Get player summary
            player_data = await self._get_player_summary(steam_id)
            if not player_data:
                embed = discord.Embed(
                    title=f"{Config.EMOJI_ERROR} Profile Not Found",
                    description="Could not retrieve profile data. The profile might be private.",
                    color=Config.COLOR_ERROR
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get owned games
            games_data = await self._get_owned_games(steam_id)
            
            # Create embed
            embed = discord.Embed(
                title=f"🎮 {player_data.get('personaname', 'Steam User')}",
                url=player_data.get('profileurl', ''),
                color=Config.COLOR_PRIMARY
            )
            
            # Set thumbnail to avatar
            if 'avatarfull' in player_data:
                embed.set_thumbnail(url=player_data['avatarfull'])
            
            # Status
            status_map = {
                0: "🔴 Offline",
                1: "🟢 Online",
                2: "🔵 Busy",
                3: "🟡 Away",
                4: "💤 Snooze",
                5: "🔍 Looking to Trade",
                6: "🎮 Looking to Play"
            }
            status = status_map.get(player_data.get('personastate', 0), "❓ Unknown")
            embed.add_field(name="Status", value=status, inline=True)
            
            # Account creation
            if 'timecreated' in player_data:
                created = player_data['timecreated']
                embed.add_field(name="Member Since", value=f"<t:{created}:D>", inline=True)
            
            # Country
            if 'loccountrycode' in player_data:
                embed.add_field(name="Country", value=f":flag_{player_data['loccountrycode'].lower()}:", inline=True)
            
            # Games info
            if games_data:
                game_count = games_data.get('game_count', 0)
                total_playtime = sum(game.get('playtime_forever', 0) for game in games_data.get('games', []))
                total_hours = total_playtime // 60
                
                embed.add_field(name="🎮 Games Owned", value=f"{game_count:,}", inline=True)
                embed.add_field(name="⏱️ Total Playtime", value=f"{total_hours:,} hours", inline=True)
                
                # Top 5 most played games
                if games_data.get('games'):
                    top_games = sorted(games_data['games'], key=lambda x: x.get('playtime_forever', 0), reverse=True)[:5]
                    games_list = []
                    for game in top_games:
                        name = game.get('name', 'Unknown Game')
                        hours = game.get('playtime_forever', 0) // 60
                        games_list.append(f"**{name}** - {hours:,} hrs")
                    
                    if games_list:
                        embed.add_field(
                            name="🏆 Top Games",
                            value="\n".join(games_list),
                            inline=False
                        )
            else:
                embed.add_field(
                    name="🔒 Game Library",
                    value="Private or no games found",
                    inline=False
                )
            
            # Currently playing
            if 'gameextrainfo' in player_data:
                embed.add_field(
                    name="🎮 Currently Playing",
                    value=f"**{player_data['gameextrainfo']}**",
                    inline=False
                )
            
            # Profile visibility
            visibility_map = {
                1: "🔒 Private",
                3: "🌐 Public"
            }
            if 'communityvisibilitystate' in player_data:
                visibility = visibility_map.get(player_data['communityvisibilitystate'], "❓ Unknown")
                embed.set_footer(text=f"Profile: {visibility} • Steam ID: {steam_id}")
            else:
                embed.set_footer(text=f"Steam ID: {steam_id}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error fetching Steam profile: {e}", exc_info=True)
            embed = discord.Embed(
                title=f"{Config.EMOJI_ERROR} Error",
                description=f"Failed to fetch Steam profile: {str(e)}",
                color=Config.COLOR_ERROR
            )
            await interaction.followup.send(embed=embed)
    
    async def _resolve_vanity_url(self, vanity_name: str) -> str:
        """Convert vanity URL to Steam ID"""
        url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
        params = {
            'key': Config.STEAM_API_KEY,
            'vanityurl': vanity_name
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('response', {}).get('success') == 1:
                        return data['response']['steamid']
        return None
    
    async def _get_player_summary(self, steam_id: str) -> dict:
        """Get player summary from Steam API"""
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            'key': Config.STEAM_API_KEY,
            'steamids': steam_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    players = data.get('response', {}).get('players', [])
                    if players:
                        return players[0]
        return None
    
    async def _get_owned_games(self, steam_id: str) -> dict:
        """Get owned games from Steam API"""
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        params = {
            'key': Config.STEAM_API_KEY,
            'steamid': steam_id,
            'include_appinfo': 1,
            'include_played_free_games': 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('response', {})
        return None
    
    @app_commands.command(name="playing", description="See what server members are currently playing")
    async def currently_playing(self, interaction: discord.Interaction):
        """Show what games server members are playing"""
        await interaction.response.defer()
        
        # Get members currently playing games
        playing_members = []
        for member in interaction.guild.members:
            if member.bot:
                continue
            for activity in member.activities:
                if isinstance(activity, discord.Game):
                    playing_members.append((member, activity.name))
                elif isinstance(activity, discord.Activity) and activity.type == discord.ActivityType.playing:
                    playing_members.append((member, activity.name))
        
        if not playing_members:
            embed = discord.Embed(
                title=f"{Config.EMOJI_GAME} Currently Playing",
                description="No one is playing any games right now!",
                color=Config.COLOR_INFO
            )
        else:
            embed = discord.Embed(
                title=f"{Config.EMOJI_GAME} Currently Playing",
                description=f"{len(playing_members)} member(s) gaming right now!",
                color=Config.COLOR_PRIMARY
            )
            
            # Group by game
            games_dict = {}
            for member, game in playing_members:
                if game not in games_dict:
                    games_dict[game] = []
                games_dict[game].append(member.display_name)
            
            for game, players in list(games_dict.items())[:10]:  # Limit to 10 games
                players_str = ", ".join(players[:5])
                if len(players) > 5:
                    players_str += f" and {len(players) - 5} more"
                embed.add_field(name=game, value=players_str, inline=False)
        
        embed.set_footer(text="MegaBot Gaming")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="lfg", description="Looking for group - find teammates")
    @app_commands.describe(game="Game you want to play", players="Number of players needed")
    async def looking_for_group(self, interaction: discord.Interaction, game: str, players: int = 1):
        """Create a looking for group message"""
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_GAME} Looking for Group!",
            description=f"**{interaction.user.display_name}** is looking for teammates!",
            color=Config.COLOR_PRIMARY
        )
        embed.add_field(name="🎮 Game", value=game, inline=True)
        embed.add_field(name="👥 Players Needed", value=str(players), inline=True)
        embed.add_field(
            name="📞 How to Join",
            value=f"React with 🎮 to join or message {interaction.user.mention}",
            inline=False
        )
        embed.set_footer(text="MegaBot LFG System")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🎮")
    
    @app_commands.command(name="gamedeal", description="Check for game deals and discounts")
    @app_commands.describe(game="Game name to search for")
    async def game_deal(self, interaction: discord.Interaction, game: str):
        """Search for game deals"""
        await interaction.response.defer()
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_MONEY} Game Deals: {game}",
            description="Checking for the best deals...",
            color=Config.COLOR_PRIMARY
        )
        embed.add_field(
            name="💡 Feature Coming Soon",
            value="This will show:\n• Current prices\n• Discounts\n• Best deals\n• Multiple store comparison",
            inline=False
        )
        embed.set_footer(text="MegaBot Gaming Deals")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="gamerole", description="Get a gaming role")
    @app_commands.describe(game="Game role to assign")
    @app_commands.choices(game=[
        app_commands.Choice(name="CS:GO", value="csgo"),
        app_commands.Choice(name="Valorant", value="valorant"),
        app_commands.Choice(name="League of Legends", value="lol"),
        app_commands.Choice(name="Fortnite", value="fortnite"),
        app_commands.Choice(name="Minecraft", value="minecraft"),
        app_commands.Choice(name="Call of Duty", value="cod"),
        app_commands.Choice(name="Apex Legends", value="apex"),
        app_commands.Choice(name="Rocket League", value="rocketleague"),
    ])
    async def game_role(self, interaction: discord.Interaction, game: str):
        """Assign or remove a game role"""
        
        role_name = f"🎮 {game.upper()}"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        
        if not role:
            # Create role if it doesn't exist
            try:
                role = await interaction.guild.create_role(
                    name=role_name,
                    color=discord.Color.blue(),
                    mentionable=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    f"{Config.EMOJI_ERROR} I don't have permission to create roles!",
                    ephemeral=True
                )
                return
        
        # Toggle role
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                f"{Config.EMOJI_SUCCESS} Removed {role.mention} role!",
                ephemeral=True
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"{Config.EMOJI_SUCCESS} Added {role.mention} role!",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Gaming(bot))
    logger.info("Gaming cog loaded")
