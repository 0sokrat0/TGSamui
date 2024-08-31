# database.py
import logging
from datetime import datetime

import aiomysql


class Database:
    def __init__(self, db_config):
        self.db_config = db_config
        self.pool = None

    async def connect(self):
        try:
            self.pool = await aiomysql.create_pool(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                db=self.db_config['db'],
                minsize=1,
                maxsize=10,
                autocommit=True
            )
            logging.info("Database connection pool created.")
        except Exception as e:
            logging.error(f"Error creating database connection pool: {e}")
            self.pool = None
            raise

    async def disconnect(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logging.info("Database connection pool closed.")
        else:
            logging.warning("Database connection pool is already closed or was never initialized.")

    async def ensure_connection(self):
        if self.pool is None:
            await self.connect()
        if self.pool is None:
            raise Exception("Failed to connect to the database")

    async def execute_query(self, query, params):
        await self.ensure_connection()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                return cursor

    async def fetch_one(self, query, params):
        await self.ensure_connection()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchone()

    async def fetch_all(self, query, params):
        await self.ensure_connection()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()

    async def add_user(self, user_id, tg_name=None):
        query = "INSERT INTO users (user_id, username) VALUES (%s, %s) ON DUPLICATE KEY UPDATE username = %s"
        await self.execute_query(query, (user_id, tg_name, tg_name))

    async def get_user_info(self, user_id):
        query = "SELECT * FROM users WHERE user_id = %s"
        return await self.fetch_one(query, (user_id,))

    async def update_user_field(self, user_id, field, value):
        query = f"UPDATE users SET {field} = %s WHERE user_id = %s"
        await self.execute_query(query, (value, user_id))

    async def add_user_phone_number(self, user_id, phone_number):
        return await self.update_user_field(user_id, 'phone_number', phone_number)

    async def is_phone_number_registered(self, user_id):
        user_info = await self.get_user_info(user_id)
        return user_info and user_info[3] is not None

    async def update_last_login(self, user_id):
        await self.update_user_field(user_id, 'last_login', datetime.now())

    async def update_last_activity(self, user_id):
        await self.update_user_field(user_id, 'last_activity', datetime.now())

    async def update_user_email(self, user_id, email):
        await self.update_user_field(user_id, 'email', email)

    async def get_properties(self, property_type=None, number_of_beds=None, location=None):
        query = """
        SELECT property_id, title, location, distance_to_sea, category, monthly_price, daily_price,
               booking_deposit, safety_deposit, bedrooms, bathrooms, pool, kitchen, cleaning, description, utilities
        FROM properties
        WHERE (%s IS NULL OR category = %s)
        AND (%s IS NULL OR bedrooms = %s)
        AND (%s IS NULL OR location = %s)
        """
        params = (property_type, property_type, number_of_beds, number_of_beds, location, location)
        return await self.fetch_all(query, params)

    async def add_property_to_favorites(self, user_id, property_id):
        query = "INSERT INTO favorites (user_id, property_id) VALUES (%s, %s)"
        await self.execute_query(query, (user_id, property_id))

    async def save_notification(self, photo, message):
        query = """
        INSERT INTO newsletters (photo, message, sent_at)
        VALUES (%s, %s, NOW())
        """
        cursor = await self.execute_query(query, (photo, message))
        await cursor.execute("SELECT LAST_INSERT_ID()")
        result = await cursor.fetchone()
        return result[0]

    async def get_notification(self, notification_id):
        query = "SELECT photo, caption FROM notifications WHERE id = %s"
        return await self.fetch_one(query, (notification_id,))

    async def subscribe_to_notifications(self, user_id):
        query = "UPDATE users SET notifications_enabled = TRUE WHERE user_id = %s"
        await self.execute_query(query, (user_id,))

    async def unsubscribe_from_notifications(self, user_id):
        query = "UPDATE users SET notifications_enabled = FALSE WHERE user_id = %s"
        await self.execute_query(query, (user_id,))

    async def get_detailed_user_statistics(self):
        query_total_users = "SELECT COUNT(*) FROM users"
        query_active_users = """
           SELECT COUNT(*)
           FROM users
           WHERE last_activity >= NOW() - INTERVAL 1 WEEK
           """
        query_new_users = """
           SELECT COUNT(*)
           FROM users
           WHERE created_at >= NOW() - INTERVAL 1 WEEK
           """

        total_users = await self.fetch_one(query_total_users, ())
        active_users = await self.fetch_one(query_active_users, ())
        new_users = await self.fetch_one(query_new_users, ())

        return {
            'total_users': total_users[0],
            'active_users': active_users[0],
            'new_users': new_users[0]
        }

