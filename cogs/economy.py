import discord
from discord import app_commands
from discord.ext import commands
from config import Config
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger('MegaBot.Economy')

class Economy(commands.Cog):
    """Economy system with currency, gambling, and shop"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        """Display user's balance"""
        balance = await self.bot.db.get_balance(interaction.user.id)
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_MONEY} Balance",
            description=f"**{interaction.user.display_name}'s** wallet",
            color=Config.COLOR_PRIMARY
        )
        embed.add_field(name="💰 Balance", value=f"**${balance:,}**", inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="MegaBot Economy")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        """Claim daily reward"""
        user_id = interaction.user.id
        now = datetime.utcnow()
        
        # Check cooldown
        last_daily = await self.bot.db.get_last_daily(user_id)
        if last_daily:
            time_diff = now - last_daily
            if time_diff < timedelta(hours=24):
                remaining = timedelta(hours=24) - time_diff
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                
                embed = discord.Embed(
                    title=f"{Config.EMOJI_WARNING} Daily Cooldown",
                    description=f"You already claimed your daily reward!",
                    color=Config.COLOR_WARNING
                )
                embed.add_field(
                    name="⏰ Next Claim",
                    value=f"In {hours}h {minutes}m",
                    inline=False
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Give reward
        reward = Config.DAILY_REWARD
        new_balance = await self.bot.db.update_balance(user_id, reward)
        await self.bot.db.set_last_daily(user_id)
        await self.bot.db.add_earned(user_id, reward)
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_SUCCESS} Daily Reward Claimed!",
            description=f"You received **${reward}**!",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=False)
        embed.set_footer(text="Come back tomorrow for more!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="work", description="Work for money")
    async def work(self, interaction: discord.Interaction):
        """Work to earn money"""
        user_id = interaction.user.id
        now = datetime.utcnow()
        
        # Check cooldown (1 hour)
        last_work = await self.bot.db.get_last_work(user_id)
        if last_work:
            time_diff = now - last_work
            if time_diff < timedelta(hours=1):
                remaining = timedelta(hours=1) - time_diff
                minutes = int(remaining.total_seconds() // 60)
                
                embed = discord.Embed(
                    title=f"{Config.EMOJI_WARNING} Work Cooldown",
                    description=f"You're still tired from working!",
                    color=Config.COLOR_WARNING
                )
                embed.add_field(name="⏰ Rest Time", value=f"{minutes} minutes", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Random job and payment
        jobs = [
            "🍕 delivered pizzas",
            "💻 wrote some code",
            "🎨 designed a logo",
            "📚 tutored a student",
            "🚗 drove for a rideshare",
            "📦 delivered packages",
            "☕ made coffee at a café",
            "🎮 tested video games"
        ]
        
        job = random.choice(jobs)
        earned = random.randint(Config.WORK_REWARD_MIN, Config.WORK_REWARD_MAX)
        new_balance = await self.bot.db.update_balance(user_id, earned)
        await self.bot.db.set_last_work(user_id)
        await self.bot.db.add_earned(user_id, earned)
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_SUCCESS} Work Complete!",
            description=f"You {job} and earned **${earned}**!",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=False)
        embed.set_footer(text="Work again in 1 hour")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="blackjack", description="Play blackjack")
    @app_commands.describe(bet="Amount to bet")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        """Play a game of blackjack"""
        user_id = interaction.user.id
        balance = await self.bot.db.get_balance(user_id)
        
        if bet < 1:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Bet must be at least $1!",
                ephemeral=True
            )
            return
        
        if bet > balance:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You don't have enough money! Balance: ${balance:,}",
                ephemeral=True
            )
            return
        
        # Simple blackjack simulation
        player_hand = random.randint(15, 21)
        dealer_hand = random.randint(15, 21)
        
        if player_hand > 21:
            result = "Bust!"
            winnings = -bet
            color = Config.COLOR_ERROR
        elif player_hand > dealer_hand or dealer_hand > 21:
            result = "You Win!"
            winnings = bet
            color = Config.COLOR_SUCCESS
        elif player_hand == dealer_hand:
            result = "Push (Tie)"
            winnings = 0
            color = Config.COLOR_INFO
        else:
            result = "Dealer Wins"
            winnings = -bet
            color = Config.COLOR_ERROR
        
        new_balance = await self.bot.db.update_balance(user_id, winnings)
        if winnings > 0:
            await self.bot.db.add_earned(user_id, winnings)
        
        embed = discord.Embed(
            title="🃏 Blackjack",
            description=result,
            color=color
        )
        embed.add_field(name="Your Hand", value=f"**{player_hand}**", inline=True)
        embed.add_field(name="Dealer Hand", value=f"**{dealer_hand}**", inline=True)
        embed.add_field(name="Result", value=f"**${winnings:+,}**", inline=False)
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=False)
        embed.set_footer(text="MegaBot Casino")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="slots", description="Play the slot machine")
    @app_commands.describe(bet="Amount to bet")
    async def slots(self, interaction: discord.Interaction, bet: int):
        """Play slots"""
        user_id = interaction.user.id
        balance = await self.bot.db.get_balance(user_id)
        
        if bet < 1:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Bet must be at least $1!",
                ephemeral=True
            )
            return
        
        if bet > balance:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You don't have enough money! Balance: ${balance:,}",
                ephemeral=True
            )
            return
        
        # Slot symbols
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
        weights = [30, 25, 20, 15, 8, 2]  # Diamond and 7 are rarer
        
        slot1 = random.choices(symbols, weights=weights)[0]
        slot2 = random.choices(symbols, weights=weights)[0]
        slot3 = random.choices(symbols, weights=weights)[0]
        
        # Calculate winnings
        if slot1 == slot2 == slot3:
            if slot1 == "💎":
                multiplier = 10
            elif slot1 == "7️⃣":
                multiplier = 15
            else:
                multiplier = 5
            winnings = bet * multiplier
            result = f"🎉 JACKPOT! {multiplier}x"
            color = Config.COLOR_SUCCESS
        elif slot1 == slot2 or slot2 == slot3:
            winnings = bet
            result = "Nice! 1x"
            color = Config.COLOR_INFO
        else:
            winnings = -bet
            result = "Try again!"
            color = Config.COLOR_ERROR
        
        new_balance = await self.bot.db.update_balance(user_id, winnings)
        if winnings > 0:
            await self.bot.db.add_earned(user_id, winnings)
        
        embed = discord.Embed(
            title="🎰 Slot Machine",
            description=f"{slot1} | {slot2} | {slot3}",
            color=color
        )
        embed.add_field(name="Result", value=result, inline=False)
        embed.add_field(name="Winnings", value=f"**${winnings:+,}**", inline=True)
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=True)
        embed.set_footer(text="MegaBot Casino")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="transfer", description="Transfer money to another user")
    @app_commands.describe(user="User to transfer to", amount="Amount to transfer")
    async def transfer(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Transfer money between users"""
        if user.bot:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You can't transfer to a bot!",
                ephemeral=True
            )
            return
        
        if user.id == interaction.user.id:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You can't transfer to yourself!",
                ephemeral=True
            )
            return
        
        if amount < 1:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Amount must be at least $1!",
                ephemeral=True
            )
            return
        
        sender_balance = await self.bot.db.get_balance(interaction.user.id)
        if amount > sender_balance:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You don't have enough money! Balance: ${sender_balance:,}",
                ephemeral=True
            )
            return
        
        # Perform transfer
        await self.bot.db.update_balance(interaction.user.id, -amount)
        await self.bot.db.update_balance(user.id, amount)
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_SUCCESS} Transfer Complete!",
            description=f"**{interaction.user.display_name}** sent **${amount:,}** to **{user.display_name}**",
            color=Config.COLOR_SUCCESS
        )
        embed.set_footer(text="MegaBot Economy")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="View the richest users")
    async def leaderboard(self, interaction: discord.Interaction):
        """Display economy leaderboard"""
        await interaction.response.defer()
        
        # Get top users from database
        leaderboard_data = await self.bot.db.get_leaderboard(10)
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_TROPHY} Economy Leaderboard",
            description="Top 10 Richest Users",
            color=Config.COLOR_PRIMARY
        )
        
        if not leaderboard_data:
            embed.description = "No users in the economy yet!"
        else:
            leaderboard_text = []
            for i, (user_id, balance) in enumerate(leaderboard_data, 1):
                user = interaction.guild.get_member(user_id)
                if user:
                    emoji = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}️⃣"
                    leaderboard_text.append(f"{emoji} **{user.display_name}** - ${balance:,}")
            
            embed.description = "\n".join(leaderboard_text) if leaderboard_text else "No users found!"
        
        embed.set_footer(text="MegaBot Economy")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="shop", description="View the item shop")
    async def shop(self, interaction: discord.Interaction):
        """Display shop items"""
        embed = discord.Embed(
            title="🛒 MegaBot Shop",
            description="Purchase items to boost your earnings and get advantages!",
            color=Config.COLOR_PRIMARY
        )
        
        # Shop items - earning boosters and advantages
        items = [
            {
                "name": "� Lucky Charm",
                "price": 1000,
                "description": "2x gambling winnings for 1 hour"
            },
            {
                "name": "💼 Briefcase",
                "price": 2500,
                "description": "2x work earnings for 24 hours"
            },
            {
                "name": "🎰 Casino Pass",
                "price": 5000,
                "description": "No bet limits for 24 hours"
            },
            {
                "name": "⚡ Energy Drink",
                "price": 1500,
                "description": "Remove work cooldown for 2 hours"
            },
            {
                "name": "💎 Diamond Multiplier",
                "price": 10000,
                "description": "3x all earnings for 1 hour"
            },
            {
                "name": "� Bank Upgrade",
                "price": 7500,
                "description": "Increase daily reward by 50% (permanent)"
            },
            {
                "name": "� Loaded Dice",
                "price": 3000,
                "description": "Better gambling odds for 3 hours"
            },
            {
                "name": "📈 Stock Market Tip",
                "price": 500,
                "description": "Instant $800-$1200 gain"
            }
        ]
        
        for item in items:
            embed.add_field(
                name=f"{item['name']} - ${item['price']:,}",
                value=item['description'],
                inline=False
            )
        
        embed.add_field(
            name="💡 How to Buy",
            value="Use `/buy <item_name>` to purchase!\nExample: `/buy Lucky Charm`",
            inline=False
        )
        
        embed.set_footer(text="MegaBot Economy • Boosts and advantages")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item="Item name to purchase")
    async def buy(self, interaction: discord.Interaction, item: str):
        """Purchase an item from the shop"""
        user_id = interaction.user.id
        balance = await self.bot.db.get_balance(user_id)
        
        # Shop items database with effects
        shop_items = {
            "lucky charm": {
                "price": 1000, 
                "emoji": "🍀",
                "effect": "gambling_boost",
                "duration": 3600,  # 1 hour
                "description": "2x gambling winnings for 1 hour"
            },
            "briefcase": {
                "price": 2500,
                "emoji": "💼",
                "effect": "work_boost",
                "duration": 86400,  # 24 hours
                "description": "2x work earnings for 24 hours"
            },
            "casino pass": {
                "price": 5000,
                "emoji": "�",
                "effect": "no_bet_limit",
                "duration": 86400,
                "description": "No bet limits for 24 hours"
            },
            "energy drink": {
                "price": 1500,
                "emoji": "⚡",
                "effect": "no_cooldown",
                "duration": 7200,  # 2 hours
                "description": "Remove work cooldown for 2 hours"
            },
            "diamond multiplier": {
                "price": 10000,
                "emoji": "💎",
                "effect": "all_boost",
                "duration": 3600,
                "description": "3x all earnings for 1 hour"
            },
            "bank upgrade": {
                "price": 7500,
                "emoji": "�",
                "effect": "daily_boost",
                "duration": None,  # Permanent
                "description": "Increase daily reward by 50% (permanent)"
            },
            "loaded dice": {
                "price": 3000,
                "emoji": "�",
                "effect": "better_odds",
                "duration": 10800,  # 3 hours
                "description": "Better gambling odds for 3 hours"
            },
            "stock market tip": {
                "price": 500,
                "emoji": "📈",
                "effect": "instant_cash",
                "duration": None,
                "description": "Instant $800-$1200 gain"
            }
        }
        
        item_lower = item.lower()
        if item_lower not in shop_items:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Item not found! Use `/shop` to see available items.",
                ephemeral=True
            )
            return
        
        item_data = shop_items[item_lower]
        price = item_data["price"]
        
        if balance < price:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Not enough money! You need ${price:,} but have ${balance:,}",
                ephemeral=True
            )
            return
        
        # Process purchase
        await self.bot.db.update_balance(user_id, -price)
        
        # Apply instant effects
        bonus_text = ""
        if item_data["effect"] == "instant_cash":
            bonus = random.randint(800, 1200)
            await self.bot.db.update_balance(user_id, bonus)
            await self.bot.db.add_earned(user_id, bonus)
            bonus_text = f"\n\n💰 **Instant Gain:** You received ${bonus:,}!"
        else:
            # Save non-instant items to database
            expiry_date = None
            if item_data["duration"]:
                expiry_date = datetime.utcnow() + timedelta(seconds=item_data["duration"])
            await self.bot.db.add_shop_item(user_id, item_lower, expiry_date)
        
        # Build embed
        new_balance = await self.bot.db.get_balance(user_id)
        embed = discord.Embed(
            title=f"{Config.EMOJI_SUCCESS} Purchase Successful!",
            description=f"You bought **{item_data['emoji']} {item.title()}**!{bonus_text}",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="💵 Price Paid", value=f"${price:,}", inline=True)
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=True)
        
        # Add effect description
        if item_data["duration"]:
            hours = item_data["duration"] / 3600
            duration_text = f"{hours:.0f} hour{'s' if hours != 1 else ''}"
            embed.add_field(
                name="⏱️ Active For",
                value=duration_text,
                inline=False
            )
        elif item_data["effect"] != "instant_cash":
            embed.add_field(
                name="✨ Effect",
                value="Permanent upgrade!",
                inline=False
            )
        
        embed.add_field(
            name="📋 Description",
            value=item_data["description"],
            inline=False
        )
        
        # Note about boosts (since we don't have active boost tracking yet)
        if item_data["effect"] not in ["instant_cash"]:
            embed.add_field(
                name="💡 Note",
                value="Boost effects are currently simulated. Full boost system coming soon!",
                inline=False
            )
        
        embed.set_footer(text="MegaBot Shop • Thank you for your purchase!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
    logger.info("Economy cog loaded")
