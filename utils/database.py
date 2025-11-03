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
    
    async def connect(self):
        """Initialize database connection and tables"""
        await self.init_db()
    
    async def close(self):
        """Close database connection (no-op since we use context managers)"""
        pass
        
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
            
            # Shop items/boosts table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS shop_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    item_name TEXT,
                    effect TEXT,
                    expiry_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Inventory table for items
            await db.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    item_name TEXT,
                    item_type TEXT,
                    quantity INTEGER DEFAULT 1,
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Rob history table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS rob_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    robber_id INTEGER,
                    victim_id INTEGER,
                    guild_id INTEGER,
                    amount INTEGER,
                    success BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
    
    # Economy functions
    async def get_balance(self, user_id: int, guild_id: int = 0) -> int:
        """Get user's balance (simplified to return just balance amount)"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT balance FROM economy WHERE user_id = ? AND (guild_id = ? OR guild_id = 0)",
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                else:
                    # Create new account with starting balance
                    await db.execute(
                        "INSERT INTO economy (user_id, guild_id, balance, bank) VALUES (?, ?, 1000, 0)",
                        (user_id, guild_id)
                    )
                    await db.commit()
                    return 1000
    
    async def update_balance(self, user_id: int, amount: int, guild_id: int = 0) -> int:
        """Update user's balance and return new balance"""
        # Ensure user exists first
        await self.get_balance(user_id, guild_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE economy SET balance = balance + ? WHERE user_id = ? AND (guild_id = ? OR guild_id = 0)",
                (amount, user_id, guild_id)
            )
            await db.commit()
            
        # Return new balance
        return await self.get_balance(user_id, guild_id)
    
    async def get_last_daily(self, user_id: int, guild_id: int = 0) -> Optional[datetime]:
        """Get last daily claim timestamp"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT last_daily FROM economy WHERE user_id = ? AND (guild_id = ? OR guild_id = 0)",
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row and row[0]:
                    return datetime.fromisoformat(row[0])
                return None
    
    async def set_last_daily(self, user_id: int, guild_id: int = 0):
        """Set last daily claim timestamp"""
        await self.get_balance(user_id, guild_id)  # Ensure user exists
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE economy SET last_daily = ? WHERE user_id = ? AND (guild_id = ? OR guild_id = 0)",
                (datetime.utcnow().isoformat(), user_id, guild_id)
            )
            await db.commit()
    
    async def get_last_work(self, user_id: int, guild_id: int = 0) -> Optional[datetime]:
        """Get last work timestamp"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT last_work FROM economy WHERE user_id = ? AND (guild_id = ? OR guild_id = 0)",
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row and row[0]:
                    return datetime.fromisoformat(row[0])
                return None
    
    async def set_last_work(self, user_id: int, guild_id: int = 0):
        """Set last work timestamp"""
        await self.get_balance(user_id, guild_id)  # Ensure user exists
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE economy SET last_work = ? WHERE user_id = ? AND (guild_id = ? OR guild_id = 0)",
                (datetime.utcnow().isoformat(), user_id, guild_id)
            )
            await db.commit()
    
    async def add_earned(self, user_id: int, amount: int, guild_id: int = 0):
        """Track earnings (for statistics) - currently just a placeholder"""
        # This could be expanded to track total earnings in a separate column/table
        pass
    
    async def get_leaderboard(self, limit: int = 10, guild_id: int = 0) -> List[tuple]:
        """Get economy leaderboard"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """SELECT user_id, (balance + bank) as total 
                   FROM economy 
                   WHERE guild_id = ? OR guild_id = 0
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
    
    # Shop items functions
    async def add_shop_item(self, user_id: int, guild_id: int, item_name: str, effect: str, expiry_date: Optional[datetime]):
        """Add a shop item/boost to user's inventory"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO shop_items (user_id, guild_id, item_name, effect, expiry_date) VALUES (?, ?, ?, ?, ?)",
                (user_id, guild_id, item_name, effect, expiry_date.isoformat() if expiry_date else None)
            )
            await db.commit()
    
    async def get_active_boosts(self, user_id: int, guild_id: int) -> List[Dict[str, Any]]:
        """Get user's active boosts"""
        async with aiosqlite.connect(self.db_path) as db:
            # Clean up expired items first
            await db.execute(
                "DELETE FROM shop_items WHERE expiry_date IS NOT NULL AND expiry_date <= ?",
                (datetime.utcnow().isoformat(),)
            )
            await db.commit()
            
            # Get active boosts
            async with db.execute(
                """SELECT item_name, effect, expiry_date 
                   FROM shop_items 
                   WHERE user_id = ? AND guild_id = ? 
                   AND (expiry_date IS NULL OR expiry_date > ?)""",
                (user_id, guild_id, datetime.utcnow().isoformat())
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'item_name': row[0],
                        'effect': row[1],
                        'expiry_date': datetime.fromisoformat(row[2]) if row[2] else None
                    }
                    for row in rows
                ]
    
    async def has_active_boost(self, user_id: int, guild_id: int, effect: str) -> bool:
        """Check if user has a specific active boost"""
        boosts = await self.get_active_boosts(user_id, guild_id)
        return any(boost['effect'] == effect for boost in boosts)
    
    async def remove_expired_boosts(self):
        """Remove all expired boosts from database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM shop_items WHERE expiry_date IS NOT NULL AND expiry_date <= ?",
                (datetime.utcnow().isoformat(),)
            )
            await db.commit()
    
    # Inventory functions
    async def add_inventory_item(self, user_id: int, guild_id: int, item_name: str, item_type: str, quantity: int = 1):
        """Add an item to user's inventory"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if item already exists
            async with db.execute(
                "SELECT id, quantity FROM inventory WHERE user_id = ? AND guild_id = ? AND item_name = ?",
                (user_id, guild_id, item_name)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    # Update quantity
                    await db.execute(
                        "UPDATE inventory SET quantity = quantity + ? WHERE id = ?",
                        (quantity, row[0])
                    )
                else:
                    # Insert new item
                    await db.execute(
                        "INSERT INTO inventory (user_id, guild_id, item_name, item_type, quantity) VALUES (?, ?, ?, ?, ?)",
                        (user_id, guild_id, item_name, item_type, quantity)
                    )
            await db.commit()
    
    async def get_inventory(self, user_id: int, guild_id: int) -> List[Dict[str, Any]]:
        """Get user's inventory"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT item_name, item_type, quantity FROM inventory WHERE user_id = ? AND guild_id = ? AND quantity > 0",
                (user_id, guild_id)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'item_name': row[0],
                        'item_type': row[1],
                        'quantity': row[2]
                    }
                    for row in rows
                ]
    
    async def get_item_quantity(self, user_id: int, guild_id: int, item_name: str) -> int:
        """Get quantity of specific item in inventory"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT quantity FROM inventory WHERE user_id = ? AND guild_id = ? AND item_name = ?",
                (user_id, guild_id, item_name)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def use_inventory_item(self, user_id: int, guild_id: int, item_name: str, quantity: int = 1) -> bool:
        """Use/consume an item from inventory"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if user has enough
            current_qty = await self.get_item_quantity(user_id, guild_id, item_name)
            if current_qty < quantity:
                return False
            
            # Reduce quantity
            await db.execute(
                "UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND guild_id = ? AND item_name = ?",
                (quantity, user_id, guild_id, item_name)
            )
            await db.commit()
            return True
    
    async def remove_inventory_item(self, user_id: int, guild_id: int, item_name: str):
        """Remove an item completely from inventory"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM inventory WHERE user_id = ? AND guild_id = ? AND item_name = ?",
                (user_id, guild_id, item_name)
            )
            await db.commit()
    
    # Rob history functions
    async def add_rob_attempt(self, robber_id: int, victim_id: int, guild_id: int, amount: int, success: bool):
        """Record a rob attempt"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO rob_history (robber_id, victim_id, guild_id, amount, success) VALUES (?, ?, ?, ?, ?)",
                (robber_id, victim_id, guild_id, amount, success)
            )
            await db.commit()
    
    async def get_last_rob(self, user_id: int, guild_id: int) -> Optional[datetime]:
        """Get last time user robbed someone"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT timestamp FROM rob_history WHERE robber_id = ? AND guild_id = ? ORDER BY timestamp DESC LIMIT 1",
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return datetime.fromisoformat(row[0])
                return None
    
    async def get_rob_stats(self, user_id: int, guild_id: int) -> Dict[str, int]:
        """Get user's rob statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total robs attempted
            async with db.execute(
                "SELECT COUNT(*) FROM rob_history WHERE robber_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ) as cursor:
                total = (await cursor.fetchone())[0]
            
            # Successful robs
            async with db.execute(
                "SELECT COUNT(*) FROM rob_history WHERE robber_id = ? AND guild_id = ? AND success = 1",
                (user_id, guild_id)
            ) as cursor:
                successful = (await cursor.fetchone())[0]
            
            # Times robbed
            async with db.execute(
                "SELECT COUNT(*) FROM rob_history WHERE victim_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ) as cursor:
                times_robbed = (await cursor.fetchone())[0]
            
            return {
                'total_attempts': total,
                'successful': successful,
                'failed': total - successful,
                'times_robbed': times_robbed
            }

