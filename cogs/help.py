"""
Help Commands Cog
Provides help and setup commands for the bot
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="help", description="Display all available commands")
    @app_commands.describe(category="Choose a specific category to view")
    @app_commands.choices(category=[
        app_commands.Choice(name="🎮 Gaming", value="gaming"),
        app_commands.Choice(name="🏆 Tournament", value="tournament"),
        app_commands.Choice(name="💰 Economy", value="economy"),
        app_commands.Choice(name="🔧 Utility", value="utility"),
        app_commands.Choice(name="📚 Study", value="study"),
        app_commands.Choice(name="🛡️ Moderation", value="moderation"),
        app_commands.Choice(name="🎉 Fun", value="fun"),
        app_commands.Choice(name="📊 Stats", value="stats"),
    ])
    async def help_command(self, interaction: discord.Interaction, category: Optional[str] = None):
        """Display help information for bot commands"""
        
        if category is None:
            # Main help menu
            embed = discord.Embed(
                title="🤖 MegaBot Help Menu",
                description="Welcome to MegaBot! Here are all available command categories.\nUse `/help category:<name>` to see commands in a specific category.",
                color=discord.Color.blue()
            )
            
            categories = {
                "🎮 Gaming": "LFG system, game roles, gaming profiles",
                "🏆 Tournament": "Tournament management and brackets",
                "💰 Economy": "Virtual currency, shop, gambling, trading",
                "🔧 Utility": "Polls, reminders, calculator, server info",
                "📚 Study": "Study timer, notes, flashcards, resources",
                "🛡️ Moderation": "Kick, ban, mute, warnings, logging",
                "🎉 Fun": "Jokes, memes, 8ball, trivia, games",
                "📊 Stats": "Server stats, user stats, leaderboards"
            }
            
            for cat_name, description in categories.items():
                embed.add_field(
                    name=cat_name,
                    value=description,
                    inline=False
                )
            
            embed.add_field(
                name="💡 Quick Start",
                value="Try `/balance` to start your economy journey!\nUse `/setup` to configure the bot for your server.\nUse `/dashboard` to access the web dashboard!",
                inline=False
            )
            
            embed.set_footer(text=f"Total Commands: 66 | Requested by {interaction.user.display_name}")
            
        else:
            # Category-specific help
            commands_dict = {
                "gaming": {
                    "title": "🎮 Gaming Commands",
                    "commands": [
                        "/playing - Set what game you're playing",
                        "/lfg - Create a looking-for-group post",
                        "/gamedeal - Search for game deals",
                        "/gamerole - Get a role for a specific game",
                        "/currentgames - See who's playing what"
                    ]
                },
                "tournament": {
                    "title": "🏆 Tournament Commands",
                    "commands": [
                        "/createtournament - Create a new tournament",
                        "/jointournament - Join a tournament",
                        "/tournamentbracket - View tournament bracket",
                        "/reportmatch - Report a match result",
                        "/tournamentinfo - View tournament details",
                        "/tournaments - List all active tournaments"
                    ]
                },
                "economy": {
                    "title": "💰 Economy Commands",
                    "commands": [
                        "/balance - Check your balance",
                        "/daily - Claim daily reward",
                        "/work - Work to earn money",
                        "/rob - Rob another user (risky!)",
                        "/give - Give money to another user",
                        "/shop - View the shop",
                        "/buy - Buy an item from shop",
                        "/inventory - View your inventory",
                        "/sell - Sell an item",
                        "/slots - Play slots machine",
                        "/coinflip - Flip a coin for money",
                        "/blackjack - Play blackjack",
                        "/leaderboard - View economy leaderboard"
                    ]
                },
                "utility": {
                    "title": "🔧 Utility Commands",
                    "commands": [
                        "/poll - Create a poll",
                        "/remind - Set a reminder",
                        "/translate - Translate text",
                        "/calculate - Calculate math expressions",
                        "/userinfo - Get info about a user",
                        "/serverinfo - Get server information",
                        "/avatar - View user's avatar",
                        "/timestamp - Generate Discord timestamps",
                        "/color - View color information"
                    ]
                },
                "study": {
                    "title": "📚 Study Commands",
                    "commands": [
                        "/studytimer - Start a study timer",
                        "/note - Create a study note",
                        "/mynotes - View your notes",
                        "/flashcard - Create a flashcard",
                        "/quiz - Take a quiz from flashcards",
                        "/studygroup - Create a study group",
                        "/resource - Share a study resource",
                        "/studystats - View your study statistics"
                    ]
                },
                "moderation": {
                    "title": "🛡️ Moderation Commands",
                    "commands": [
                        "/kick - Kick a member",
                        "/ban - Ban a member",
                        "/unban - Unban a member",
                        "/mute - Mute a member",
                        "/unmute - Unmute a member",
                        "/warn - Warn a member",
                        "/warnings - View warnings for a user",
                        "/clear - Clear messages",
                        "/slowmode - Set slowmode",
                        "/lock - Lock a channel",
                        "/unlock - Unlock a channel",
                        "/modlogs - View moderation logs"
                    ]
                },
                "fun": {
                    "title": "🎉 Fun Commands",
                    "commands": [
                        "/joke - Get a random joke",
                        "/meme - Get a random meme",
                        "/8ball - Ask the magic 8ball",
                        "/trivia - Play trivia game",
                        "/wouldyourather - Would you rather game",
                        "/roll - Roll dice",
                        "/flip - Flip a coin",
                        "/rps - Rock paper scissors",
                        "/rate - Rate something out of 10",
                        "/choose - Choose between options"
                    ]
                },
                "stats": {
                    "title": "📊 Stats Commands",
                    "commands": [
                        "/stats - View your stats",
                        "/serverstats - View server statistics",
                        "/topusers - View most active users",
                        "/activity - View server activity graph",
                        "/usergrowth - View user growth statistics",
                        "/commandstats - View command usage stats"
                    ]
                }
            }
            
            if category in commands_dict:
                cat_data = commands_dict[category]
                embed = discord.Embed(
                    title=cat_data["title"],
                    description=f"Here are all commands in the {category} category:",
                    color=discord.Color.green()
                )
                
                for cmd in cat_data["commands"]:
                    embed.add_field(
                        name=cmd.split(" - ")[0],
                        value=cmd.split(" - ")[1] if " - " in cmd else "No description",
                        inline=False
                    )
                
                embed.set_footer(text=f"Use /help to see all categories | Requested by {interaction.user.display_name}")
            else:
                embed = discord.Embed(
                    title="❌ Invalid Category",
                    description="Please select a valid category from the dropdown!",
                    color=discord.Color.red()
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setup", description="Setup the bot for your server")
    @app_commands.default_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        """Setup wizard for the bot"""
        
        embed = discord.Embed(
            title="🔧 MegaBot Setup Wizard",
            description="Welcome to MegaBot setup! Follow these steps to configure the bot:",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="1️⃣ Create Channels",
            value="Create these optional channels:\n"
                  "• `#mod-logs` - For moderation logs\n"
                  "• `#welcome` - For welcome messages\n"
                  "• `#economy` - For economy commands\n"
                  "• `#gaming` - For LFG posts",
            inline=False
        )
        
        embed.add_field(
            name="2️⃣ Set Permissions",
            value="Make sure the bot has these permissions:\n"
                  "✅ Manage Messages\n"
                  "✅ Manage Roles\n"
                  "✅ Kick Members\n"
                  "✅ Ban Members\n"
                  "✅ Send Messages\n"
                  "✅ Embed Links",
            inline=False
        )
        
        embed.add_field(
            name="3️⃣ Configure Moderation",
            value="Use these commands to set up moderation:\n"
                  "• `/slowmode` - Set channel slowmode\n"
                  "• `/lock` - Lock channels when needed",
            inline=False
        )
        
        embed.add_field(
            name="4️⃣ Economy Setup",
            value="The economy system is ready to use!\n"
                  "Users can start with `/balance` and `/daily`",
            inline=False
        )
        
        embed.add_field(
            name="5️⃣ Test Commands",
            value="Try these commands to test:\n"
                  "• `/help` - View all commands\n"
                  "• `/serverinfo` - View server info\n"
                  "• `/poll` - Create a test poll",
            inline=False
        )
        
        embed.add_field(
            name="✅ You're All Set!",
            value="Your bot is now configured! Use `/help` to see all available commands.\n"
                  "Need help? Check the documentation or contact support.",
            inline=False
        )
        
        embed.set_footer(text=f"Setup by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="info", description="Get information about the bot")
    async def info(self, interaction: discord.Interaction):
        """Display bot information"""
        
        embed = discord.Embed(
            title="ℹ️ About MegaBot",
            description="A comprehensive Discord bot with economy, gaming, sports, utility tools, and more!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"Servers: {len(self.bot.guilds)}\n"
                  f"Users: {sum(g.member_count for g in self.bot.guilds)}\n"
                  f"Commands: 66",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Features",
            value="• 💰 Economy System\n"
                  "• 🎮 Gaming Integration\n"
                  "• ⚽ Sports Betting\n"
                  "• 📚 Study Tools\n"
                  "• 🛡️ Moderation Tools",
            inline=True
        )
        
        embed.add_field(
            name="🔗 Links",
            value="[Discord Developer Portal](https://discord.com/developers/applications/)",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"MegaBot v1.0 | Requested by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dashboard", description="Get the link to the web dashboard")
    async def dashboard(self, interaction: discord.Interaction):
        """Provides link to the web dashboard"""
        
        embed = discord.Embed(
            title="🌐 MegaBot Web Dashboard",
            description="Access the interactive web dashboard to explore all bot features, commands, and statistics!",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="📊 Dashboard Features",
            value="• 📋 Complete command list with details\n"
                  "• 📈 Real-time bot statistics\n"
                  "• 🎮 Feature overview and categories\n"
                  "• 📱 Responsive mobile-friendly design\n"
                  "• 🔍 Interactive command explorer",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Access Dashboard",
            value="**[Click here to open dashboard](https://megabotdiscord.netlify.app/)**",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tip",
            value="Bookmark the dashboard for quick access to command documentation and bot stats!",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        # Create a button for easy access
        view = discord.ui.View()
        button = discord.ui.Button(
            label="Open Dashboard",
            style=discord.ButtonStyle.link,
            url="https://megabotdiscord.netlify.app/",
            emoji="🌐"
        )
        view.add_item(button)
        
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))
