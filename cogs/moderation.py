"""
Moderation Commands Cog
Provides server moderation and management features
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import random
from typing import Optional

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channels = {}  # {guild_id: channel_id}
        self.auto_roles = {}  # {guild_id: [role_ids]}
        self.giveaways = {}  # Active giveaways
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Welcome new members"""
        guild_id = member.guild.id
        
        # Send welcome message
        if guild_id in self.welcome_channels:
            channel = self.bot.get_channel(self.welcome_channels[guild_id])
            if channel:
                embed = discord.Embed(
                    title="👋 Welcome!",
                    description=f"Welcome to **{member.guild.name}**, {member.mention}!",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name="Member Count", value=f"You are member #{member.guild.member_count}")
                embed.set_footer(text=f"ID: {member.id}")
                
                await channel.send(embed=embed)
        
        # Auto-assign roles
        if guild_id in self.auto_roles:
            roles = [member.guild.get_role(role_id) for role_id in self.auto_roles[guild_id]]
            roles = [r for r in roles if r is not None]
            
            if roles:
                try:
                    await member.add_roles(*roles, reason="Auto-role on join")
                except discord.Forbidden:
                    pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Goodbye message"""
        guild_id = member.guild.id
        
        if guild_id in self.welcome_channels:
            channel = self.bot.get_channel(self.welcome_channels[guild_id])
            if channel:
                embed = discord.Embed(
                    title="👋 Goodbye",
                    description=f"**{member.name}** has left the server.",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                
                await channel.send(embed=embed)
    
    @app_commands.command(name="setwelcome", description="Set welcome channel")
    @app_commands.describe(channel="Channel for welcome messages")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the welcome channel for new members"""
        self.welcome_channels[interaction.guild.id] = channel.id
        
        embed = discord.Embed(
            title="✅ Welcome Channel Set!",
            description=f"New members will be welcomed in {channel.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setautorole", description="Set auto-role for new members")
    @app_commands.describe(role="Role to auto-assign")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_autorole(self, interaction: discord.Interaction, role: discord.Role):
        """Set a role to be automatically assigned to new members"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.auto_roles:
            self.auto_roles[guild_id] = []
        
        if role.id in self.auto_roles[guild_id]:
            await interaction.response.send_message(f"❌ {role.mention} is already an auto-role!", ephemeral=True)
            return
        
        self.auto_roles[guild_id].append(role.id)
        
        embed = discord.Embed(
            title="✅ Auto-Role Added!",
            description=f"New members will automatically receive {role.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="removeautorole", description="Remove auto-role")
    @app_commands.describe(role="Role to remove from auto-assign")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_autorole(self, interaction: discord.Interaction, role: discord.Role):
        """Remove a role from auto-assignment"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.auto_roles or role.id not in self.auto_roles[guild_id]:
            await interaction.response.send_message(f"❌ {role.mention} is not an auto-role!", ephemeral=True)
            return
        
        self.auto_roles[guild_id].remove(role.id)
        
        embed = discord.Embed(
            title="✅ Auto-Role Removed!",
            description=f"{role.mention} will no longer be auto-assigned",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="giveaway", description="Start a giveaway")
    @app_commands.describe(
        duration="Duration in minutes",
        winners="Number of winners",
        prize="What you're giving away"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway(
        self, 
        interaction: discord.Interaction, 
        duration: int, 
        winners: int,
        prize: str
    ):
        """Start a giveaway"""
        if duration < 1 or duration > 10080:  # Max 1 week
            await interaction.response.send_message("❌ Duration must be 1 minute - 1 week!", ephemeral=True)
            return
        
        if winners < 1 or winners > 20:
            await interaction.response.send_message("❌ Winners must be 1-20!", ephemeral=True)
            return
        
        end_time = datetime.utcnow() + timedelta(minutes=duration)
        
        embed = discord.Embed(
            title="🎉 GIVEAWAY! 🎉",
            description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** <t:{int(end_time.timestamp())}:R>",
            color=discord.Color.gold(),
            timestamp=end_time
        )
        embed.add_field(name="How to Enter", value="React with 🎉 to enter!")
        embed.set_footer(text=f"Hosted by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🎉")
        
        # Store giveaway data
        self.giveaways[message.id] = {
            'prize': prize,
            'winners': winners,
            'end_time': end_time,
            'host': interaction.user.id,
            'channel': interaction.channel.id
        }
        
        # Schedule giveaway end
        self.bot.loop.create_task(self.end_giveaway(message.id, duration))
    
    async def end_giveaway(self, message_id, duration):
        """End a giveaway and pick winners"""
        await self.bot.wait_until_ready()
        await asyncio.sleep(duration * 60)
        
        if message_id not in self.giveaways:
            return
        
        giveaway = self.giveaways[message_id]
        channel = self.bot.get_channel(giveaway['channel'])
        
        if not channel:
            del self.giveaways[message_id]
            return
        
        try:
            message = await channel.fetch_message(message_id)
            
            # Get users who reacted
            reaction = discord.utils.get(message.reactions, emoji="🎉")
            if not reaction:
                await channel.send("❌ No one entered the giveaway!")
                del self.giveaways[message_id]
                return
            
            users = [user async for user in reaction.users() if not user.bot]
            
            if len(users) == 0:
                await channel.send("❌ No valid entries for the giveaway!")
                del self.giveaways[message_id]
                return
            
            # Pick winners
            num_winners = min(giveaway['winners'], len(users))
            winners = random.sample(users, num_winners)
            
            embed = discord.Embed(
                title="🎉 Giveaway Ended! 🎉",
                description=f"**Prize:** {giveaway['prize']}",
                color=discord.Color.green()
            )
            
            winner_mentions = ", ".join([w.mention for w in winners])
            embed.add_field(name="🏆 Winner(s)", value=winner_mentions)
            
            await channel.send(content=winner_mentions, embed=embed)
            
            del self.giveaways[message_id]
            
        except Exception as e:
            print(f"Error ending giveaway: {e}")
            del self.giveaways[message_id]
    
    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.describe(
        member="Member to kick",
        reason="Reason for kick"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        reason: Optional[str] = "No reason provided"
    ):
        """Kick a member from the server"""
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You can't kick this member (role hierarchy)!", ephemeral=True)
            return
        
        try:
            await member.kick(reason=f"{interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**{member}** has been kicked",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick this member!", ephemeral=True)
    
    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.describe(
        member="Member to ban",
        reason="Reason for ban"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        reason: Optional[str] = "No reason provided"
    ):
        """Ban a member from the server"""
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You can't ban this member (role hierarchy)!", ephemeral=True)
            return
        
        try:
            await member.ban(reason=f"{interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**{member}** has been banned",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=interaction.user.mention)
            
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to ban this member!", ephemeral=True)
    
    @app_commands.command(name="clear", description="Clear messages")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        """Bulk delete messages"""
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Amount must be 1-100!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"🗑️ Deleted {len(deleted)} messages!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages!", ephemeral=True)
    
    @app_commands.command(name="slowmode", description="Set channel slowmode")
    @app_commands.describe(seconds="Slowmode delay in seconds (0 to disable)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        """Set slowmode for the channel"""
        if seconds < 0 or seconds > 21600:
            await interaction.response.send_message("❌ Slowmode must be 0-21600 seconds!", ephemeral=True)
            return
        
        try:
            await interaction.channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                await interaction.response.send_message("✅ Slowmode disabled!")
            else:
                await interaction.response.send_message(f"✅ Slowmode set to {seconds} seconds!")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to edit this channel!", ephemeral=True)
    
    @app_commands.command(name="mute", description="Mute a member")
    @app_commands.describe(
        member="Member to mute",
        duration="Duration in minutes",
        reason="Reason for mute"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        duration: int,
        reason: Optional[str] = "No reason provided"
    ):
        """Timeout a member for a specified duration"""
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You can't mute this member (role hierarchy)!", ephemeral=True)
            return
        
        if duration < 1 or duration > 40320:  # Max 28 days
            await interaction.response.send_message("❌ Duration must be 1 minute - 28 days!", ephemeral=True)
            return
        
        try:
            timeout_until = datetime.utcnow() + timedelta(minutes=duration)
            await member.timeout(timeout_until, reason=f"{interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"**{member}** has been muted",
                color=discord.Color.orange()
            )
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
            embed.add_field(name="Expires", value=f"<t:{int(timeout_until.timestamp())}:R>", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to mute this member!", ephemeral=True)
    
    @app_commands.command(name="unmute", description="Unmute a member")
    @app_commands.describe(
        member="Member to unmute",
        reason="Reason for unmute"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        reason: Optional[str] = "No reason provided"
    ):
        """Remove timeout from a member"""
        try:
            await member.timeout(None, reason=f"{interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"**{member}** has been unmuted",
                color=discord.Color.green()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to unmute this member!", ephemeral=True)
    
    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(
        member="Member to warn",
        reason="Reason for warning"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member,
        reason: str
    ):
        """Issue a warning to a member"""
        if member.bot:
            await interaction.response.send_message("❌ You can't warn bots!", ephemeral=True)
            return
        
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ You can't warn this member (role hierarchy)!", ephemeral=True)
            return
        
        # Save warning to database
        await self.bot.db.add_warning(member.id, interaction.user.id, reason)
        warning_count = await self.bot.db.get_warning_count(member.id)
        
        # Public warning embed
        embed = discord.Embed(
            title="⚠️ Member Warned",
            description=f"**{member}** has received a warning (Total: {warning_count})",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"Member ID: {member.id}")
        
        await interaction.response.send_message(embed=embed)
        
        # Try to DM the member
        try:
            dm_embed = discord.Embed(
                title=f"⚠️ Warning from {interaction.guild.name}",
                description=f"You have been warned by {interaction.user}",
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(
                name="What does this mean?",
                value="This is a formal warning. Repeated violations may result in mute, kick, or ban.",
                inline=False
            )
            dm_embed.set_footer(text=f"Server: {interaction.guild.name}")
            
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            # User has DMs disabled
            pass

import asyncio

async def setup(bot):
    await bot.add_cog(Moderation(bot))
