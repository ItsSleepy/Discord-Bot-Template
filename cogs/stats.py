"""
Stats Commands Cog
Provides server statistics and analytics
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from collections import Counter
from typing import Optional

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_counts = {}  # {guild_id: {user_id: count}}
        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Track message statistics"""
        if message.author.bot or not message.guild:
            return
        
        guild_id = message.guild.id
        user_id = message.author.id
        
        if guild_id not in self.message_counts:
            self.message_counts[guild_id] = {}
        
        if user_id not in self.message_counts[guild_id]:
            self.message_counts[guild_id][user_id] = 0
        
        self.message_counts[guild_id][user_id] += 1
    
    @app_commands.command(name="serverstats", description="View server statistics")
    async def serverstats(self, interaction: discord.Interaction):
        """Display comprehensive server statistics"""
        guild = interaction.guild
        
        # Member statistics
        total_members = guild.member_count
        human_members = len([m for m in guild.members if not m.bot])
        bot_members = total_members - human_members
        
        # Online status
        online = len([m for m in guild.members if m.status != discord.Status.offline])
        
        # Channel statistics
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Role statistics
        total_roles = len(guild.roles)
        
        # Boost statistics
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        
        embed = discord.Embed(
            title=f"📊 Server Statistics - {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Members
        embed.add_field(
            name="👥 Members",
            value=f"Total: **{total_members}**\nHumans: **{human_members}**\nBots: **{bot_members}**\nOnline: **{online}**",
            inline=True
        )
        
        # Channels
        embed.add_field(
            name="💬 Channels",
            value=f"Text: **{text_channels}**\nVoice: **{voice_channels}**\nCategories: **{categories}**",
            inline=True
        )
        
        # Server Info
        embed.add_field(
            name="🏰 Server Info",
            value=f"Owner: {guild.owner.mention}\nCreated: <t:{int(guild.created_at.timestamp())}:R>\nRoles: **{total_roles}**",
            inline=True
        )
        
        # Boosts
        embed.add_field(
            name="🚀 Boosts",
            value=f"Level: **{boost_level}**\nBoosts: **{boost_count}**",
            inline=True
        )
        
        # Emojis
        embed.add_field(
            name="😀 Emojis",
            value=f"Total: **{len(guild.emojis)}**",
            inline=True
        )
        
        # Verification
        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest"
        }
        
        embed.add_field(
            name="🔒 Security",
            value=f"Verification: **{verification_levels[guild.verification_level]}**",
            inline=True
        )
        
        embed.set_footer(text=f"Server ID: {guild.id}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="channelstats", description="View channel statistics")
    @app_commands.describe(channel="Channel to view stats for (defaults to current)")
    async def channelstats(
        self, 
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None
    ):
        """Display channel statistics"""
        channel = channel or interaction.channel
        
        embed = discord.Embed(
            title=f"📊 Channel Statistics - #{channel.name}",
            color=discord.Color.blue()
        )
        
        # Basic info
        embed.add_field(name="📝 Name", value=channel.name, inline=True)
        embed.add_field(name="🆔 ID", value=channel.id, inline=True)
        embed.add_field(name="📅 Created", value=channel.created_at.strftime("%Y-%m-%d"), inline=True)
        
        # Topic
        if channel.topic:
            embed.add_field(name="📌 Topic", value=channel.topic[:100], inline=False)
        
        # Settings
        embed.add_field(name="🔞 NSFW", value="Yes" if channel.nsfw else "No", inline=True)
        embed.add_field(name="⏱️ Slowmode", value=f"{channel.slowmode_delay}s" if channel.slowmode_delay else "Off", inline=True)
        
        # Category
        if channel.category:
            embed.add_field(name="📁 Category", value=channel.category.name, inline=True)
        
        # Permissions
        can_send = channel.permissions_for(interaction.guild.me).send_messages
        can_embed = channel.permissions_for(interaction.guild.me).embed_links
        
        embed.add_field(
            name="🤖 Bot Permissions",
            value=f"Send Messages: {'✅' if can_send else '❌'}\nEmbed Links: {'✅' if can_embed else '❌'}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roleinfo", description="View role information")
    @app_commands.describe(role="Role to view info about")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        """Display detailed role information"""
        embed = discord.Embed(
            title=f"📊 Role Information",
            color=role.color if role.color != discord.Color.default() else discord.Color.blue()
        )
        
        embed.add_field(name="👤 Name", value=role.name, inline=True)
        embed.add_field(name="🆔 ID", value=role.id, inline=True)
        embed.add_field(name="🎨 Color", value=str(role.color), inline=True)
        
        embed.add_field(name="👥 Members", value=len(role.members), inline=True)
        embed.add_field(name="📊 Position", value=role.position, inline=True)
        embed.add_field(name="📌 Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        
        embed.add_field(name="🎭 Hoisted", value="Yes" if role.hoist else "No", inline=True)
        embed.add_field(name="🤖 Managed", value="Yes" if role.managed else "No", inline=True)
        embed.add_field(name="📅 Created", value=role.created_at.strftime("%Y-%m-%d"), inline=True)
        
        # Key permissions
        key_perms = []
        if role.permissions.administrator:
            key_perms.append("👑 Administrator")
        if role.permissions.manage_guild:
            key_perms.append("⚙️ Manage Server")
        if role.permissions.manage_roles:
            key_perms.append("🎭 Manage Roles")
        if role.permissions.manage_channels:
            key_perms.append("📁 Manage Channels")
        if role.permissions.kick_members:
            key_perms.append("👢 Kick Members")
        if role.permissions.ban_members:
            key_perms.append("🔨 Ban Members")
        
        if key_perms:
            embed.add_field(name="🔑 Key Permissions", value="\n".join(key_perms), inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="topchatters", description="View most active chatters")
    async def topchatters(self, interaction: discord.Interaction):
        """Display most active chatters in the server"""
        guild_id = interaction.guild.id
        
        if guild_id not in self.message_counts or not self.message_counts[guild_id]:
            await interaction.response.send_message("❌ No message data available yet!", ephemeral=True)
            return
        
        # Sort by message count
        sorted_users = sorted(
            self.message_counts[guild_id].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title="💬 Top Chatters",
            description="Most active members (since bot started)",
            color=discord.Color.gold()
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, count) in enumerate(sorted_users):
            user = interaction.guild.get_member(user_id)
            if user:
                medal = medals[i] if i < 3 else f"#{i+1}"
                embed.add_field(
                    name=f"{medal} {user.display_name}",
                    value=f"**{count}** messages",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="emojistats", description="View emoji usage statistics")
    async def emojistats(self, interaction: discord.Interaction):
        """Display server emoji statistics"""
        guild = interaction.guild
        
        if not guild.emojis:
            await interaction.response.send_message("❌ This server has no custom emojis!", ephemeral=True)
            return
        
        # Separate animated and static
        static_emojis = [e for e in guild.emojis if not e.animated]
        animated_emojis = [e for e in guild.emojis if e.animated]
        
        embed = discord.Embed(
            title="😀 Emoji Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="📊 Total", value=len(guild.emojis), inline=True)
        embed.add_field(name="🖼️ Static", value=len(static_emojis), inline=True)
        embed.add_field(name="🎬 Animated", value=len(animated_emojis), inline=True)
        
        # Emoji limits based on boost level
        limits = {
            0: (50, 50),
            1: (100, 100),
            2: (150, 150),
            3: (250, 250)
        }
        
        static_limit, animated_limit = limits[guild.premium_tier]
        
        embed.add_field(
            name="📈 Capacity",
            value=f"Static: {len(static_emojis)}/{static_limit}\nAnimated: {len(animated_emojis)}/{animated_limit}",
            inline=False
        )
        
        # Show some emojis
        if static_emojis:
            sample = " ".join([str(e) for e in static_emojis[:10]])
            embed.add_field(name="Static Emojis", value=sample, inline=False)
        
        if animated_emojis:
            sample = " ".join([str(e) for e in animated_emojis[:10]])
            embed.add_field(name="Animated Emojis", value=sample, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="membercount", description="View member count over time")
    async def membercount(self, interaction: discord.Interaction):
        """Display member count information"""
        guild = interaction.guild
        
        total = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = total - humans
        
        # Status breakdown
        online = len([m for m in guild.members if m.status == discord.Status.online])
        idle = len([m for m in guild.members if m.status == discord.Status.idle])
        dnd = len([m for m in guild.members if m.status == discord.Status.dnd])
        offline = len([m for m in guild.members if m.status == discord.Status.offline])
        
        embed = discord.Embed(
            title="👥 Member Count",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 Total Members",
            value=f"**{total}**",
            inline=False
        )
        
        embed.add_field(
            name="👤 Humans",
            value=f"**{humans}**",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Bots",
            value=f"**{bots}**",
            inline=True
        )
        
        embed.add_field(
            name="📈 Status Breakdown",
            value=f"🟢 Online: **{online}**\n🟡 Idle: **{idle}**\n🔴 DND: **{dnd}**\n⚫ Offline: **{offline}**",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
