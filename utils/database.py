"""
Database utilities for MegaBot
Handles all database operations using SQLite
"""

import sqlite3
import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = db_path
        
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Economy table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS economy (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    balance INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    last_daily TIMESTAMP,
                    last_work TIMESTAMP
                )
            """)
            
            # Reminders table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    channel_id INTEGER,
                    message TEXT,
                    remind_time TIMESTAMP
                )
            """)
            
            # Homework table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS homework (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    subject TEXT,
                    assignment TEXT,
                    due_date DATE,
                    completed BOOLEAN DEFAULT 0
                )
            """)
            
            # Tournament table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tournaments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    name TEXT,
                    game TEXT,
                    max_players INTEGER,
                    status TEXT,
                    created_at TIMESTAMP
                )
            """)
            
            # Server configs
            await db.execute("""
                CREATE TABLE IF NOT EXISTS server_config (
                    guild_id INTEGER PRIMARY KEY,
                    welcome_channel INTEGER,
                    log_channel INTEGER,
                    prefix TEXT DEFAULT '!'
                )
            """)
            
            await db.commit()
    
    # Economy functions
    async def get_balance(self, user_id: int, guild_id: int) -> Dict[str, int]:
        """Get user's balance"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT balance, bank FROM economy WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {'balance': row[0], 'bank': row[1]}
                else:
                    # Create new account
                    await db.execute(
                        "INSERT INTO economy (user_id, guild_id, balance, bank) VALUES (?, ?, 100, 0)",
                        (user_id, guild_id)
                    )
                    await db.commit()
                    return {'balance': 100, 'bank': 0}
    
    async def update_balance(self, user_id: int, guild_id: int, amount: int):
        """Update user's balance"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE economy SET balance = balance + ? WHERE user_id = ? AND guild_id = ?",
                (amount, user_id, guild_id)
            )
            await db.commit()
    
    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[tuple]:
        """Get economy leaderboard"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT user_id, (balance + bank) as total 
                   FROM economy 
                   WHERE guild_id = ? 
                   ORDER BY total DESC 
                   LIMIT ?""",
                (guild_id, limit)
            ) as cursor:
                return await cursor.fetchall()
    
    async def check_cooldown(self, user_id: int, guild_id: int, cooldown_type: str) -> Optional[datetime]:
        """Check if user is on cooldown"""
        async with aiosqlite.connect(self.db_path) as db:
            column = f"last_{cooldown_type}"
            async with db.execute(
                f"SELECT {column} FROM economy WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row and row[0]:
                    return datetime.fromisoformat(row[0])
                return None
    
    async def update_cooldown(self, user_id: int, guild_id: int, cooldown_type: str):
        """Update cooldown timestamp"""
        async with aiosqlite.connect(self.db_path) as db:
            column = f"last_{cooldown_type}"
            await db.execute(
                f"UPDATE economy SET {column} = ? WHERE user_id = ? AND guild_id = ?",
                (datetime.utcnow().isoformat(), user_id, guild_id)
            )
            await db.commit()
    
    # Reminder functions
    async def add_reminder(self, user_id: int, channel_id: int, message: str, remind_time: datetime):
        """Add a reminder"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO reminders (user_id, channel_id, message, remind_time) VALUES (?, ?, ?, ?)",
                (user_id, channel_id, message, remind_time.isoformat())
            )
            await db.commit()
    
    async def get_due_reminders(self) -> List[Dict[str, Any]]:
        """Get reminders that are due"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, user_id, channel_id, message FROM reminders WHERE remind_time <= ?",
                (datetime.utcnow().isoformat(),)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {'id': row[0], 'user_id': row[1], 'channel_id': row[2], 'message': row[3]}
                    for row in rows
                ]
    
    async def delete_reminder(self, reminder_id: int):
        """Delete a reminder"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            await db.commit()
    
    # Homework functions
    async def add_homework(self, user_id: int, subject: str, assignment: str, due_date: str):
        """Add homework assignment"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO homework (user_id, subject, assignment, due_date) VALUES (?, ?, ?, ?)",
                (user_id, subject, assignment, due_date)
            )
            await db.commit()
    
    async def get_homework(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's homework"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, subject, assignment, due_date, completed FROM homework WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'subject': row[1],
                        'assignment': row[2],
                        'due_date': row[3],
                        'completed': bool(row[4])
                    }
                    for row in rows
                ]
    
    async def complete_homework(self, homework_id: int):
        """Mark homework as complete"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE homework SET completed = 1 WHERE id = ?",
                (homework_id,)
            )
            await db.commit()
    
    async def delete_homework(self, homework_id: int):
        """Delete homework"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM homework WHERE id = ?", (homework_id,))
            await db.commit()
    
    # Server config functions
    async def get_server_config(self, guild_id: int) -> Dict[str, Any]:
        """Get server configuration"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT welcome_channel, log_channel, prefix FROM server_config WHERE guild_id = ?",
                (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'welcome_channel': row[0],
                        'log_channel': row[1],
                        'prefix': row[2]
                    }
                else:
                    return {'welcome_channel': None, 'log_channel': None, 'prefix': '!'}
    
    async def set_welcome_channel(self, guild_id: int, channel_id: int):
        """Set welcome channel"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO server_config (guild_id, welcome_channel) 
                   VALUES (?, ?) 
                   ON CONFLICT(guild_id) 
                   DO UPDATE SET welcome_channel = ?""",
                (guild_id, channel_id, channel_id)
            )
            await db.commit()
