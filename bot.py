import discord
from discord.ext import commands
import asyncio
import logging
import sys
import os
from datetime import datetime
from config import Config
from api.bot_api import BotAPI
from database import Database

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('MegaBot')

class MegaBot(commands.Bot):
    """Main bot class with all features integrated"""
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None  # We'll create custom help
        )
        
        self.start_time = datetime.now()
        self.config = Config
        self.db = Database()  # Initialize database
        
    async def setup_hook(self):
        """Load all cogs when bot starts"""
        # Connect to database first
        logger.info("Connecting to database...")
        await self.db.connect()
        
        logger.info("Loading cogs...")
        
        # List of all cog modules
        cogs = [
            'cogs.help',
            'cogs.gaming',
            'cogs.tournament',
            'cogs.economy',
            'cogs.utility',
            'cogs.study',
            'cogs.moderation',
            'cogs.fun',
            'cogs.stats'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"[OK] Loaded {cog}")
            except Exception as e:
                logger.error(f"[ERROR] Failed to load {cog}: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"[OK] Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"[ERROR] Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"BOT ONLINE: {self.user.name}")
        logger.info(f"Connected to {len(self.guilds)} server(s)")
        logger.info(f"Serving {sum(g.member_count for g in self.guilds)} users")
        
        # Start API server for website stats
        api = BotAPI(self)
        api.run()
        logger.info("API server started on http://localhost:5000")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="your server | /help"
            ),
            status=discord.Status.online
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{Config.EMOJI_ERROR} You don't have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{Config.EMOJI_ERROR} Missing required argument: {error.param}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{Config.EMOJI_WARNING} Command on cooldown. Try again in {error.retry_after:.1f}s")
        else:
            logger.error(f"Error in command {ctx.command}: {error}")
            await ctx.send(f"{Config.EMOJI_ERROR} An error occurred. Please try again later.")
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new server"""
        logger.info(f"📥 Joined new server: {guild.name} (ID: {guild.id})")
        
        # Send welcome message to first available channel
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="👋 Thanks for adding MegaBot!",
                    description="I'm an all-in-one bot with gaming, sports, economy, study tools, and more!",
                    color=Config.COLOR_PRIMARY
                )
                embed.add_field(
                    name="🚀 Get Started",
                    value="Use `/help` to see all available commands!",
                    inline=False
                )
                embed.add_field(
                    name="⚙️ Setup",
                    value="Use `/setup` to configure the bot for your server",
                    inline=False
                )
                embed.set_footer(text="MegaBot - Your Ultimate Server Assistant")
                await channel.send(embed=embed)
                break
    
    async def on_member_join(self, member):
        """Called when a member joins the server"""
        # This will be handled by moderation cog
        pass
    
    async def on_message(self, message):
        """Called when a message is sent"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Process commands
        await self.process_commands(message)

def main():
    """Main function to run the bot"""
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        logger.error("❌ .env file not found!")
        logger.info("📝 Please create a .env file based on .env.example")
        logger.info("💡 Add your Discord bot token to the .env file")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Create bot instance
    bot = MegaBot()
    
    try:
        logger.info("Starting MegaBot...")
        bot.run(Config.DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("[ERROR] Invalid Discord token!")
        logger.info("Please check your DISCORD_TOKEN in the .env file")
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested...")
    except Exception as e:
        logger.error(f"[ERROR] Failed to start bot: {e}")
    finally:
        # Close database connection on shutdown
        import asyncio
        asyncio.run(bot.db.close())

if __name__ == "__main__":
    main()
