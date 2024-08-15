import aiomysql
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

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


class ProfileUpdate(StatesGroup):
    waiting_for_email = State()
    waiting_for_phone_number = State()
    confirming_email = State()
    confirming_phone_number = State()


async def edit_or_send_message(callback: CallbackQuery, text, reply_markup=None, parse_mode=None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)


@router.callback_query(F.data == "update_email")
async def prompt_for_email(callback: CallbackQuery, state: FSMContext):
    await edit_or_send_message(callback, "Пожалуйста, введите ваш новый email:")
    await state.set_state(ProfileUpdate.waiting_for_email)


@router.callback_query(F.data == "update_phone_number")
async def prompt_for_phone_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, нажмите на кнопку ниже, чтобы отправить ваш новый номер телефона.",
                                  reply_markup=kb.numbers)
    await callback.answer()
    await state.set_state(ProfileUpdate.waiting_for_phone_number)


@router.message(ProfileUpdate.waiting_for_email)
async def update_email(message: Message, state: FSMContext):
    email = message.text
    if "@" in email and "." in email and len(email) >= 5:
        await state.update_data(new_email=email)
        await message.answer(f"Вы хотите обновить email на: {email}? (Да/Нет)")
        await state.set_state(ProfileUpdate.confirming_email)
    else:
        await message.answer("Пожалуйста, введите корректный email (используйте @ и .).")


@router.message(ProfileUpdate.confirming_email)
async def confirm_email_update(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        data = await state.get_data()
        new_email = data['new_email']
        await db.update_user_email(message.from_user.id, new_email)
        await message.answer("Ваш email был успешно обновлен.", reply_markup=kb.main)
        await state.clear()
    else:
        await message.answer("Обновление email отменено.", reply_markup=kb.main)
        await state.clear()


@router.message(F.contact, ProfileUpdate.waiting_for_phone_number)
async def update_phone_number(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(new_phone_number=phone_number)
    await message.answer(f"Вы хотите обновить номер телефона на: {phone_number}? (Да/Нет)")
    await state.set_state(ProfileUpdate.confirming_phone_number)


@router.message(ProfileUpdate.confirming_phone_number)
async def confirm_phone_update(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        data = await state.get_data()
        new_phone_number = data['new_phone_number']
        await db.update_user_phone_number(message.from_user.id, new_phone_number)
        await message.answer("Ваш номер телефона был успешно обновлен.", reply_markup=kb.main)
        await state.clear()
    else:
        await message.answer("Обновление номера телефона отменено.", reply_markup=kb.main)
        await state.clear()


async def get_user_info(user_id):
    query = "SELECT user_id, username, email, phone_number FROM users WHERE user_id = %s"
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, (user_id,))
            result = await cursor.fetchone()
            return result


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    await ensure_db_connection()
    await db.update_last_activity(callback.from_user.id)
    user_info = await get_user_info(callback.from_user.id)
    if user_info:
        profile_info = (
            f"👤 <b>Ваш Профиль</b>\n\n"
            f"🔹 <b>Имя пользователя:</b> {user_info['username']}\n"
            f"🔹 <b>Номер телефона:</b> {user_info['phone_number']}\n"
            f"🔹 <b>Email:</b> {user_info['email'] if user_info['email'] else 'Не указан'}\n"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Обновить Email", callback_data="update_email")],
            [InlineKeyboardButton(text="Обновить номер телефона", callback_data="update_phone_number")],
            [InlineKeyboardButton(text="🔚 Вернуться в главное меню", callback_data="back_to_main")]
        ])

        await edit_or_send_message(callback, profile_info, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await edit_or_send_message(callback, "Профиль не найден. Пожалуйста, зарегистрируйтесь.", reply_markup=kb.main)
