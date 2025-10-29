# 🤖 MegaBot - Complete Documentation

**Your Ultimate Discord Server Assistant**

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [Command List](#command-list)
5. [Configuration](#configuration)
6. [Project Structure](#project-structure)
7. [Current Status](#current-status)
8. [API Integration](#api-integration)
9. [Troubleshooting](#troubleshooting)
10. [Changelog](#changelog)

---

## 🌟 Overview

MegaBot is a comprehensive, multi-purpose Discord bot with **66 commands** across **9 categories**, combining gaming, productivity, entertainment, and utility features into one powerful package.

### Statistics
- **Total Commands:** 66
- **Active Cogs:** 9 (11 total, 2 disabled)
- **Database:** SQLite with persistent storage
- **API:** Flask server on port 5000
- **Status:** 🟢 Fully Operational

---

## 🎯 Features

### 🎮 Gaming Features (5 commands)
- **Steam Integration**: View profiles, game libraries, and playtime stats
- **Game Stats**: Track currently playing games
- **LFG System**: Find teammates for multiplayer
- **Game Roles**: Auto-assign game-specific roles
- **Game Deals**: Track price alerts

### 🏆 Tournament Management (7 commands)
- Create and manage tournaments with brackets
- Team registration and match scheduling
- Automated score tracking and leaderboards
- Prize pool management

### 💰 Economy & Casino (9 commands)
- Virtual currency system with persistent database
- Gambling games (Blackjack, Slots)
- Daily rewards and work commands
- Shop with roles and perks
- Money transfer and leaderboards
- Total earnings tracking

### 📚 Study & Productivity (8 commands)
- Pomodoro study timers
- Homework reminders and tracking
- Quiz creator and flashcards
- Code snippet sharing
- Progress tracking

### 🛠️ Utility Commands (7 commands)
- Polls and voting systems
- Personal and server reminders
- Translation tools
- Calculator
- User/Server information
- Avatar display

### 🎲 Fun & Entertainment (9 commands)
- Trivia games
- Meme generator
- Joke generator
- Fortune telling
- Coin flip, dice roll
- Choice maker
- 8-ball predictions
- Rating system

### 🛡️ Moderation (12 commands)
- Kick, ban, mute, unmute
- Warning system with tracking
- Message clearing (bulk delete)
- Slowmode control
- Lock/unlock channels
- Custom welcome messages
- Auto-role assignment
- Giveaway system

### 📊 Statistics (6 commands)
- Server statistics
- Channel analytics
- Role information
- Top chatters tracking
- Emoji usage stats
- Member count tracking

### 🏅 Help & Info (4 commands)
- Interactive help system
- Bot setup wizard
- Bot information
- Dashboard overview

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Steam API Key (optional, for gaming features)

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd DiscordBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   - Copy `.env.example` to `.env`
   - Add your Discord bot token
   - Add optional API keys

4. **Run the bot**
   ```bash
   python bot.py
   ```

### First-Time Setup
1. Invite bot to your server
2. Run `/setup` to configure bot
3. Set welcome channel with `/setwelcome`
4. Configure auto-roles with `/setautorole`

---

## 📖 Complete Command List

### Help & Info (4)
- `/help` - View all commands and categories
- `/setup` - Initial bot setup wizard
- `/info` - Bot information and stats
- `/dashboard` - User dashboard overview

### Economy (9)
- `/balance` - Check your balance
- `/daily` - Claim daily reward ($100-$500)
- `/work` - Work for money ($50-$200)
- `/shop` - View shop items
- `/buy <item>` - Purchase shop items
- `/slots <amount>` - Play slots machine
- `/blackjack <amount>` - Play blackjack
- `/transfer <user> <amount>` - Send money to user
- `/leaderboard` - View richest users

### Gaming (5)
- `/steam <username>` - View Steam profile and game library
- `/playing` - See who's playing what
- `/lfg <game>` - Find teammates
- `/gamerole <game>` - Get game role
- `/gamedeal <game>` - Check game deals

### Moderation (12)
- `/kick <member> [reason]` - Kick member
- `/ban <member> [reason]` - Ban member
- `/mute <member> <duration> [reason]` - Timeout member
- `/unmute <member> [reason]` - Remove timeout
- `/warn <member> <reason>` - Issue warning
- `/clear <amount>` - Delete messages (1-100)
- `/slowmode <seconds>` - Set channel slowmode
- `/lock [channel]` - Lock channel
- `/unlock [channel]` - Unlock channel
- `/setwelcome <channel>` - Set welcome channel
- `/setautorole <role>` - Auto-assign role to new members
- `/giveaway <prize> <duration>` - Start giveaway

### Utility (7)
- `/poll <question>` - Create poll
- `/remind <time> <message>` - Set reminder
- `/translate <language> <text>` - Translate text
- `/calculate <expression>` - Calculate math
- `/userinfo [user]` - View user information
- `/serverinfo` - View server details
- `/avatar [user]` - Get user's avatar

### Fun (9)
- `/joke` - Get random joke
- `/meme <template>` - Generate meme
- `/8ball <question>` - Magic 8-ball
- `/trivia [category]` - Gaming trivia
- `/flip` - Flip a coin
- `/roll [sides]` - Roll dice
- `/choose <options>` - Let bot choose
- `/fortune` - Get fortune reading
- `/rate <thing>` - Rate something (1-10)

### Study (8)
- `/pomodoro <duration>` - Start study timer
- `/stoppomodoro` - Stop timer
- `/homework <assignment>` - Add homework
- `/homeworklist` - View homework
- `/homeworkdone <id>` - Mark complete
- `/homeworkdelete <id>` - Delete homework
- `/quiz <topic>` - Take quiz
- `/flashcard <topic>` - Study flashcards

### Statistics (6)
- `/serverstats` - Server statistics
- `/channelstats [channel]` - Channel stats
- `/roleinfo <role>` - Role information
- `/topchatters` - Most active users
- `/emojistats` - Emoji usage statistics
- `/membercount` - Member growth graph

### Tournament (7)
- `/createtournament <name>` - Create tournament
- `/jointournament <name>` - Join tournament
- `/leavetournament <name>` - Leave tournament
- `/tournamentinfo <name>` - View tournament info
- `/starttournament <name>` - Start tournament
- `/listtournaments` - List all tournaments
- `/deletetournament <name>` - Delete tournament

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Required
DISCORD_TOKEN=your_discord_bot_token_here

# Optional - Gaming Features
STEAM_API_KEY=your_steam_api_key

# Optional - Utility Features
OPENWEATHER_API_KEY=your_weather_api_key

# Optional - AI Features (Disabled)
OPENAI_API_KEY=your_openai_api_key
```

### Getting API Keys

#### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application
3. Go to "Bot" section
4. Copy token

#### Steam API Key
1. Go to [Steam Web API](https://steamcommunity.com/dev/apikey)
2. Register for API key
3. Verify domain name

---

## 📁 Project Structure

```
DiscordBot/
├── bot.py                     # Main bot file
├── config.py                  # Configuration
├── database.py                # Database manager
├── requirements.txt           # Dependencies
├── .env                       # Environment variables
├── .env.example              # Example env file
├── .gitignore                # Git ignore rules
├── bot.log                   # Bot logs (generated)
├── bot_data.db              # SQLite database (generated)
│
├── api/
│   └── bot_api.py            # Flask API server
│
├── cogs/                     # Command modules
│   ├── help.py               # Help & info commands
│   ├── gaming.py             # Gaming commands
│   ├── tournament.py         # Tournament system
│   ├── economy.py            # Economy & casino
│   ├── utility.py            # Utility commands
│   ├── study.py              # Study tools
│   ├── moderation.py         # Moderation tools
│   ├── fun.py                # Fun commands
│   ├── stats.py              # Statistics tracking
│   ├── sports.py             # DISABLED (not loaded)
│   └── ai.py                 # DISABLED (not loaded)
│
├── data/                     # Data storage
│   └── README.md
│
├── utils/                    # Helper functions (future)
│
└── docs/                     # Documentation
    ├── README.md
    ├── QUICKSTART.md
    ├── PROJECT_OVERVIEW.md
    ├── FILE_STRUCTURE.md
    ├── TROUBLESHOOTING.md
    └── ...
```

---

## 📊 Current Status

### Bot Health: 🟢 EXCELLENT
- **Commands Synced:** 66/66 ✅
- **Cogs Loaded:** 9/11 (2 intentionally disabled)
- **Bot Status:** Online and functional
- **API Server:** Running on http://localhost:5000
- **Database:** Connected (bot_data.db)

### Disabled Cogs
1. **sports.py** - Removed per user request
   - 7 sports/F1 commands disabled
   - File kept for future re-enabling
2. **ai.py** - Not loaded
   - 6 AI commands not loaded
   - Requires OpenAI API key

### Database Tables
1. **users** - User profiles, balances, earnings
2. **shop_items** - Purchase tracking with expiry
3. **warnings** - Moderation warning history
4. **reminders** - Scheduled reminders

---

## 🔌 API Integration

### Flask API Server
The bot runs a Flask API server on port 5000 for:
- Real-time bot statistics
- Website integration
- Health checks

### Endpoints
- `GET /api/stats` - Bot statistics
- `GET /api/status` - Bot online status
- `GET /api/health` - Health check

### CORS Enabled
Allows website to fetch bot data from localhost.

---

## 🔧 Troubleshooting

### Common Issues

#### Bot Not Starting
```bash
# Check dependencies
pip install -r requirements.txt

# Verify .env file exists
ls -la .env

# Check token is valid
# Go to Discord Developer Portal
```

#### Commands Not Syncing
```python
# Bot automatically syncs on startup
# Check bot.log for errors
# Verify bot has proper permissions
```

#### Database Errors
```bash
# Delete database to reset
rm bot_data.db

# Bot will recreate on next start
python bot.py
```

#### Interaction Timeout
If commands timeout:
- Check database queries are optimized
- Use `await interaction.response.defer()` for slow commands
- Daily command timeout was fixed in October 2025

---

## 📝 Changelog

### October 22, 2025

#### ✅ Completed
- Implemented complete database persistence
- All economy data now saves across restarts
- Fixed interaction timeout on `/daily` command
- Removed sports/F1 commands (user request)
- Website updated to remove sports sections
- Added 6 new commands (shop, buy, mute, unmute, warn, sportsbet - but sportsbet disabled)
- Complete code cleanup (no __pycache__, no .pyc files)
- Comprehensive audit completed

#### 🔧 Fixed
- `/daily` command timeout issue
- Balance persistence
- Cooldown tracking
- Shop purchases now saved
- Warnings tracked in database
- Reminders saved properly

#### ❌ Removed
- Sports betting commands (4)
- F1 racing commands (4)
- Sports tracking features

#### 📊 Statistics
- Commands: 73 → 66 (after sports removal)
- Cogs: 11 (9 active, 2 disabled)
- Database: Fully implemented
- API: Flask server operational

---

## 🎯 Future Enhancements

### Planned Features
- [ ] Web dashboard for management
- [ ] Advanced analytics
- [ ] More gambling games
- [ ] Achievement system
- [ ] Custom commands
- [ ] Music player

### Optional Re-additions
- [ ] AI commands (requires OpenAI key)
- [ ] Sports commands (requires sports API)
- [ ] Weather commands (requires weather API)

---

## 🤝 Contributing

This is a personal project, but feel free to:
- Report bugs
- Suggest features
- Fork and improve

---

## 📜 License

This project is for personal use and learning purposes.

---

## 👨‍💻 Author

**Your Name**

---

## 🙏 Acknowledgments

- Discord.py library
- SQLite database
- Flask API framework
- Steam Web API
- Font Awesome icons

---

**Made with ❤️ for the Discord community**

**Last Updated:** October 22, 2025
**Version:** 2.0
**Status:** 🟢 Production Ready

