import aiosqlite
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger('MegaBot.Database')

class Database:
    """Async SQLite database manager for the bot"""
    
    def __init__(self, db_path='bot_data.db'):
        self.db_path = db_path
        self.conn = None
    
    async def connect(self):
        """Connect to the database and create tables"""
        self.conn = await aiosqlite.connect(self.db_path)
        await self.create_tables()
        logger.info(f"Database connected: {self.db_path}")
    
    async def close(self):
        """Close the database connection"""
        if self.conn:
            await self.conn.close()
            logger.info("Database connection closed")
    
    async def create_tables(self):
        """Create all necessary tables"""
        
        # Users table - economy data
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 1000,
                total_earned INTEGER DEFAULT 0,
                join_date TEXT,
                last_daily TEXT,
                last_work TEXT
            )
        ''')
        
        # Shop items - active boosts
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_name TEXT,
                expiry_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Warnings - moderation
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Reminders
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel_id INTEGER,
                message TEXT,
                reminder_time TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        await self.conn.commit()
        logger.info("Database tables created/verified")
    
    # ==================== USER METHODS ====================
    
    async def get_user(self, user_id):
        """Get user data, create if doesn't exist"""
        async with self.conn.execute(
            'SELECT * FROM users WHERE user_id = ?', (user_id,)
        ) as cursor:
            user = await cursor.fetchone()
        
        if not user:
            # Create new user with default values
            now = datetime.utcnow().isoformat()
            await self.conn.execute(
                '''INSERT INTO users (user_id, balance, total_earned, join_date, last_daily, last_work)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (user_id, Config.STARTING_BALANCE, 0, now, None, None)
            )
            await self.conn.commit()
            
            # Fetch the newly created user
            async with self.conn.execute(
                'SELECT * FROM users WHERE user_id = ?', (user_id,)
            ) as cursor:
                user = await cursor.fetchone()
        
        return user
    
    async def get_balance(self, user_id):
        """Get user's balance"""
        user = await self.get_user(user_id)
        return user[1]  # balance column
    
    async def update_balance(self, user_id, amount):
        """Update user's balance (can be positive or negative)"""
        current = await self.get_balance(user_id)
        new_balance = max(0, current + amount)
        
        await self.conn.execute(
            'UPDATE users SET balance = ? WHERE user_id = ?',
            (new_balance, user_id)
        )
        await self.conn.commit()
        return new_balance
    
    async def set_balance(self, user_id, amount):
        """Set user's balance to a specific amount"""
        await self.get_user(user_id)  # Ensure user exists
        await self.conn.execute(
            'UPDATE users SET balance = ? WHERE user_id = ?',
            (max(0, amount), user_id)
        )
        await self.conn.commit()
    
    async def add_earned(self, user_id, amount):
        """Add to user's total earned"""
        user = await self.get_user(user_id)
        new_total = user[2] + amount  # total_earned column
        
        await self.conn.execute(
            'UPDATE users SET total_earned = ? WHERE user_id = ?',
            (new_total, user_id)
        )
        await self.conn.commit()
    
    # ==================== COOLDOWN METHODS ====================
    
    async def get_last_daily(self, user_id):
        """Get user's last daily claim time"""
        user = await self.get_user(user_id)
        last_daily = user[4]  # last_daily column
        if last_daily:
            return datetime.fromisoformat(last_daily)
        return None
    
    async def set_last_daily(self, user_id):
        """Set user's last daily claim to now"""
        await self.get_user(user_id)  # Ensure user exists
        now = datetime.utcnow().isoformat()
        await self.conn.execute(
            'UPDATE users SET last_daily = ? WHERE user_id = ?',
            (now, user_id)
        )
        await self.conn.commit()
    
    async def get_last_work(self, user_id):
        """Get user's last work time"""
        user = await self.get_user(user_id)
        last_work = user[5]  # last_work column
        if last_work:
            return datetime.fromisoformat(last_work)
        return None
    
    async def set_last_work(self, user_id):
        """Set user's last work time to now"""
        await self.get_user(user_id)  # Ensure user exists
        now = datetime.utcnow().isoformat()
        await self.conn.execute(
            'UPDATE users SET last_work = ? WHERE user_id = ?',
            (now, user_id)
        )
        await self.conn.commit()
    
    # ==================== LEADERBOARD METHODS ====================
    
    async def get_leaderboard(self, limit=10):
        """Get top users by balance"""
        async with self.conn.execute(
            'SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT ?',
            (limit,)
        ) as cursor:
            return await cursor.fetchall()
    
    # ==================== SHOP METHODS ====================
    
    async def add_shop_item(self, user_id, item_name, expiry_date):
        """Add an active shop item/boost"""
        await self.conn.execute(
            'INSERT INTO shop_items (user_id, item_name, expiry_date) VALUES (?, ?, ?)',
            (user_id, item_name, expiry_date.isoformat() if expiry_date else None)
        )
        await self.conn.commit()
    
    async def get_active_items(self, user_id):
        """Get all active items for a user"""
        now = datetime.utcnow().isoformat()
        async with self.conn.execute(
            '''SELECT item_name, expiry_date FROM shop_items 
               WHERE user_id = ? AND (expiry_date IS NULL OR expiry_date > ?)''',
            (user_id, now)
        ) as cursor:
            return await cursor.fetchall()
    
    async def remove_expired_items(self):
        """Remove expired items from database"""
        now = datetime.utcnow().isoformat()
        await self.conn.execute(
            'DELETE FROM shop_items WHERE expiry_date IS NOT NULL AND expiry_date <= ?',
            (now,)
        )
        await self.conn.commit()
    
    # ==================== MODERATION METHODS ====================
    
    async def add_warning(self, user_id, moderator_id, reason):
        """Add a warning to a user"""
        now = datetime.utcnow().isoformat()
        await self.conn.execute(
            'INSERT INTO warnings (user_id, moderator_id, reason, timestamp) VALUES (?, ?, ?, ?)',
            (user_id, moderator_id, reason, now)
        )
        await self.conn.commit()
    
    async def get_warnings(self, user_id):
        """Get all warnings for a user"""
        async with self.conn.execute(
            'SELECT moderator_id, reason, timestamp FROM warnings WHERE user_id = ? ORDER BY timestamp DESC',
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()
    
    async def get_warning_count(self, user_id):
        """Get total warning count for a user"""
        async with self.conn.execute(
            'SELECT COUNT(*) FROM warnings WHERE user_id = ?',
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    # ==================== REMINDER METHODS ====================
    
    async def add_reminder(self, user_id, channel_id, message, reminder_time):
        """Add a reminder"""
        now = datetime.utcnow().isoformat()
        await self.conn.execute(
            'INSERT INTO reminders (user_id, channel_id, message, reminder_time, created_at) VALUES (?, ?, ?, ?, ?)',
            (user_id, channel_id, message, reminder_time.isoformat(), now)
        )
        await self.conn.commit()
    
    async def get_due_reminders(self):
        """Get all reminders that are due"""
        now = datetime.utcnow().isoformat()
        async with self.conn.execute(
            'SELECT id, user_id, channel_id, message FROM reminders WHERE reminder_time <= ?',
            (now,)
        ) as cursor:
            return await cursor.fetchall()
    
    async def remove_reminder(self, reminder_id):
        """Remove a reminder by ID"""
        await self.conn.execute(
            'DELETE FROM reminders WHERE id = ?',
            (reminder_id,)
        )
        await self.conn.commit()
