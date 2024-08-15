import logging

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

import app.keyboards as kb
from config import db_config, ADMINS
from database.database import Database

router = Router()
db = Database(db_config)


async def ensure_db_connection():
    if db.pool is None:
        await db.connect()
        if db.pool is None:
            raise Exception("Failed to connect to the database")
        print("Database connected successfully.")


@router.message(CommandStart())
async def send_welcome(message: Message):
    await ensure_db_connection()
    await db.update_last_activity(message.from_user.id)
    user_id = message.from_user.id
    user_info = await db.get_user_info(user_id)

    if user_info:
        phone_number_index = 3
        if user_info[phone_number_index]:
            welcome_text = (
                f"<b>Приветствую, {message.from_user.first_name}!</b>\n"
                "Добро пожаловать в нашего Telegram-бота по поиску недвижимости на острове <u><b>Самуи</b></u>! 🌴🏠\n\n"
                "<b>Я могу помочь вам найти идеальное место для вашего отдыха или проживания на этом прекрасном острове.</b>\n\n"
            )
            if user_id in ADMINS:
                await message.answer(welcome_text, reply_markup=kb.admin_main, parse_mode=ParseMode.HTML)
            else:
                await message.answer(welcome_text, reply_markup=kb.main, parse_mode=ParseMode.HTML)
        else:
            await message.answer('Пожалуйста, предоставьте ваш номер телефона.', reply_markup=kb.numbers)
    else:
        await db.add_user(user_id, message.from_user.username)
        await message.answer('Регистрация...')
        await message.answer('Пожалуйста, нажмите на кнопку ниже, чтобы отправить ваш номер телефона.',
                             reply_markup=kb.numbers)
        await message.answer('Вы успешно зарегистрированы. Добро пожаловать!',
                             reply_markup=kb.main if user_id not in ADMINS else kb.admin_main)


@router.message(F.contact)
async def handle_contact(message: Message):
    telegram_id = message.from_user.id
    phone_number = message.contact.phone_number

    success = await db.add_user_phone_number(telegram_id, phone_number)
    logging.info(f"add_user_phone_number: user_id={telegram_id}, phone_number={phone_number}, success={success}")

    await message.answer("Спасибо, ваш номер телефона успешно сохранен.", reply_markup=kb.main)
    welcome_text = (
        f"<b>Приветствую, {message.from_user.first_name}!</b>\n"
        "Добро пожаловать в нашего Telegram-бота по поиску недвижимости на острове <u><b>Самуи</b></u>! 🌴🏠\n\n"
        "<b>Я могу помочь вам найти идеальное место для вашего отдыха или проживания на этом прекрасном острове.</b>\n\n"
    )
    await message.answer(welcome_text, reply_markup=kb.main, parse_mode=ParseMode.HTML)
