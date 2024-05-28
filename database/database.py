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

    async def add_user(self, user_id, tg_name=None):
        await self.ensure_connection()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "INSERT INTO users (user_id, username) VALUES (%s, %s) ON DUPLICATE KEY UPDATE username = %s"
                await cursor.execute(query, (user_id, tg_name, tg_name))
                await conn.commit()

    async def get_user_info(self, user_id):
        await self.ensure_connection()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "SELECT * FROM users WHERE user_id = %s"
                await cursor.execute(query, (user_id,))
                return await cursor.fetchone()

    async def add_user_phone_number(self, user_id, phone_number):
        await self.ensure_connection()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "UPDATE users SET phone_number = %s WHERE user_id = %s"
                await cursor.execute(query, (phone_number, user_id))
                await conn.commit()
                return cursor.rowcount > 0

    async def is_phone_number_registered(self, user_id):
        user_info = await self.get_user_info(user_id)
        # Проверяем, существует ли запись и не равен ли номер телефона NULL
        return user_info and user_info[3] is not None

    async def update_last_login(self, user_id):
        await self.ensure_connection()
        now = datetime.now()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "UPDATE users SET last_login = %s WHERE user_id = %s"
                await cursor.execute(query, (now, user_id))
                await conn.commit()

    async def update_last_activity(self, user_id):
        await self.ensure_connection()
        now = datetime.now()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "UPDATE users SET last_activity = %s WHERE user_id = %s"
                await cursor.execute(query, (now, user_id))
                await conn.commit()

    async def update_user_email(self, user_id, email):
        await self.ensure_connection()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "UPDATE users SET email = %s WHERE user_id = %s"
                await cursor.execute(query, (email, user_id))
                await conn.commit()

    async def update_user_phone_number(self, user_id, phone_number):
        await self.ensure_connection()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "UPDATE users SET phone_number = %s WHERE user_id = %s"
                await cursor.execute(query, (phone_number, user_id))
                await conn.commit()

    async def get_properties(db, property_type=None, number_of_beds=None, location=None):
        await db.ensure_connection()

        query = """
        SELECT property_id, title, location, distance_to_sea, category, monthly_price, daily_price,
               booking_deposit, safety_deposit, bedrooms, bathrooms, pool, kitchen, cleaning, description, utilities
        FROM properties
        WHERE (%s IS NULL OR category = %s)
        AND (%s IS NULL OR bedrooms = %s)
        AND (%s IS NULL OR location = %s)
        """
        params = (property_type, property_type, number_of_beds, number_of_beds, location, location)

        logging.info(f"Executing query: {query}")
        logging.info(f"With params: {params}")

        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                result = await cursor.fetchall()

                logging.info(f"Query result: {result}")

                properties = []
                for row in result:
                    property = {
                        'id': row[0],
                        'name': row[1],
                        'location': row[2],
                        'distance_to_sea': row[3],
                        'category': row[4],
                        'monthly_price': row[5],
                        'daily_price': row[6],
                        'booking_deposit': row[7],
                        'safety_deposit': row[8],
                        'bedrooms': row[9],
                        'bathrooms': row[10],
                        'pool': row[11],
                        'kitchen': row[12],
                        'cleaning': row[13],
                        'description': row[14],
                        'utilities': row[15]
                    }
                    properties.append(property)

        return properties

    async def add_property_to_favorites(self, user_id, property_id):
        await self.ensure_connection()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "INSERT INTO favorites (user_id, property_id) VALUES (%s, %s)"
                await cursor.execute(query, (user_id, property_id))
                await conn.commit()




    async def save_notification(self, photo: str, message: str):
        await self.ensure_connection()

        query = """
        INSERT INTO newsletters (photo, message, sent_at)
        VALUES (%s, %s, NOW())
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (photo, message))
                await conn.commit()
                await cursor.execute("SELECT LAST_INSERT_ID()")
                result = await cursor.fetchone()
                return result[0]

    async def get_notification(self, notification_id: int):
        await self.ensure_connection()
        query = """
           SELECT photo, caption FROM notifications WHERE id = %s
           """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (notification_id,))
                result = await cursor.fetchone()
        return result


    async def update_last_activity(self, user_id: int):
        await self.ensure_connection()

        query = "UPDATE users SET last_activity = NOW() WHERE user_id = %s"
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (user_id,))
                await conn.commit()

    async def subscribe_to_notifications(self, user_id: int):
        await self.ensure_connection()

        query = """
           UPDATE users SET notifications_enabled = TRUE WHERE user_id = %s
           """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (user_id,))
                await conn.commit()

    async def unsubscribe_from_notifications(self, user_id: int):
        await self.ensure_connection()

        query = """
           UPDATE users SET notifications_enabled = FALSE WHERE user_id = %s
           """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (user_id,))
                await conn.commit()


    async def get_detailed_user_statistics(self):
        await self.ensure_connection()

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

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query_total_users)
                total_users = await cursor.fetchone()

                await cursor.execute(query_active_users)
                active_users = await cursor.fetchone()

                await cursor.execute(query_new_users)
                new_users = await cursor.fetchone()

        return {
            'total_users': total_users[0],
            'active_users': active_users[0],
            'new_users': new_users[0]
        }