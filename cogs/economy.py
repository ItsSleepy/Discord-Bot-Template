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
        guild_id = interaction.guild.id if interaction.guild else 0
        balance = await self.bot.db.get_balance(interaction.user.id, guild_id)
        
        # Get active boosts
        boosts = await self.bot.db.get_active_boosts(interaction.user.id, guild_id)
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_MONEY} Balance",
            description=f"**{interaction.user.display_name}'s** wallet",
            color=Config.COLOR_PRIMARY
        )
        embed.add_field(name="💰 Balance", value=f"**${balance:,}**", inline=False)
        
        # Show active boosts
        if boosts:
            boost_list = []
            for boost in boosts:
                item_name = boost['item_name'].replace('_', ' ').title()
                if boost['expiry_date']:
                    remaining = boost['expiry_date'] - datetime.utcnow()
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                    boost_list.append(f"✨ {item_name} ({time_str})")
                else:
                    boost_list.append(f"✨ {item_name} (Permanent)")
            
            embed.add_field(
                name="🎁 Active Boosts",
                value="\n".join(boost_list),
                inline=False
            )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="MegaBot Economy")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        """Claim daily reward"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0
        now = datetime.utcnow()
        
        # Check cooldown
        last_daily = await self.bot.db.get_last_daily(user_id, guild_id)
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
        
        # Apply boosts
        boost_text = ""
        has_bank_upgrade = await self.bot.db.has_active_boost(user_id, guild_id, "daily_boost")
        has_all_boost = await self.bot.db.has_active_boost(user_id, guild_id, "all_boost")
        
        if has_all_boost:
            reward = int(reward * 3)
            boost_text = "\n💎 **Diamond Multiplier Active!** (3x)"
        elif has_bank_upgrade:
            reward = int(reward * 1.5)
            boost_text = "\n🏦 **Bank Upgrade Active!** (+50%)"
        
        new_balance = await self.bot.db.update_balance(user_id, reward, guild_id)
        await self.bot.db.set_last_daily(user_id, guild_id)
        await self.bot.db.add_earned(user_id, reward, guild_id)
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_SUCCESS} Daily Reward Claimed!",
            description=f"You received **${reward}**!{boost_text}",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=False)
        embed.set_footer(text="Come back tomorrow for more!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="work", description="Work for money")
    async def work(self, interaction: discord.Interaction):
        """Work to earn money"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0
        now = datetime.utcnow()
        
        # Check for no cooldown boost
        has_no_cooldown = await self.bot.db.has_active_boost(user_id, guild_id, "no_cooldown")
        
        if not has_no_cooldown:
            # Check cooldown (1 hour)
            last_work = await self.bot.db.get_last_work(user_id, guild_id)
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
        
        # Apply boosts
        boost_text = ""
        has_work_boost = await self.bot.db.has_active_boost(user_id, guild_id, "work_boost")
        has_all_boost = await self.bot.db.has_active_boost(user_id, guild_id, "all_boost")
        
        if has_all_boost:
            earned *= 3
            boost_text = "\n💎 **Diamond Multiplier Active!** (3x)"
        elif has_work_boost:
            earned *= 2
            boost_text = "\n💼 **Briefcase Boost Active!** (2x)"
        
        new_balance = await self.bot.db.update_balance(user_id, earned, guild_id)
        await self.bot.db.set_last_work(user_id, guild_id)
        await self.bot.db.add_earned(user_id, earned, guild_id)
        
        embed = discord.Embed(
            title=f"{Config.EMOJI_SUCCESS} Work Complete!",
            description=f"You {job} and earned **${earned}**!{boost_text}",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=False)
        
        cooldown_text = "No cooldown!" if has_no_cooldown else "Work again in 1 hour"
        embed.set_footer(text=cooldown_text)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="blackjack", description="Play blackjack")
    @app_commands.describe(bet="Amount to bet")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        """Play a game of blackjack"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0
        balance = await self.bot.db.get_balance(user_id, guild_id)
        
        # Minimum bet requirement
        min_bet = 100
        if bet < min_bet:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Minimum bet is ${min_bet}! Please bet at least ${min_bet}.",
                ephemeral=True
            )
            return
        
        if bet > balance:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You don't have enough money! Balance: ${balance:,}",
                ephemeral=True
            )
            return
        
        # Check for better odds boost
        has_better_odds = await self.bot.db.has_active_boost(user_id, guild_id, "better_odds")
        has_gambling_boost = await self.bot.db.has_active_boost(user_id, guild_id, "gambling_boost")
        has_all_boost = await self.bot.db.has_active_boost(user_id, guild_id, "all_boost")
        
        # Simple blackjack simulation with better odds for player if they have boost
        if has_better_odds:
            player_hand = random.randint(17, 21)  # Better starting hand
            dealer_hand = random.randint(15, 20)
        else:
            player_hand = random.randint(15, 21)
            dealer_hand = random.randint(15, 21)
        
        if player_hand > 21:
            result = "Bust!"
            winnings = -bet
            color = Config.COLOR_ERROR
        elif player_hand > dealer_hand or dealer_hand > 21:
            result = "You Win!"
            winnings = bet
            
            # Apply gambling boosts to winnings
            boost_text = ""
            if has_all_boost:
                winnings *= 3
                boost_text = "\n💎 **Diamond Multiplier!** (3x)"
            elif has_gambling_boost:
                winnings *= 2
                boost_text = "\n🍀 **Lucky Charm!** (2x)"
            
            result += boost_text
            color = Config.COLOR_SUCCESS
        elif player_hand == dealer_hand:
            result = "Push (Tie)"
            winnings = 0
            color = Config.COLOR_INFO
        else:
            result = "Dealer Wins"
            winnings = -bet
            color = Config.COLOR_ERROR
        
        new_balance = await self.bot.db.update_balance(user_id, winnings, guild_id)
        if winnings > 0:
            await self.bot.db.add_earned(user_id, winnings, guild_id)
        
        embed = discord.Embed(
            title="🃏 Blackjack",
            description=result,
            color=color
        )
        embed.add_field(name="Your Hand", value=f"**{player_hand}**", inline=True)
        embed.add_field(name="Dealer Hand", value=f"**{dealer_hand}**", inline=True)
        embed.add_field(name="Result", value=f"**${winnings:+,}**", inline=False)
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=False)
        
        # Show active boosts
        active_boosts = []
        if has_better_odds:
            active_boosts.append("🎲 Loaded Dice")
        if has_gambling_boost:
            active_boosts.append("🍀 Lucky Charm")
        if has_all_boost:
            active_boosts.append("💎 Diamond Multiplier")
        
        if active_boosts:
            embed.add_field(name="✨ Active Boosts", value=" • ".join(active_boosts), inline=False)
        
        embed.set_footer(text="MegaBot Casino")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="slots", description="Play the slot machine")
    @app_commands.describe(bet="Amount to bet")
    async def slots(self, interaction: discord.Interaction, bet: int):
        """Play slots"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0
        balance = await self.bot.db.get_balance(user_id, guild_id)
        
        # Minimum bet requirement
        min_bet = 100
        if bet < min_bet:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Minimum bet is ${min_bet}! Please bet at least ${min_bet}.",
                ephemeral=True
            )
            return
        
        if bet > balance:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You don't have enough money! Balance: ${balance:,}",
                ephemeral=True
            )
            return
        
        # Check for boosts
        has_better_odds = await self.bot.db.has_active_boost(user_id, guild_id, "better_odds")
        has_gambling_boost = await self.bot.db.has_active_boost(user_id, guild_id, "gambling_boost")
        has_all_boost = await self.bot.db.has_active_boost(user_id, guild_id, "all_boost")
        
        # Slot symbols
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
        
        # Better odds if player has the boost
        if has_better_odds:
            weights = [25, 20, 18, 17, 12, 8]  # Better chances for rare symbols
        else:
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
        
        # Apply gambling boosts to positive winnings
        boost_text = ""
        if winnings > 0:
            if has_all_boost:
                winnings = int(winnings * 3)
                boost_text = "\n💎 **Diamond Multiplier!** (3x)"
            elif has_gambling_boost:
                winnings = int(winnings * 2)
                boost_text = "\n🍀 **Lucky Charm!** (2x)"
        
        new_balance = await self.bot.db.update_balance(user_id, winnings, guild_id)
        if winnings > 0:
            await self.bot.db.add_earned(user_id, winnings, guild_id)
        
        embed = discord.Embed(
            title="🎰 Slot Machine",
            description=f"{slot1} | {slot2} | {slot3}",
            color=color
        )
        embed.add_field(name="Result", value=result + boost_text, inline=False)
        embed.add_field(name="Winnings", value=f"**${winnings:+,}**", inline=True)
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=True)
        
        # Show active boosts
        active_boosts = []
        if has_better_odds:
            active_boosts.append("🎲 Loaded Dice")
        if has_gambling_boost:
            active_boosts.append("🍀 Lucky Charm")
        if has_all_boost:
            active_boosts.append("💎 Diamond Multiplier")
        
        if active_boosts:
            embed.add_field(name="✨ Active Boosts", value=" • ".join(active_boosts), inline=False)
        
        embed.set_footer(text="MegaBot Casino")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="transfer", description="Transfer money to another user")
    @app_commands.describe(user="User to transfer to", amount="Amount to transfer")
    async def transfer(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Transfer money between users"""
        guild_id = interaction.guild.id if interaction.guild else 0
        
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
        
        sender_balance = await self.bot.db.get_balance(interaction.user.id, guild_id)
        if amount > sender_balance:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You don't have enough money! Balance: ${sender_balance:,}",
                ephemeral=True
            )
            return
        
        # Perform transfer
        await self.bot.db.update_balance(interaction.user.id, -amount, guild_id)
        await self.bot.db.update_balance(user.id, amount, guild_id)
        
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
        
        guild_id = interaction.guild.id if interaction.guild else 0
        
        # Get top users from database
        leaderboard_data = await self.bot.db.get_leaderboard(10, guild_id)
        
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
                user = interaction.guild.get_member(user_id) if interaction.guild else None
                if user:
                    emoji = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}️⃣"
                    leaderboard_text.append(f"{emoji} **{user.display_name}** - ${balance:,}")
            
            embed.description = "\n".join(leaderboard_text) if leaderboard_text else "No users found!"
        
        embed.set_footer(text="MegaBot Economy")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="inventory", description="View your inventory")
    async def inventory(self, interaction: discord.Interaction):
        """Display user's inventory"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0
        
        items = await self.bot.db.get_inventory(user_id, guild_id)
        
        embed = discord.Embed(
            title=f"🎒 {interaction.user.display_name}'s Inventory",
            color=Config.COLOR_PRIMARY
        )
        
        if not items:
            embed.description = "Your inventory is empty!\nBuy items from `/shop` to fill it up."
        else:
            # Group by item type
            security_items = [item for item in items if item['item_type'] == 'security']
            consumables = [item for item in items if item['item_type'] == 'consumable']
            tools = [item for item in items if item['item_type'] == 'tool']
            
            if security_items:
                security_text = []
                for item in security_items:
                    name = item['item_name'].replace('_', ' ').title()
                    security_text.append(f"🛡️ **{name}** x{item['quantity']}")
                embed.add_field(name="🔒 Security Items", value="\n".join(security_text), inline=False)
            
            if tools:
                tool_text = []
                for item in tools:
                    name = item['item_name'].replace('_', ' ').title()
                    tool_text.append(f"🔧 **{name}** x{item['quantity']}")
                embed.add_field(name="🛠️ Tools", value="\n".join(tool_text), inline=False)
            
            if consumables:
                consumable_text = []
                for item in consumables:
                    name = item['item_name'].replace('_', ' ').title()
                    consumable_text.append(f"✨ **{name}** x{item['quantity']}")
                embed.add_field(name="💊 Consumables", value="\n".join(consumable_text), inline=False)
        
        embed.set_footer(text="Use /use <item> to activate items • /shop to buy more")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rob", description="Attempt to rob another user")
    @app_commands.describe(user="User to rob")
    async def rob(self, interaction: discord.Interaction, user: discord.Member):
        """Rob another user"""
        robber_id = interaction.user.id
        victim_id = user.id
        guild_id = interaction.guild.id if interaction.guild else 0
        
        # Validation checks
        if user.bot:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You can't rob a bot!",
                ephemeral=True
            )
            return
        
        if user.id == robber_id:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You can't rob yourself!",
                ephemeral=True
            )
            return
        
        # Check cooldown (2 hours)
        last_rob = await self.bot.db.get_last_rob(robber_id, guild_id)
        if last_rob:
            time_diff = datetime.utcnow() - last_rob
            if time_diff < timedelta(hours=2):
                remaining = timedelta(hours=2) - time_diff
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                
                embed = discord.Embed(
                    title=f"{Config.EMOJI_WARNING} Rob Cooldown",
                    description="You need to lay low for a while!",
                    color=Config.COLOR_WARNING
                )
                embed.add_field(name="⏰ Next Rob", value=f"In {hours}h {minutes}m", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Get balances
        robber_balance = await self.bot.db.get_balance(robber_id, guild_id)
        victim_balance = await self.bot.db.get_balance(victim_id, guild_id)
        
        # Check minimum balance for robber
        if robber_balance < 500:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You need at least $500 to attempt a rob!",
                ephemeral=True
            )
            return
        
        # Check victim has money worth stealing
        if victim_balance < 100:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} {user.display_name} is too poor to rob! (Less than $100)",
                ephemeral=True
            )
            return
        
        # Check for security items
        victim_padlock = await self.bot.db.get_item_quantity(victim_id, guild_id, "padlock")
        victim_alarm = await self.bot.db.get_item_quantity(victim_id, guild_id, "alarm_system")
        victim_guard_dog = await self.bot.db.get_item_quantity(victim_id, guild_id, "guard_dog")
        robber_lockpick = await self.bot.db.get_item_quantity(robber_id, guild_id, "lockpick")
        
        # Base success rate: 50%
        success_rate = 50
        
        # Security items reduce success rate
        if victim_padlock > 0:
            success_rate -= 15  # Padlock: -15%
        if victim_alarm > 0:
            success_rate -= 20  # Alarm: -20%
        if victim_guard_dog > 0:
            success_rate -= 25  # Guard Dog: -25%
        
        # Lockpick increases success rate
        if robber_lockpick > 0:
            success_rate += 20  # Lockpick: +20%
        
        # Minimum 5%, maximum 90%
        success_rate = max(5, min(90, success_rate))
        
        # Determine success
        success = random.randint(1, 100) <= success_rate
        
        if success:
            # Calculate stolen amount (10-30% of victim's balance)
            steal_percent = random.randint(10, 30) / 100
            stolen_amount = int(victim_balance * steal_percent)
            stolen_amount = min(stolen_amount, victim_balance)  # Can't steal more than they have
            
            # Transfer money
            await self.bot.db.update_balance(victim_id, -stolen_amount, guild_id)
            await self.bot.db.update_balance(robber_id, stolen_amount, guild_id)
            await self.bot.db.add_earned(robber_id, stolen_amount, guild_id)
            
            # Consume security items (they break after successful defense attempt... but rob succeeded)
            # Guard dog has a chance to counter-attack
            counter_attack = False
            if victim_guard_dog > 0 and random.randint(1, 100) <= 30:  # 30% counter-attack
                counter_attack = True
                counter_damage = random.randint(200, 500)
                await self.bot.db.update_balance(robber_id, -counter_damage, guild_id)
                await self.bot.db.use_inventory_item(victim_id, guild_id, "guard_dog", 1)
            
            embed = discord.Embed(
                title=f"💰 Rob Successful!",
                description=f"You successfully robbed **{user.display_name}**!",
                color=Config.COLOR_SUCCESS
            )
            embed.add_field(name="💵 Stolen", value=f"${stolen_amount:,}", inline=True)
            embed.add_field(name="📊 Success Rate", value=f"{success_rate}%", inline=True)
            
            if counter_attack:
                embed.add_field(
                    name="🐕 Guard Dog Attack!",
                    value=f"The guard dog bit you! Lost ${counter_damage:,}",
                    inline=False
                )
            
            new_balance = await self.bot.db.get_balance(robber_id, guild_id)
            embed.add_field(name="💰 Your New Balance", value=f"${new_balance:,}", inline=False)
            
        else:
            # Rob failed - robber loses money as fine
            fine = random.randint(300, 800)
            await self.bot.db.update_balance(robber_id, -fine, guild_id)
            
            # Victim gets notified and may get compensation
            compensation = 0
            if victim_alarm > 0:
                # Alarm triggers police - robber pays more, victim gets compensation
                compensation = int(fine * 0.5)
                await self.bot.db.update_balance(victim_id, compensation, guild_id)
                await self.bot.db.use_inventory_item(victim_id, guild_id, "alarm_system", 1)
            
            embed = discord.Embed(
                title=f"🚨 Rob Failed!",
                description=f"You were caught trying to rob **{user.display_name}**!",
                color=Config.COLOR_ERROR
            )
            embed.add_field(name="💸 Fine Paid", value=f"${fine:,}", inline=True)
            embed.add_field(name="📊 Success Rate", value=f"{success_rate}%", inline=True)
            
            if compensation > 0:
                embed.add_field(
                    name="🚨 Alarm Triggered!",
                    value=f"Police caught you! Victim received ${compensation:,} compensation",
                    inline=False
                )
            
            new_balance = await self.bot.db.get_balance(robber_id, guild_id)
            embed.add_field(name="💰 Your New Balance", value=f"${new_balance:,}", inline=False)
        
        # Record attempt
        await self.bot.db.add_rob_attempt(robber_id, victim_id, guild_id, stolen_amount if success else 0, success)
        
        # Show security items that were active
        security_active = []
        if victim_padlock > 0:
            security_active.append("🔒 Padlock (-15%)")
        if victim_alarm > 0:
            security_active.append("🚨 Alarm System (-20%)")
        if victim_guard_dog > 0:
            security_active.append("🐕 Guard Dog (-25%)")
        if robber_lockpick > 0:
            security_active.append("🔓 Your Lockpick (+20%)")
        
        if security_active:
            embed.add_field(name="🛡️ Active Items", value="\n".join(security_active), inline=False)
        
        embed.set_footer(text=f"Rob again in 2 hours • Success rate: {success_rate}%")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="use", description="Use an item from your inventory")
    @app_commands.describe(item="Item name to use")
    async def use_item(self, interaction: discord.Interaction, item: str):
        """Use/activate an item from inventory"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0
        
        item_lower = item.lower().replace(' ', '_')
        
        # Check if user has the item
        quantity = await self.bot.db.get_item_quantity(user_id, guild_id, item_lower)
        if quantity <= 0:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You don't have any **{item}** in your inventory!",
                ephemeral=True
            )
            return
        
        # Define usable items (boosts/consumables)
        usable_items = {
            "lucky_charm": {
                "effect": "gambling_boost",
                "duration": 3600,
                "description": "2x gambling winnings for 1 hour"
            },
            "briefcase": {
                "effect": "work_boost",
                "duration": 86400,
                "description": "2x work earnings for 24 hours"
            },
            "energy_drink": {
                "effect": "no_cooldown",
                "duration": 7200,
                "description": "Remove work cooldown for 2 hours"
            },
            "diamond_multiplier": {
                "effect": "all_boost",
                "duration": 3600,
                "description": "3x all earnings for 1 hour"
            },
            "loaded_dice": {
                "effect": "better_odds",
                "duration": 10800,
                "description": "Better gambling odds for 3 hours"
            },
            "stock_market_tip": {
                "effect": "stock_cooldown",
                "duration": 86400,
                "description": "Risky investment - can crash or moon!",
                "instant_payout": True
            }
        }
        
        if item_lower not in usable_items:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} **{item}** cannot be used! It's a passive item that works automatically.",
                ephemeral=True
            )
            return
        
        # Check if user already has this boost active
        item_data = usable_items[item_lower]
        has_boost = await self.bot.db.has_active_boost(user_id, guild_id, item_data["effect"])
        if has_boost:
            await interaction.response.send_message(
                f"{Config.EMOJI_WARNING} You already have this boost active! Wait for it to expire.",
                ephemeral=True
            )
            return
        
        # Use the item
        success = await self.bot.db.use_inventory_item(user_id, guild_id, item_lower, 1)
        if not success:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Failed to use item!",
                ephemeral=True
            )
            return
        
        # Check if this is a special instant payout item (Stock Market Tip)
        if item_data.get("instant_payout"):
            # Stock market with risk/reward - weighted random outcomes
            roll = random.randint(1, 100)
            
            if roll <= 30:  # 30% - Market Crash 💥
                payout = 0
                outcome = "💥 **MARKET CRASH!**"
                description = "The market crashed and you lost your entire investment!"
                color = Config.COLOR_ERROR
                result_emoji = "📉"
            elif roll <= 50:  # 20% - Small Loss 📉
                payout = random.randint(1000, 2000)
                loss = 2500 - payout
                outcome = f"📉 **Down Market**"
                description = f"The market is down. You lost ${loss:,}."
                color = Config.COLOR_WARNING
                result_emoji = "📉"
            elif roll <= 75:  # 25% - Small Profit 📊
                payout = random.randint(2600, 3500)
                profit = payout - 2500
                outcome = f"📊 **Modest Gains**"
                description = f"Small returns. You gained ${profit:,}."
                color = Config.COLOR_INFO
                result_emoji = "📊"
            elif roll <= 90:  # 15% - Good Profit 📈
                payout = random.randint(4000, 5500)
                profit = payout - 2500
                outcome = f"📈 **Bull Market!**"
                description = f"Excellent returns! You gained ${profit:,}!"
                color = Config.COLOR_SUCCESS
                result_emoji = "📈"
            else:  # 5% - Jackpot 🚀
                payout = random.randint(6000, 8000)
                profit = payout - 2500
                outcome = f"🚀 **TO THE MOON!**"
                description = f"MASSIVE RETURNS! You gained ${profit:,}!!!"
                color = Config.COLOR_SUCCESS
                result_emoji = "🚀"
            
            # Apply the payout
            await self.bot.db.update_balance(user_id, payout, guild_id)
            if payout > 0:
                await self.bot.db.add_earned(user_id, payout, guild_id)
            
            # Add cooldown boost to prevent immediate re-use
            expiry_date = datetime.utcnow() + timedelta(seconds=item_data["duration"])
            await self.bot.db.add_shop_item(user_id, guild_id, item_lower, item_data["effect"], expiry_date)
            
            new_balance = await self.bot.db.get_balance(user_id, guild_id)
            embed = discord.Embed(
                title=f"{result_emoji} Stock Market Result",
                description=description,
                color=color
            )
            embed.add_field(name="📊 Outcome", value=outcome, inline=False)
            embed.add_field(name="💵 Investment", value="$2,500", inline=True)
            embed.add_field(name="💰 Return", value=f"${payout:,}", inline=True)
            
            # Show profit/loss
            net_result = payout - 2500
            if net_result > 0:
                embed.add_field(name="✅ Net Profit", value=f"+${net_result:,}", inline=True)
            elif net_result < 0:
                embed.add_field(name="❌ Net Loss", value=f"-${abs(net_result):,}", inline=True)
            else:
                embed.add_field(name="⚖️ Break Even", value="$0", inline=True)
            
            embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=False)
            embed.add_field(name="⏰ Cooldown", value="Can invest again in 24 hours", inline=False)
            
            # Add flavor text based on outcome
            if payout == 0:
                embed.set_footer(text="💸 Better luck next time! The market is unpredictable.")
            elif net_result < 0:
                embed.set_footer(text="📉 Sometimes you win, sometimes you lose. That's investing!")
            elif net_result < 1000:
                embed.set_footer(text="📊 Slow and steady gains. Not bad!")
            elif net_result < 3000:
                embed.set_footer(text="📈 Great investment! You timed the market well!")
            else:
                embed.set_footer(text="🚀 DIAMOND HANDS! 💎🙌 You're a stock market genius!")
            
            await interaction.response.send_message(embed=embed)
            return
        
        # Activate the boost (for normal consumables)
        expiry_date = datetime.utcnow() + timedelta(seconds=item_data["duration"])
        await self.bot.db.add_shop_item(user_id, guild_id, item_lower, item_data["effect"], expiry_date)
        
        hours = item_data["duration"] / 3600
        embed = discord.Embed(
            title=f"✨ Item Activated!",
            description=f"You used **{item.replace('_', ' ').title()}**!",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="⏱️ Duration", value=f"{hours:.0f} hour{'s' if hours != 1 else ''}", inline=True)
        embed.add_field(name="📋 Effect", value=item_data["description"], inline=False)
        embed.set_footer(text="Boost is now active! Check /balance to see active boosts")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="sell", description="Sell an item from your inventory")
    @app_commands.describe(item="Item name to sell", quantity="Amount to sell (default: 1)")
    async def sell(self, interaction: discord.Interaction, item: str, quantity: int = 1):
        """Sell items from inventory"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0
        
        if quantity < 1:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Quantity must be at least 1!",
                ephemeral=True
            )
            return
        
        item_lower = item.lower().replace(' ', '_')
        
        # Check if user has enough of the item
        current_qty = await self.bot.db.get_item_quantity(user_id, guild_id, item_lower)
        if current_qty < quantity:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} You only have {current_qty}x **{item}**!",
                ephemeral=True
            )
            return
        
        # Define sell prices (50% of buy price)
        sell_prices = {
            "padlock": 125,
            "alarm_system": 375,
            "guard_dog": 500,
            "lockpick": 250,
            "lucky_charm": 500,
            "briefcase": 1250,
            "energy_drink": 750,
            "diamond_multiplier": 5000,
            "loaded_dice": 1500,
            "reverse_rob_card": 400,
            "stock_market_tip": 1250
        }
        
        if item_lower not in sell_prices:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} This item cannot be sold!",
                ephemeral=True
            )
            return
        
        # Calculate total sell value
        sell_value = sell_prices[item_lower] * quantity
        
        # Remove items and give money
        success = await self.bot.db.use_inventory_item(user_id, guild_id, item_lower, quantity)
        if not success:
            await interaction.response.send_message(
                f"{Config.EMOJI_ERROR} Failed to sell item!",
                ephemeral=True
            )
            return
        
        new_balance = await self.bot.db.update_balance(user_id, sell_value, guild_id)
        
        embed = discord.Embed(
            title=f"💵 Item Sold!",
            description=f"You sold **{quantity}x {item.replace('_', ' ').title()}**",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="💰 Received", value=f"${sell_value:,}", inline=True)
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=True)
        embed.set_footer(text="Items sell for 50% of their purchase price")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="shop", description="View the item shop")
    async def shop(self, interaction: discord.Interaction):
        """Display shop items"""
        embed = discord.Embed(
            title="🛒 MegaBot Shop",
            description="Purchase items to boost your earnings, get protection, and more!",
            color=Config.COLOR_PRIMARY
        )
        
        # Security items
        embed.add_field(
            name="🔒 **Padlock** - $250",
            value="Reduces rob success rate by 15%",
            inline=False
        )
        embed.add_field(
            name="🚨 **Alarm System** - $750",
            value="Reduces rob success by 20% + gives you compensation if robbed",
            inline=False
        )
        embed.add_field(
            name="🐕 **Guard Dog** - $1,000",
            value="Reduces rob success by 25% + 30% chance to counter-attack robber",
            inline=False
        )
        embed.add_field(
            name="🔓 **Lockpick** - $500",
            value="Increases YOUR rob success rate by 20%",
            inline=False
        )
        embed.add_field(
            name="🔄 **Reverse Rob Card** - $800",
            value="If robbed, automatically rob them back for 2x (one-time use)",
            inline=False
        )
        
        # Divider
        embed.add_field(name="\u200b", value="━━━━━━━━━━━━━━━━━━━━", inline=False)
        
        # Boost items
        embed.add_field(
            name="🍀 **Lucky Charm** - $1,000",
            value="2x gambling winnings for 1 hour",
            inline=False
        )
        embed.add_field(
            name="💼 **Briefcase** - $2,500",
            value="2x work earnings for 24 hours",
            inline=False
        )
        embed.add_field(
            name="⚡ **Energy Drink** - $1,500",
            value="Remove work cooldown for 2 hours",
            inline=False
        )
        embed.add_field(
            name="💎 **Diamond Multiplier** - $10,000",
            value="3x all earnings for 1 hour",
            inline=False
        )
        embed.add_field(
            name="🎲 **Loaded Dice** - $3,000",
            value="Better gambling odds for 3 hours",
            inline=False
        )
        
        # Divider
        embed.add_field(name="\u200b", value="━━━━━━━━━━━━━━━━━━━━", inline=False)
        
        # Special items
        embed.add_field(
            name="📈 **Stock Market Tip** - $2,500",
            value="⚠️ **RISKY!** Market can crash (lose all) or moon (up to $8k). 24hr cooldown.",
            inline=False
        )
        
        embed.add_field(
            name="💡 How to Buy",
            value="Use `/buy <item_name>` to purchase!\nExample: `/buy Padlock`\n\nBoost items go to `/inventory` - use them with `/use <item>`\nSecurity items work automatically when in your inventory!\n📈 Stock Market is HIGH RISK - you can lose everything!",
            inline=False
        )
        
        embed.set_footer(text="MegaBot Shop • Items stored in /inventory • Sell with /sell")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item="Item name to purchase")
    async def buy(self, interaction: discord.Interaction, item: str):
        """Purchase an item from the shop"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0
        balance = await self.bot.db.get_balance(user_id, guild_id)
        
        # Complete shop items database
        shop_items = {
            # Security items
            "padlock": {
                "price": 250,
                "emoji": "🔒",
                "type": "security",
                "description": "Reduces rob success rate by 15%"
            },
            "alarm system": {
                "price": 750,
                "emoji": "�",
                "type": "security",
                "description": "Reduces rob success by 20% + compensation if robbed"
            },
            "guard dog": {
                "price": 1000,
                "emoji": "🐕",
                "type": "security",
                "description": "Reduces rob success by 25% + 30% counter-attack chance"
            },
            "lockpick": {
                "price": 500,
                "emoji": "🔓",
                "type": "tool",
                "description": "Increases YOUR rob success rate by 20%"
            },
            "reverse rob card": {
                "price": 800,
                "emoji": "🔄",
                "type": "security",
                "description": "Automatically rob them back for 2x (one-time use)"
            },
            # Boost items
            "lucky charm": {
                "price": 1000, 
                "emoji": "🍀",
                "type": "consumable",
                "description": "2x gambling winnings for 1 hour"
            },
            "briefcase": {
                "price": 2500,
                "emoji": "�",
                "type": "consumable",
                "description": "2x work earnings for 24 hours"
            },
            "energy drink": {
                "price": 1500,
                "emoji": "⚡",
                "type": "consumable",
                "description": "Remove work cooldown for 2 hours"
            },
            "diamond multiplier": {
                "price": 10000,
                "emoji": "💎",
                "type": "consumable",
                "description": "3x all earnings for 1 hour"
            },
            "loaded dice": {
                "price": 3000,
                "emoji": "🎲",
                "type": "consumable",
                "description": "Better gambling odds for 3 hours"
            },
            # Special items
            "stock market tip": {
                "price": 2500,
                "emoji": "📈",
                "type": "special",
                "description": "⚠️ RISKY! Can crash (lose all) or moon ($6k-$8k). Avg: slight loss"
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
        await self.bot.db.update_balance(user_id, -price, guild_id)
        
        # Add all items to inventory (no more instant items)
        await self.bot.db.add_inventory_item(user_id, guild_id, item_lower, item_data["type"], 1)
        
        # Build embed
        new_balance = await self.bot.db.get_balance(user_id, guild_id)
        embed = discord.Embed(
            title=f"{Config.EMOJI_SUCCESS} Purchase Successful!",
            description=f"You bought **{item_data['emoji']} {item.title()}**!",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="💵 Price Paid", value=f"${price:,}", inline=True)
        embed.add_field(name="💰 New Balance", value=f"${new_balance:,}", inline=True)
        
        embed.add_field(
            name="📋 Description",
            value=item_data["description"],
            inline=False
        )
        
        # Instructions based on item type
        if item_data["type"] == "consumable":
            embed.add_field(
                name="💡 How to Use",
                value="Item added to your `/inventory`!\nActivate it with `/use " + item.title() + "`",
                inline=False
            )
        elif item_data["type"] in ["security", "tool"]:
            embed.add_field(
                name="💡 Auto-Active",
                value="Item added to your `/inventory`!\nIt works automatically - no need to activate!",
                inline=False
            )
        
        embed.set_footer(text="MegaBot Shop • Check /inventory to see your items")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
    logger.info("Economy cog loaded")
