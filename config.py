import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration class"""
    
    # Discord Settings
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '/')
    
    # API Keys
    STEAM_API_KEY = os.getenv('STEAM_API_KEY', '')  # Pending approval
    # OPENWEATHER_API_KEY removed - weather feature not needed
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    FORMULA1_API_KEY = os.getenv('FORMULA1_API_KEY', '')
    SPORTS_API_KEY = os.getenv('SPORTS_API_KEY', '')
    
    # Bot Settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False') == 'True'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/database.db')
    
    # Economy Settings
    STARTING_BALANCE = int(os.getenv('STARTING_BALANCE', 1000))
    DAILY_REWARD = int(os.getenv('DAILY_REWARD', 100))
    WORK_REWARD_MIN = int(os.getenv('WORK_REWARD_MIN', 50))
    WORK_REWARD_MAX = int(os.getenv('WORK_REWARD_MAX', 200))
    
    # Study Settings
    DEFAULT_STUDY_DURATION = int(os.getenv('DEFAULT_STUDY_DURATION', 25))
    DEFAULT_BREAK_DURATION = int(os.getenv('DEFAULT_BREAK_DURATION', 5))
    
    # Server Settings
    DEFAULT_WELCOME_CHANNEL = os.getenv('DEFAULT_WELCOME_CHANNEL', 'general')
    AUTO_ROLE_ENABLED = os.getenv('AUTO_ROLE_ENABLED', 'False') == 'True'
    
    # Color Scheme for Embeds
    COLOR_PRIMARY = 0x00D9FF  # Cyan
    COLOR_SUCCESS = 0x00FF00  # Green
    COLOR_ERROR = 0xFF0000    # Red
    COLOR_WARNING = 0xFFAA00  # Orange
    COLOR_INFO = 0x5865F2     # Discord Blurple
    
    # Emojis
    EMOJI_SUCCESS = '✅'
    EMOJI_ERROR = '❌'
    EMOJI_WARNING = '⚠️'
    EMOJI_LOADING = '⏳'
    EMOJI_MONEY = '💰'
    EMOJI_TROPHY = '🏆'
    EMOJI_GAME = '🎮'
    EMOJI_STUDY = '📚'
    EMOJI_SPORTS = '🏎️'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is required in .env file")
        return True

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please create a .env file with your Discord token.")
    print("See .env.example for reference.")
