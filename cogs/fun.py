"""
Fun Commands Cog
Provides entertainment commands like trivia, jokes, memes, etc.
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import random
from typing import Optional

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_sessions = {}  # Active trivia games
        
    @app_commands.command(name="joke", description="Get a random joke")
    async def joke(self, interaction: discord.Interaction):
        """Fetch a random joke from API"""
        await interaction.response.defer()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://official-joke-api.appspot.com/random_joke") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        embed = discord.Embed(
                            title="😄 Random Joke",
                            description=data['setup'],
                            color=discord.Color.gold()
                        )
                        embed.add_field(name="Punchline", value=f"||{data['punchline']}||")
                        embed.set_footer(text="Click the spoiler to reveal!")
                        
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ Couldn't fetch a joke!")
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")
    
    @app_commands.command(name="meme", description="Get a random meme")
    async def meme(self, interaction: discord.Interaction):
        """Fetch a random meme from Reddit"""
        await interaction.response.defer()
        
        try:
            # Popular meme subreddits
            subreddits = ['memes', 'dankmemes', 'wholesomememes', 'me_irl']
            subreddit = random.choice(subreddits)
            
            async with aiohttp.ClientSession() as session:
                url = f"https://www.reddit.com/r/{subreddit}/random.json"
                headers = {'User-Agent': 'Discord Bot'}
                
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        post = data[0]['data']['children'][0]['data']
                        
                        embed = discord.Embed(
                            title=post['title'],
                            color=discord.Color.orange()
                        )
                        embed.set_image(url=post['url'])
                        embed.set_footer(text=f"👍 {post['ups']} upvotes | r/{subreddit}")
                        
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ Couldn't fetch a meme!")
        except Exception as e:
            await interaction.followup.send(f"❌ Error fetching meme: {str(e)}")
    
    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    @app_commands.describe(question="Your yes/no question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        """Magic 8-ball responses"""
        responses = [
            "🔮 It is certain.",
            "🔮 It is decidedly so.",
            "🔮 Without a doubt.",
            "🔮 Yes - definitely.",
            "🔮 You may rely on it.",
            "🔮 As I see it, yes.",
            "🔮 Most likely.",
            "🔮 Outlook good.",
            "🔮 Yes.",
            "🔮 Signs point to yes.",
            "🤔 Reply hazy, try again.",
            "🤔 Ask again later.",
            "🤔 Better not tell you now.",
            "🤔 Cannot predict now.",
            "🤔 Concentrate and ask again.",
            "❌ Don't count on it.",
            "❌ My reply is no.",
            "❌ My sources say no.",
            "❌ Outlook not so good.",
            "❌ Very doubtful."
        ]
        
        answer = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.purple()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=answer, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="trivia", description="Start a trivia game")
    @app_commands.describe(
        category="Trivia category (general, science, history, geography, sports)",
        difficulty="Difficulty (easy, medium, hard)"
    )
    async def trivia(
        self, 
        interaction: discord.Interaction, 
        category: Optional[str] = "general",
        difficulty: Optional[str] = "medium"
    ):
        """Start a trivia game"""
        await interaction.response.defer()
        
        # Category mapping for OpenTDB API
        categories = {
            'general': 9,
            'science': 17,
            'history': 23,
            'geography': 22,
            'sports': 21
        }
        
        category_id = categories.get(category.lower(), 9)
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://opentdb.com/api.php?amount=1&category={category_id}&difficulty={difficulty.lower()}&type=multiple"
                
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if data['response_code'] != 0:
                            await interaction.followup.send("❌ No trivia questions available!")
                            return
                        
                        question_data = data['results'][0]
                        question = question_data['question']
                        correct_answer = question_data['correct_answer']
                        all_answers = question_data['incorrect_answers'] + [correct_answer]
                        random.shuffle(all_answers)
                        
                        # Format with emojis
                        emojis = ['🅰️', '🅱️', '©️', '🅳']
                        options = "\n".join([f"{emojis[i]} {ans}" for i, ans in enumerate(all_answers)])
                        
                        embed = discord.Embed(
                            title=f"🎯 Trivia - {category.title()} ({difficulty.title()})",
                            description=f"**{question}**\n\n{options}",
                            color=discord.Color.blue()
                        )
                        embed.set_footer(text="You have 30 seconds to answer! Type A, B, C, or D")
                        
                        await interaction.followup.send(embed=embed)
                        
                        # Store correct answer
                        correct_letter = ['A', 'B', 'C', 'D'][all_answers.index(correct_answer)]
                        
                        def check(m):
                            return (m.author.id == interaction.user.id and 
                                   m.channel.id == interaction.channel.id and 
                                   m.content.upper() in ['A', 'B', 'C', 'D'])
                        
                        try:
                            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
                            
                            if msg.content.upper() == correct_letter:
                                embed = discord.Embed(
                                    title="✅ Correct!",
                                    description=f"The answer is **{correct_letter}: {correct_answer}**",
                                    color=discord.Color.green()
                                )
                                embed.set_footer(text="🎉 Great job!")
                            else:
                                user_answer_idx = ord(msg.content.upper()) - ord('A')
                                embed = discord.Embed(
                                    title="❌ Incorrect!",
                                    description=f"You answered: **{msg.content.upper()}: {all_answers[user_answer_idx]}**\n\nCorrect answer: **{correct_letter}: {correct_answer}**",
                                    color=discord.Color.red()
                                )
                                embed.set_footer(text="Better luck next time!")
                            
                            await interaction.channel.send(embed=embed)
                            
                        except Exception:
                            embed = discord.Embed(
                                title="⏰ Time's Up!",
                                description=f"The correct answer was **{correct_letter}: {correct_answer}**",
                                color=discord.Color.orange()
                            )
                            await interaction.channel.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ Error fetching trivia question!")
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")
    
    @app_commands.command(name="flip", description="Flip a coin")
    async def flip(self, interaction: discord.Interaction):
        """Flip a coin"""
        result = random.choice(['Heads', 'Tails'])
        emoji = '🪙' if result == 'Heads' else '💿'
        
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"{emoji} **{result}**!",
            color=discord.Color.gold()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roll", description="Roll dice")
    @app_commands.describe(
        dice="Dice notation (e.g., 2d6 for 2 six-sided dice)"
    )
    async def roll(self, interaction: discord.Interaction, dice: str):
        """Roll dice in DnD notation"""
        try:
            # Parse dice notation (e.g., "2d6", "1d20")
            parts = dice.lower().split('d')
            if len(parts) != 2:
                await interaction.response.send_message("❌ Use format: XdY (e.g., 2d6)", ephemeral=True)
                return
            
            num_dice = int(parts[0])
            num_sides = int(parts[1])
            
            if num_dice < 1 or num_dice > 100:
                await interaction.response.send_message("❌ Number of dice must be 1-100!", ephemeral=True)
                return
            
            if num_sides < 2 or num_sides > 1000:
                await interaction.response.send_message("❌ Number of sides must be 2-1000!", ephemeral=True)
                return
            
            rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
            total = sum(rolls)
            
            embed = discord.Embed(
                title=f"🎲 Rolling {dice}",
                color=discord.Color.purple()
            )
            
            if num_dice <= 20:
                embed.add_field(name="Rolls", value=", ".join(map(str, rolls)), inline=False)
            
            embed.add_field(name="Total", value=f"**{total}**", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid dice format! Use: XdY (e.g., 2d6)", ephemeral=True)
    
    @app_commands.command(name="choose", description="Let the bot choose for you")
    @app_commands.describe(choices="Comma-separated choices")
    async def choose(self, interaction: discord.Interaction, choices: str):
        """Choose randomly from options"""
        options = [opt.strip() for opt in choices.split(',')]
        
        if len(options) < 2:
            await interaction.response.send_message("❌ Provide at least 2 choices separated by commas!", ephemeral=True)
            return
        
        choice = random.choice(options)
        
        embed = discord.Embed(
            title="🎯 Random Choice",
            description=f"I choose: **{choice}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="Options", value=", ".join(options))
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="fortune", description="Get your fortune told")
    async def fortune(self, interaction: discord.Interaction):
        """Get a random fortune"""
        fortunes = [
            "🔮 A pleasant surprise is waiting for you.",
            "🔮 Your hard work will soon pay off.",
            "🔮 An exciting opportunity is on the horizon.",
            "🔮 Someone is thinking of you right now.",
            "🔮 Your creativity will shine today.",
            "🔮 Good news is coming your way.",
            "🔮 A new friendship will brighten your day.",
            "🔮 Trust your instincts today.",
            "🔮 Adventure awaits you soon.",
            "🔮 Your patience will be rewarded.",
            "🔮 Today is a great day to start something new.",
            "🔮 Happiness is just around the corner.",
            "🔮 Your kindness will be remembered.",
            "🔮 Success is in your future.",
            "🔮 A dream you have will come true."
        ]
        
        fortune = random.choice(fortunes)
        
        embed = discord.Embed(
            title="🔮 Your Fortune",
            description=fortune,
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Fortune for {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rate", description="Rate something out of 10")
    @app_commands.describe(thing="What to rate")
    async def rate(self, interaction: discord.Interaction, thing: str):
        """Rate anything on a scale of 1-10"""
        rating = random.randint(1, 10)
        
        if rating <= 3:
            emoji = "😬"
            comment = "Not great..."
        elif rating <= 5:
            emoji = "😐"
            comment = "It's okay"
        elif rating <= 7:
            emoji = "😊"
            comment = "Pretty good!"
        elif rating <= 9:
            emoji = "😍"
            comment = "Amazing!"
        else:
            emoji = "🤩"
            comment = "PERFECT!"
        
        embed = discord.Embed(
            title="⭐ Rating",
            description=f"**{thing}**",
            color=discord.Color.gold()
        )
        embed.add_field(name="Score", value=f"{emoji} **{rating}/10** - {comment}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
