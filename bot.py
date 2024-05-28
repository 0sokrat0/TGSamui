import atexit
import asyncio
import logging
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from app import handlers, admin
from config import TOKEN, db_config, ADMINS
from database.database import Database
import aiomysql

# Создание экземпляра базы данных
db = Database(db_config)

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройка логирования
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler('bot.log', maxBytes=5*1024*1024, backupCount=2, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

async def notify_admins(message: str):
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, message)
        except TelegramBadRequest as e:
            logging.error(f"Failed to send message to admin {admin_id}: {e}")
        except Exception as e:
            logging.exception(f"Failed to send message to admin {admin_id}: {e}")

async def check_new_properties(bot: Bot, db: Database):
    while True:
        try:
            now = datetime.now()
            one_day_ago = now - timedelta(days=1)

            query = "SELECT * FROM properties WHERE created_at >= %s AND notified = FALSE"
            async with db.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, (one_day_ago,))
                    new_properties = await cursor.fetchall()

            if new_properties:
                users_query = "SELECT user_id, last_notified FROM users WHERE notifications_enabled = TRUE"
                async with db.pool.acquire() as conn:
                    async with conn.cursor(aiomysql.DictCursor) as cursor:
                        await cursor.execute(users_query)
                        users = await cursor.fetchall()

                for user in users:
                    last_notified = user['last_notified']
                    if last_notified is None or (now - last_notified).days >= 1:
                        message_text = "Новые объекты недвижимости:\n\n"
                        for property in new_properties:
                            message_text += (
                                f"🏠 <b>{property['name']}</b>\n"
                                f"📍 <b>Расположение:</b> {property['location']}\n"
                                f"🌊 <b>Удаленность от моря:</b> {property['distance_to_sea']} метров\n"
                                f"💰 <b>Стоимость в месяц:</b> {property['monthly_price']}฿\n"
                                "-----------------------\n"
                            )

                        try:
                            await bot.send_message(user['user_id'], message_text, parse_mode=ParseMode.HTML)
                        except Exception as e:
                            logging.error(f"Error sending message to user {user['user_id']}: {e}")

                        # Обновить поле notified для текущей property
                        update_property_query = "UPDATE properties SET notified = TRUE WHERE property_id = %s"
                        async with db.pool.acquire() as conn:
                            async with conn.cursor() as cursor:
                                for property in new_properties:
                                    await cursor.execute(update_property_query, (property['property_id'],))
                                await conn.commit()

                        update_user_query = "UPDATE users SET last_notified = %s WHERE user_id = %s"
                        async with db.pool.acquire() as conn:
                            async with conn.cursor() as cursor:
                                await cursor.execute(update_user_query, (now, user['user_id']))
                                await conn.commit()

            await asyncio.sleep(86400)  # Проверять раз в день

        except Exception as e:
            logging.error(f"Error in check_new_properties: {e}")
            await asyncio.sleep(60)  # Подождать минуту перед повторной попыткой

async def on_startup(dispatcher: Dispatcher):
    try:
        await db.connect()
        asyncio.create_task(check_new_properties(bot, db))  # Запуск задачи проверки новых объектов недвижимости
    except Exception as e:
        await notify_admins(f"Error connecting to the database: {e}")
        raise

async def on_shutdown(dispatcher: Dispatcher):
    try:
        await db.disconnect()
    except Exception as e:
        await notify_admins(f"Error disconnecting from the database: {e}")
        raise

async def main():
    dp.include_routers(handlers.router, admin.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        await notify_admins(f"Bot stopped unexpectedly: {e}")
        raise
    finally:
        await bot.session.close()
        await db.disconnect()

def exit_handler():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db.disconnect())
    loop.run_until_complete(notify_admins("Bot is shutting down. Please check the system."))
    loop.close()

if __name__ == "__main__":
    setup_logging()

    atexit.register(exit_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Пока")
        asyncio.run(notify_admins("Бот отключился"))
    except Exception as e:
        logging.exception("Произошла ошибка: %s", e)
        asyncio.run(notify_admins(f"‼️Bot stopped due to an error: {e}"))
