"""
Study Commands Cog
Provides study tools like Pomodoro timers, homework tracking, quizzes, etc.
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
import random

class Study(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.homework = {}  # {user_id: [assignments]}
        self.pomodoro_sessions = {}  # {user_id: session_data}
        
    @app_commands.command(name="pomodoro", description="Start a Pomodoro timer")
    @app_commands.describe(
        work_minutes="Work duration (default: 25 minutes)",
        break_minutes="Break duration (default: 5 minutes)"
    )
    async def pomodoro(
        self, 
        interaction: discord.Interaction, 
        work_minutes: Optional[int] = 25,
        break_minutes: Optional[int] = 5
    ):
        """Start a Pomodoro study session"""
        if work_minutes < 1 or work_minutes > 60:
            await interaction.response.send_message("❌ Work time must be between 1-60 minutes!", ephemeral=True)
            return
        
        if break_minutes < 1 or break_minutes > 30:
            await interaction.response.send_message("❌ Break time must be between 1-30 minutes!", ephemeral=True)
            return
        
        user_id = interaction.user.id
        
        if user_id in self.pomodoro_sessions:
            await interaction.response.send_message("⚠️ You already have an active Pomodoro session!", ephemeral=True)
            return
        
        self.pomodoro_sessions[user_id] = True
        
        embed = discord.Embed(
            title="🍅 Pomodoro Timer Started!",
            description=f"**Focus time:** {work_minutes} minutes\n**Break time:** {break_minutes} minutes",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="💪 Stay Focused!", value="I'll notify you when it's break time!")
        embed.set_footer(text=f"Started by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        
        # Work phase
        await asyncio.sleep(work_minutes * 60)
        
        if user_id not in self.pomodoro_sessions:
            return  # User stopped the timer
        
        # Break notification
        embed = discord.Embed(
            title="🎉 Break Time!",
            description=f"Great work! Take a {break_minutes} minute break.",
            color=discord.Color.green()
        )
        embed.add_field(name="💧 Drink water", value="Stay hydrated!")
        embed.add_field(name="🧘 Stretch", value="Move your body!")
        
        await interaction.channel.send(content=interaction.user.mention, embed=embed)
        
        # Break phase
        await asyncio.sleep(break_minutes * 60)
        
        if user_id in self.pomodoro_sessions:
            # End notification
            embed = discord.Embed(
                title="✅ Pomodoro Complete!",
                description="Ready for another session?",
                color=discord.Color.blue()
            )
            
            await interaction.channel.send(content=interaction.user.mention, embed=embed)
            del self.pomodoro_sessions[user_id]
    
    @app_commands.command(name="stoppomodoro", description="Stop your active Pomodoro timer")
    async def stoppomodoro(self, interaction: discord.Interaction):
        """Stop the active Pomodoro session"""
        user_id = interaction.user.id
        
        if user_id in self.pomodoro_sessions:
            del self.pomodoro_sessions[user_id]
            await interaction.response.send_message("⏹️ Pomodoro timer stopped!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No active Pomodoro session!", ephemeral=True)
    
    @app_commands.command(name="homework", description="Add homework assignment")
    @app_commands.describe(
        subject="Subject/Class name",
        assignment="Assignment description",
        due_date="Due date (YYYY-MM-DD)"
    )
    async def homework_add(
        self, 
        interaction: discord.Interaction, 
        subject: str, 
        assignment: str,
        due_date: str
    ):
        """Add a homework assignment"""
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message("❌ Invalid date format! Use YYYY-MM-DD", ephemeral=True)
            return
        
        user_id = interaction.user.id
        
        if user_id not in self.homework:
            self.homework[user_id] = []
        
        hw_item = {
            'subject': subject,
            'assignment': assignment,
            'due_date': due,
            'completed': False,
            'id': len(self.homework[user_id]) + 1
        }
        
        self.homework[user_id].append(hw_item)
        
        embed = discord.Embed(
            title="✅ Homework Added!",
            description=f"**{subject}**\n{assignment}",
            color=discord.Color.green()
        )
        embed.add_field(name="📅 Due", value=due.strftime("%B %d, %Y"))
        embed.add_field(name="🆔 ID", value=hw_item['id'])
        
        days_until = (due.date() - datetime.now().date()).days
        if days_until < 0:
            embed.add_field(name="⚠️", value="Already overdue!")
        elif days_until == 0:
            embed.add_field(name="⚡", value="Due today!")
        elif days_until <= 3:
            embed.add_field(name="⏰", value=f"Due in {days_until} days!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="homeworklist", description="View your homework list")
    async def homework_list(self, interaction: discord.Interaction):
        """View all homework assignments"""
        user_id = interaction.user.id
        
        if user_id not in self.homework or not self.homework[user_id]:
            await interaction.response.send_message("📚 No homework assignments! You're all caught up!", ephemeral=True)
            return
        
        # Sort by due date
        assignments = sorted(self.homework[user_id], key=lambda x: x['due_date'])
        
        embed = discord.Embed(
            title="📚 Your Homework List",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        for hw in assignments:
            if hw['completed']:
                status = "✅"
            else:
                days_until = (hw['due_date'].date() - datetime.now().date()).days
                if days_until < 0:
                    status = "🔴 OVERDUE"
                elif days_until == 0:
                    status = "🟡 DUE TODAY"
                elif days_until <= 3:
                    status = f"🟠 {days_until}d"
                else:
                    status = f"🟢 {days_until}d"
            
            embed.add_field(
                name=f"{status} {hw['subject']} (ID: {hw['id']})",
                value=f"{hw['assignment']}\n📅 Due: {hw['due_date'].strftime('%Y-%m-%d')}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="homeworkdone", description="Mark homework as complete")
    @app_commands.describe(homework_id="Homework ID")
    async def homework_complete(self, interaction: discord.Interaction, homework_id: int):
        """Mark homework as completed"""
        user_id = interaction.user.id
        
        if user_id not in self.homework:
            await interaction.response.send_message("❌ No homework found!", ephemeral=True)
            return
        
        hw = next((h for h in self.homework[user_id] if h['id'] == homework_id), None)
        
        if not hw:
            await interaction.response.send_message(f"❌ Homework with ID {homework_id} not found!", ephemeral=True)
            return
        
        hw['completed'] = True
        
        embed = discord.Embed(
            title="🎉 Homework Complete!",
            description=f"**{hw['subject']}**\n{hw['assignment']}",
            color=discord.Color.green()
        )
        embed.set_footer(text="Great job! Keep it up! 💪")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="homeworkdelete", description="Delete homework assignment")
    @app_commands.describe(homework_id="Homework ID")
    async def homework_delete(self, interaction: discord.Interaction, homework_id: int):
        """Delete a homework assignment"""
        user_id = interaction.user.id
        
        if user_id not in self.homework:
            await interaction.response.send_message("❌ No homework found!", ephemeral=True)
            return
        
        initial_count = len(self.homework[user_id])
        self.homework[user_id] = [h for h in self.homework[user_id] if h['id'] != homework_id]
        
        if len(self.homework[user_id]) == initial_count:
            await interaction.response.send_message(f"❌ Homework with ID {homework_id} not found!", ephemeral=True)
            return
        
        await interaction.response.send_message(f"🗑️ Homework assignment {homework_id} deleted!", ephemeral=True)
    
    @app_commands.command(name="quiz", description="Take a quick quiz")
    @app_commands.describe(
        subject="Quiz subject (math, science, history, geography)",
        difficulty="Difficulty level (easy, medium, hard)"
    )
    async def quiz(
        self, 
        interaction: discord.Interaction, 
        subject: str,
        difficulty: Optional[str] = "medium"
    ):
        """Take a randomized quiz"""
        # Sample quiz questions
        quizzes = {
            'math': {
                'easy': [
                    ('What is 5 + 7?', '12'),
                    ('What is 3 × 4?', '12'),
                    ('What is 20 ÷ 4?', '5'),
                ],
                'medium': [
                    ('What is 15% of 200?', '30'),
                    ('What is the square root of 144?', '12'),
                    ('What is 8²?', '64'),
                ],
                'hard': [
                    ('What is the derivative of x²?', '2x'),
                    ('What is π rounded to 2 decimals?', '3.14'),
                    ('What is the integral of 1/x?', 'ln(x)'),
                ]
            },
            'science': {
                'easy': [
                    ('What planet is closest to the sun?', 'Mercury'),
                    ('What is H2O?', 'Water'),
                    ('How many legs does a spider have?', '8'),
                ],
                'medium': [
                    ('What is the powerhouse of the cell?', 'Mitochondria'),
                    ('What is the chemical symbol for gold?', 'Au'),
                    ('What is the speed of light in km/s?', '300000'),
                ],
                'hard': [
                    ('What is the atomic number of Carbon?', '6'),
                    ('What is Newton\'s second law? (F=?)', 'ma'),
                    ('What is the study of fungi called?', 'Mycology'),
                ]
            }
        }
        
        if subject.lower() not in quizzes:
            await interaction.response.send_message(
                f"❌ Subject not found! Available: {', '.join(quizzes.keys())}", 
                ephemeral=True
            )
            return
        
        if difficulty.lower() not in ['easy', 'medium', 'hard']:
            difficulty = 'medium'
        
        question, answer = random.choice(quizzes[subject.lower()][difficulty.lower()])
        
        embed = discord.Embed(
            title=f"📝 {subject.title()} Quiz ({difficulty.title()})",
            description=f"**Question:**\n{question}",
            color=discord.Color.purple()
        )
        embed.add_field(name="💡 Tip", value="Reply with your answer in the next 30 seconds!")
        embed.set_footer(text="Type your answer in chat")
        
        await interaction.response.send_message(embed=embed)
        
        def check(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
        
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            
            if msg.content.lower().strip() == answer.lower().strip():
                embed = discord.Embed(
                    title="✅ Correct!",
                    description=f"The answer is **{answer}**",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Great job! 🎉")
            else:
                embed = discord.Embed(
                    title="❌ Incorrect",
                    description=f"The correct answer is **{answer}**\nYou answered: {msg.content}",
                    color=discord.Color.red()
                )
                embed.set_footer(text="Better luck next time!")
            
            await interaction.channel.send(embed=embed)
            
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ Time's Up!",
                description=f"The correct answer was **{answer}**",
                color=discord.Color.orange()
            )
            await interaction.channel.send(embed=embed)
    
    @app_commands.command(name="flashcard", description="Study with flashcards")
    @app_commands.describe(
        front="Front of the card (question/term)",
        back="Back of the card (answer/definition)"
    )
    async def flashcard(self, interaction: discord.Interaction, front: str, back: str):
        """Create a flashcard for studying"""
        embed = discord.Embed(
            title="📇 Flashcard",
            description="React with 🔄 to flip the card!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Question", value=front, inline=False)
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🔄")
        
        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) == "🔄"
        
        try:
            await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            
            embed = discord.Embed(
                title="📇 Flashcard (Flipped)",
                color=discord.Color.green()
            )
            embed.add_field(name="Question", value=front, inline=False)
            embed.add_field(name="Answer", value=back, inline=False)
            
            await message.edit(embed=embed)
        except asyncio.TimeoutError:
            pass

async def setup(bot):
    await bot.add_cog(Study(bot))
