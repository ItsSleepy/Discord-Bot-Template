# Discord Bot Template - Changelog

## Version 2.0 - November 3, 2025

### 🎉 Major Updates

#### Economy System Overhaul
- **Guild-Based Economy**: Each server now has its own separate economy
- **Inventory System**: Players can own and manage items
- **Rob System**: Rob other users with security items and cooldowns
- **Advanced Shop**: 11 items with security, boosts, and special items

#### New Commands (13 Economy Commands Total)
- `/inventory` - View your items and active boosts
- `/rob <user>` - Attempt to rob another user (2hr cooldown)
- `/use <item>` - Activate consumable items
- `/sell <item> [qty]` - Sell items for 50% price

#### Enhanced Existing Commands
- `/balance` - Now shows active boosts with time remaining
- `/daily` - Supports boost multipliers (Bank Upgrade, Diamond Multiplier)
- `/work` - Boost support, no-cooldown items (Energy Drink)
- `/blackjack` - Better odds items, boost multipliers
- `/slots` - Better odds items, boost multipliers
- `/shop` - Expanded from 8 to 11 items
- `/buy` - Supports security, tools, boosts, and special items

---

### 🛒 New Shop Items

#### Security Items (Auto-Active)
1. **Padlock** ($250) - Reduces rob success by 15%
2. **Alarm System** ($750) - Reduces rob success by 20% + compensation if robbed
3. **Guard Dog** ($1,000) - Reduces rob success by 25% + 30% counter-attack
4. **Lockpick** ($500) - Increases YOUR rob success by 20%
5. **Reverse Rob Card** ($800) - Auto-counter when robbed (one-time)

#### Boost Items (Must Activate with /use)
6. **Lucky Charm** ($1,000) - 2x gambling winnings (1 hour)
7. **Briefcase** ($2,500) - 2x work earnings (24 hours)
8. **Energy Drink** ($1,500) - Remove work cooldown (2 hours)
9. **Diamond Multiplier** ($10,000) - 3x all earnings (1 hour)
10. **Loaded Dice** ($3,000) - Better gambling odds (3 hours)

#### Special Items (Risk/Reward)
11. **Stock Market Tip** ($2,500) - Risky investment with 5 possible outcomes:
    - 30% - Market Crash 💥 ($0) - Lose everything
    - 20% - Down Market 📉 ($1,000-$2,000) - Small loss
    - 25% - Modest Gains 📊 ($2,600-$3,500) - Small profit
    - 15% - Bull Market 📈 ($4,000-$5,500) - Good profit
    - 5% - To The Moon 🚀 ($6,000-$8,000) - Jackpot!

---

### 🗄️ Database Changes

#### New Tables
- `shop_items` - Tracks active boosts with expiry dates
- `inventory` - Stores user items with quantities and types
- `rob_history` - Logs all robbery attempts
- `economy` table updated - Added guild_id support

#### New Database Methods (20+)
- Inventory: `add_inventory_item()`, `get_inventory()`, `get_item_quantity()`, `use_inventory_item()`
- Boosts: `add_shop_item()`, `get_active_boosts()`, `has_active_boost()`
- Rob: `add_rob_attempt()`, `get_last_rob()`
- Economy: All methods now support `guild_id` parameter

---

### 🔧 Technical Improvements

#### Code Structure
- Moved database.py to `utils/database.py`
- Updated imports in bot.py: `from utils.database import Database`
- Added admin cog to cogs list
- Improved error handling for environment variables

#### Removed Features
- ❌ OpenAI integration (unused)
- ❌ Sports betting (unused)
- ❌ Weather features (unused)
- Cleaned from: config.py, .env.example, help.py, __init__.py

#### Configuration
- Removed unused API key references
- Simplified .env.example
- Added validation for required environment variables

---

### 📊 Command Count

| Category | Commands | Change |
|----------|----------|--------|
| Economy | 13 | +4 |
| Gaming | 5 | - |
| Tournament | 7 | - |
| Study | 6 | - |
| Moderation | 8 | - |
| Fun | 8 | - |
| Utility | 12 | - |
| Help | 3 | - |
| Stats | 4 | - |
| **TOTAL** | **66** | **+4** |

---

### 🎮 Gameplay Features

#### Rob System Mechanics
- **Cooldown**: 2 hours between attempts
- **Requirements**: $500 minimum, victim needs $100+
- **Base Success**: 50% chance
- **Amount Stolen**: 10-30% of victim's balance
- **Failure Penalty**: $300-$800 fine
- **Security Modifiers**: Items affect success rates
- **Special Events**: Guard dog attacks, alarm compensation

#### Boost System
- Boosts tracked with expiry dates
- Active boosts shown in `/balance`
- Prevents duplicate boosts
- Auto-expires after duration
- Different boost types: work, gambling, all, better_odds, no_cooldown

#### Strategic Depth
- **Protection vs Offense**: Buy security or lockpicks?
- **Safe vs Risky**: Briefcase grind or Stock Market gamble?
- **Resource Management**: When to activate boosts?
- **Risk Assessment**: Can you afford to rob or invest?

---

### 🚀 Setup Instructions

1. **Copy Template**:
   ```bash
   cp -r "DiscordBot Template" "MyBot"
   cd MyBot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

4. **Required Environment Variables**:
   - `DISCORD_TOKEN` - Your Discord bot token (required)
   - `STEAM_API_KEY` - For Steam integration (optional)
   - `FORMULA1_API_KEY` - For F1 features (optional)

5. **Run Bot**:
   ```bash
   python bot.py
   ```

---

### ⚠️ Important Notes

#### Database Migration
- First run will auto-create new tables
- Existing economy data preserved
- Guild IDs default to 0 for global economy
- After first run, each server gets separate economy

#### Railway/Cloud Deployment
- Add environment variables to dashboard (not .env file)
- Never commit .env to git (in .gitignore)
- Use environment-specific configs

#### Security
- Never share your DISCORD_TOKEN
- Keep API keys private
- Use .gitignore for sensitive files
- Template is pre-sanitized (no personal data)

---

### 📝 Migration from Old Version

If upgrading from old template:

1. **Backup**: Copy your `.env` file
2. **Replace Files**: Update bot.py, config.py, cogs/economy.py, utils/database.py
3. **Update .env**: Remove unused API keys (OPENAI, SPORTS, WEATHER)
4. **Test**: Run bot locally first
5. **Deploy**: Push changes to production

---

### 🐛 Known Issues

None at this time.

---

### 🔮 Future Plans

- Additional security items
- Trading system between users
- Gambling tournaments
- Investment portfolios
- Stock market trends over time

---

### 📞 Support

For issues or questions:
- Check COMPLETE_README.md for full documentation
- Review this changelog for new features
- Test commands with `/help`

---

**Template Version**: 2.0  
**Last Updated**: November 3, 2025  
**Status**: Production Ready ✅

---

## Previous Versions

### Version 1.0 - Initial Release
- Basic economy system (9 commands)
- Gaming integration (Steam)
- Tournament system
- Study tools
- Moderation features
- Fun commands
- Utility tools
