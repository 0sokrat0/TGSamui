import aiomysql
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import app.keyboards as kb
from config import db_config
from database.database import Database

router = Router()
db = Database(db_config)


async def ensure_db_connection():
    if db.pool is None:
        await db.connect()
        if db.pool is None:
            raise Exception("Failed to connect to the database")
        print("Database connected successfully.")




@router.callback_query(F.data == "best_properties")
async def show_top_properties(callback: CallbackQuery):
    await ensure_db_connection()
    buttons = [[InlineKeyboardButton(text="Реальный Самуи🏝️",url="https://t.me/realsamuiru")],
               [InlineKeyboardButton(text="Аренда на Самуи", url="https://t.me/villanasamui")],
               [InlineKeyboardButton(text="🔚 Возврат в меню", callback_data="back_to_main")]]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.answer("🌟 Лучшие объекты недвижимости")
    await callback.message.answer("🌟 Лучшие объекты недвижимости:", reply_markup=keyboard)


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback_query: CallbackQuery):
    await db.update_last_activity(callback_query.from_user.id)
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=kb.main)
    await callback_query.answer()
