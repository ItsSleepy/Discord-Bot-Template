"""
Utility Commands Cog
Provides useful utility commands like polls, reminders, weather, etc.
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
from datetime import datetime, timedelta
import asyncio
from typing import Optional
import json

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()
        
    def cog_unload(self):
        self.check_reminders.cancel()
    
    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.describe(
        question="The poll question",
        options="Comma-separated options (up to 10)"
    )
    async def poll(self, interaction: discord.Interaction, question: str, options: str):
        """Create a poll with multiple options"""
        option_list = [opt.strip() for opt in options.split(',')][:10]
        
        if len(option_list) < 2:
            await interaction.response.send_message("❌ You need at least 2 options!", ephemeral=True)
            return
        
        # Emoji numbers
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        description = "\n\n".join([f"{emojis[i]} {opt}" for i, opt in enumerate(option_list)])
        
        embed = discord.Embed(
            title=f"📊 {question}",
            description=description,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Poll by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        
        message = await interaction.original_response()
        for i in range(len(option_list)):
            await message.add_reaction(emojis[i])
    
    @app_commands.command(name="remind", description="Set a reminder")
    @app_commands.describe(
        time="Time in minutes",
        message="Reminder message"
    )
    async def remind(self, interaction: discord.Interaction, time: int, message: str):
        """Set a reminder for yourself"""
        if time <= 0 or time > 10080:  # Max 1 week
            await interaction.response.send_message("❌ Time must be between 1 minute and 1 week!", ephemeral=True)
            return
        
        remind_time = datetime.utcnow() + timedelta(minutes=time)
        
        # Save reminder to database
        await self.bot.db.add_reminder(
            interaction.user.id,
            interaction.channel.id,
            message,
            remind_time
        )
        
        embed = discord.Embed(
            title="⏰ Reminder Set!",
            description=f"I'll remind you in **{time} minutes**:\n```{message}```",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @tasks.loop(seconds=30)
    async def check_reminders(self):
        """Check and send due reminders"""
        # Get due reminders from database
        due_reminders = await self.bot.db.get_due_reminders()
        
        for reminder in due_reminders:
            reminder_id, user_id, channel_id, message = reminder
            try:
                channel = self.bot.get_channel(channel_id)
                user = self.bot.get_user(user_id)
                
                if channel and user:
                    embed = discord.Embed(
                        title="⏰ Reminder!",
                        description=f"**{user.mention}**, you asked me to remind you:\n```{message}```",
                        color=discord.Color.gold()
                    )
                    await channel.send(embed=embed)
                
                # Remove sent reminder from database
                await self.bot.db.remove_reminder(reminder_id)
            except Exception as e:
                print(f"Error sending reminder: {e}")
                # Remove failed reminder from database
                await self.bot.db.remove_reminder(reminder_id)
    
    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()
    
    @app_commands.command(name="translate", description="Translate text")
    @app_commands.describe(
        text="Text to translate",
        target_language="Target language code (e.g., es, fr, de)"
    )
    async def translate(self, interaction: discord.Interaction, text: str, target_language: str):
        """Translate text using a free API"""
        await interaction.response.defer()
        
        try:
            # Using LibreTranslate (free, open source)
            async with aiohttp.ClientSession() as session:
                url = "https://libretranslate.com/translate"
                data = {
                    'q': text,
                    'source': 'auto',
                    'target': target_language.lower(),
                    'format': 'text'
                }
                
                async with session.post(url, json=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        translated = result['translatedText']
                        
                        embed = discord.Embed(
                            title="🌍 Translation",
                            color=discord.Color.blue()
                        )
                        embed.add_field(name="Original", value=text, inline=False)
                        embed.add_field(name=f"Translated ({target_language.upper()})", value=translated, inline=False)
                        
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ Translation failed. Check language code!")
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")
    
    @app_commands.command(name="calculate", description="Perform calculations")
    @app_commands.describe(expression="Mathematical expression (e.g., 2+2, 5*10)")
    async def calculate(self, interaction: discord.Interaction, expression: str):
        """Safe calculator"""
        # Remove dangerous characters
        safe_expr = ''.join(c for c in expression if c in '0123456789+-*/().^ ')
        safe_expr = safe_expr.replace('^', '**')
        
        try:
            result = eval(safe_expr, {"__builtins__": {}}, {})
            
            embed = discord.Embed(
                title="🧮 Calculator",
                color=discord.Color.blue()
            )
            embed.add_field(name="Expression", value=f"`{expression}`", inline=False)
            embed.add_field(name="Result", value=f"```{result}```", inline=False)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Invalid expression: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="userinfo", description="Get information about a user")
    @app_commands.describe(user="User to get info about (leave empty for yourself)")
    async def userinfo(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Display information about a user"""
        user = user or interaction.user
        
        embed = discord.Embed(
            title=f"👤 User Information",
            color=user.color
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="Display Name", value=user.display_name, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "N/A", inline=True)
        
        roles = [role.mention for role in user.roles[1:]]  # Skip @everyone
        embed.add_field(name=f"Roles [{len(roles)}]", value=", ".join(roles) if roles else "No roles", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="serverinfo", description="Get server information")
    async def serverinfo(self, interaction: discord.Interaction):
        """Display server information"""
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"🏰 {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        
        embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        embed.add_field(name="Boost Level", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="avatar", description="Get user's avatar")
    @app_commands.describe(user="User to get avatar from (leave empty for yourself)")
    async def avatar(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Display user's avatar in high quality"""
        user = user or interaction.user
        
        embed = discord.Embed(
            title=f"🖼️ {user.display_name}'s Avatar",
            color=discord.Color.blue()
        )
        
        avatar_url = user.display_avatar.url
        embed.set_image(url=avatar_url)
        embed.add_field(name="Download", value=f"[Click here]({avatar_url})")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
