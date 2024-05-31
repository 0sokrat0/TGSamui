# app/admin.py
import logging
from datetime import time, datetime

import pandas as pd
from aiogram import F, Router, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery, FSInputFile
import app.keyboards as kb
from bot import db, bot
from config import ADMINS, db_config
from database.database import Database

db = Database(db_config)

router = Router()

# Кнопки для админ панели
admins_panel = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="📋 Создать карточку"),
            KeyboardButton(text="🗑️ Удалить карточку")
        ],
        [
            KeyboardButton(text="✏️ Редактировать карточку"),
            KeyboardButton(text="📜 Просмотреть все карточки")
        ],
        [
            KeyboardButton(text="📊 Аналитика"),
            KeyboardButton(text="✉️ Создать рассылку"),
            KeyboardButton(text="📄 Экспорт данных")
        ],
        [
            KeyboardButton(text="🔙 Вернуться в меню")
        ]
    ]
)

class AdminProtect:
    async def __call__(self, message: Message):
        return message.from_user.id in ADMINS

# Команда для вызова панели администратора
@router.message(F.text == "⚙️ Админ панель")
async def apanel(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer('Это панель администратора', reply_markup=admins_panel)
    else:
        await message.answer('У вас нет доступа к этой панели.')




# Определение состояний для создания, редактирования и удаления карточек
class NewProperty(StatesGroup):
    waiting_for_name = State()
    waiting_for_photo1 = State()
    waiting_for_photo2 = State()
    waiting_for_photo3 = State()
    waiting_for_photo4 = State()
    waiting_for_photo5 = State()
    waiting_for_photo6 = State()
    waiting_for_photo7 = State()
    waiting_for_photo8 = State()
    waiting_for_photo9 = State()
    waiting_for_location = State()
    waiting_for_distance_to_sea = State()
    waiting_for_property_type = State()
    waiting_for_monthly_price = State()
    waiting_for_daily_price = State()
    waiting_for_booking_deposit_fixed = State()
    waiting_for_security_deposit = State()
    waiting_for_bedrooms = State()
    waiting_for_bathrooms = State()
    waiting_for_pool = State()
    waiting_for_kitchen = State()
    waiting_for_cleaning = State()
    waiting_for_description = State()
    waiting_for_utility_bill = State()
    waiting_for_coordinates = State()
    waiting_for_delete_id = State()
    waiting_for_edit_id = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()
    confirm_deletion = State()
    confirm_edit = State()
    waiting_for_edit_location_coordinates = State()


# Начало создания карточки
@router.message(F.text == "📋 Создать карточку")
async def start_property_creation(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Введите название объекта (или напишите 'Отмена' для отмены действия):")
        await state.set_state(NewProperty.waiting_for_name)
    else:
        await message.answer('У вас нет доступа к этой команде.')

# Ввод названия объекта
@router.message(NewProperty.waiting_for_name)
async def property_name_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(name=message.text)
    await message.answer("Отправьте фото объекта (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_photo1)

# Ввод первого фото
@router.message(NewProperty.waiting_for_photo1, F.photo)
async def property_photo1_received(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo1=photo_id)
    await message.answer("Отправьте второе фото (или напишите /skip для пропуска):")
    await state.set_state(NewProperty.waiting_for_photo2)

# Аналогично обновляем обработчики для остальных фото
@router.message(NewProperty.waiting_for_photo2, F.photo)
async def property_photo2_received(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo2=photo_id)
    await message.answer("Отправьте третье фото (или напишите /skip для пропуска):")
    await state.set_state(NewProperty.waiting_for_photo3)

@router.message(NewProperty.waiting_for_photo3, F.photo)
async def property_photo3_received(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo3=photo_id)
    await message.answer("Отправьте четвертое фото (или напишите /skip для пропуска):")
    await state.set_state(NewProperty.waiting_for_photo4)

@router.message(NewProperty.waiting_for_photo4, F.photo)
async def property_photo4_received(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo4=photo_id)
    await message.answer("Отправьте пятое фото (или напишите /skip для пропуска):")
    await state.set_state(NewProperty.waiting_for_photo5)

@router.message(NewProperty.waiting_for_photo5, F.photo)
async def property_photo5_received(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo5=photo_id)
    await message.answer("Отправьте шестое фото (или напишите /skip для пропуска):")
    await state.set_state(NewProperty.waiting_for_photo6)

@router.message(NewProperty.waiting_for_photo6, F.photo)
async def property_photo6_received(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo6=photo_id)
    await message.answer("Отправьте седьмое фото (или напишите /skip для пропуска):")
    await state.set_state(NewProperty.waiting_for_photo7)

@router.message(NewProperty.waiting_for_photo7, F.photo)
async def property_photo7_received(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo7=photo_id)
    await message.answer("Отправьте восьмое фото (или напишите /skip для пропуска):")
    await state.set_state(NewProperty.waiting_for_photo8)

@router.message(NewProperty.waiting_for_photo8, F.photo)
async def property_photo8_received(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo8=photo_id)
    await message.answer("Отправьте девятое фото (или напишите /skip для пропуска):")
    await state.set_state(NewProperty.waiting_for_photo9)

@router.message(NewProperty.waiting_for_photo9, F.photo)
async def property_photo9_received(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo9=photo_id)
    await message.answer("Введите расположение объекта:")
    await state.set_state(NewProperty.waiting_for_location)

# Обработка пропуска ввода фото
@router.message(F.text == "/skip")
async def skip_photo(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == NewProperty.waiting_for_photo1:
        await state.update_data(photo1=None)
        await message.answer("Отправьте второе фото (или напишите /skip для пропуска):")
        await state.set_state(NewProperty.waiting_for_photo2)
    elif current_state == NewProperty.waiting_for_photo2:
        await state.update_data(photo2=None)
        await message.answer("Отправьте третье фото (или напишите /skip для пропуска):")
        await state.set_state(NewProperty.waiting_for_photo3)
    elif current_state == NewProperty.waiting_for_photo3:
        await state.update_data(photo3=None)
        await message.answer("Отправьте четвертое фото (или напишите /skip для пропуска):")
        await state.set_state(NewProperty.waiting_for_photo4)
    elif current_state == NewProperty.waiting_for_photo4:
        await state.update_data(photo4=None)
        await message.answer("Отправьте пятое фото (или напишите /skip для пропуска):")
        await state.set_state(NewProperty.waiting_for_photo5)
    elif current_state == NewProperty.waiting_for_photo5:
        await state.update_data(photo5=None)
        await message.answer("Отправьте шестое фото (или напишите /skip для пропуска):")
        await state.set_state(NewProperty.waiting_for_photo6)
    elif current_state == NewProperty.waiting_for_photo6:
        await state.update_data(photo6=None)
        await message.answer("Отправьте седьмое фото (или напишите /skip для пропуска):")
        await state.set_state(NewProperty.waiting_for_photo7)
    elif current_state == NewProperty.waiting_for_photo7:
        await state.update_data(photo7=None)
        await message.answer("Отправьте восьмое фото (или напишите /skip для пропуска):")
        await state.set_state(NewProperty.waiting_for_photo8)
    elif current_state == NewProperty.waiting_for_photo8:
        await state.update_data(photo8=None)
        await message.answer("Отправьте девятое фото (или напишите /skip для пропуска):")
        await state.set_state(NewProperty.waiting_for_photo9)
    elif current_state == NewProperty.waiting_for_photo9:
        await state.update_data(photo9=None)
        await message.answer("Введите расположение объекта:")
        await state.set_state(NewProperty.waiting_for_location)

# Ввод расположения объекта
@router.message(NewProperty.waiting_for_location)
async def property_location_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(location=message.text)
    await message.answer("Отправьте геопозицию объекта или введите координаты в формате 9°25'22.9\"N 99°59'32.5\"E (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_coordinates)

# Ввод координат объекта
@router.message(NewProperty.waiting_for_coordinates, F.text)
async def property_coordinates_received_text(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    try:
        coords = message.text.split()
        if len(coords) == 2:
            latitude = coords[0].replace("°", " ").replace("'", " ").replace("\"", "").replace("N", "").replace("S", "-").strip()
            longitude = coords[1].replace("°", " ").replace("'", " ").replace("\"", "").replace("E", "").replace("W", "-").strip()
            await state.update_data(latitude=float(latitude), longitude=float(longitude))
            await proceed_with_next_step(message, state)
        else:
            raise ValueError("Invalid format")
    except Exception as e:
        await message.answer("Неверный формат координат. Пожалуйста, попробуйте снова.")

@router.message(NewProperty.waiting_for_coordinates, F.location)
async def property_coordinates_received_location(message: Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    await state.update_data(latitude=latitude, longitude=longitude)
    await proceed_with_next_step(message, state)

async def proceed_with_next_step(message: Message, state: FSMContext):
    await message.answer("Координаты успешно добавлены.")
    await state.set_state(NewProperty.waiting_for_distance_to_sea)

# Ввод удаленности от моря
@router.message(NewProperty.waiting_for_distance_to_sea)
async def property_distance_to_sea_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(distance_to_sea=message.text)
    await message.answer("Введите тип жилья (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_property_type)

# Ввод типа жилья
@router.message(NewProperty.waiting_for_property_type)
async def property_type_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(property_type=message.text)
    await message.answer("Введите стоимость в месяц (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_monthly_price)

# Ввод стоимости в месяц
@router.message(NewProperty.waiting_for_monthly_price)
async def property_monthly_price_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(monthly_price=message.text)
    await message.answer("Введите стоимость постуточно (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_daily_price)

# Ввод стоимости постуточно
@router.message(NewProperty.waiting_for_daily_price)
async def property_daily_price_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(daily_price=message.text)
    await message.answer("Введите фиксированный депозит для брони (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_booking_deposit_fixed)

# Ввод фиксированного депозита
@router.message(NewProperty.waiting_for_booking_deposit_fixed)
async def property_booking_deposit_fixed_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(booking_deposit_fixed=message.text)
    await message.answer("Введите сохраненный депозит (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_security_deposit)

# Ввод сохраненного депозита
@router.message(NewProperty.waiting_for_security_deposit)
async def property_security_deposit_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(security_deposit=message.text)
    await message.answer("Введите количество спален (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_bedrooms)

# Ввод количества спален
@router.message(NewProperty.waiting_for_bedrooms)
async def property_bedrooms_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(bedrooms=message.text)
    await message.answer("Введите количество ванных комнат (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_bathrooms)

# Ввод количества ванных комнат
@router.message(NewProperty.waiting_for_bathrooms)
async def property_bathrooms_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(bathrooms=message.text)
    await message.answer("Есть ли бассейн? (Да/Нет) (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_pool)

# Ввод информации о бассейне
@router.message(NewProperty.waiting_for_pool)
async def property_pool_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(pool=message.text)
    await message.answer("Есть ли кухня? (Да/Нет) (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_kitchen)

# Ввод информации о кухне
@router.message(NewProperty.waiting_for_kitchen)
async def property_kitchen_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(kitchen=message.text)
    await message.answer("Есть ли уборка? (Да/Нет) (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_cleaning)

# Ввод информации об уборке
@router.message(NewProperty.waiting_for_cleaning)
async def property_cleaning_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(cleaning=message.text)
    await message.answer("Введите описание (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_description)

# Ввод описания объекта
@router.message(NewProperty.waiting_for_description)
async def property_description_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(description=message.text)
    await message.answer("Введите утилиты (вода, электричество и т.д.) (или напишите 'Отмена' для отмены действия):")
    await state.set_state(NewProperty.waiting_for_utility_bill)

# Ввод информации об утилитах
@router.message(NewProperty.waiting_for_utility_bill)
async def property_utility_bill_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(utility_bill=message.text)
    await db.ensure_connection()

    property_data = await state.get_data()

    query = """
    INSERT INTO properties (name, photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8, photo9, location, distance_to_sea, property_type,
                            monthly_price, daily_price, booking_deposit_fixed, security_deposit, bedrooms, bathrooms, pool, kitchen, cleaning, description, utility_bill, latitude, longitude)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    params = (
        property_data.get('name'), property_data.get('photo1'), property_data.get('photo2'),
        property_data.get('photo3'), property_data.get('photo4'), property_data.get('photo5'),
        property_data.get('photo6'), property_data.get('photo7'), property_data.get('photo8'),
        property_data.get('photo9'), property_data.get('location'), property_data.get('distance_to_sea'),
        property_data.get('property_type'), property_data.get('monthly_price'), property_data.get('daily_price'),
        property_data.get('booking_deposit_fixed'), property_data.get('security_deposit'),
        property_data.get('bedrooms'), property_data.get('bathrooms'), property_data.get('pool'),
        property_data.get('kitchen'), property_data.get('cleaning'), property_data.get('description'),
        property_data.get('utility_bill'), property_data.get('latitude'), property_data.get('longitude')
    )

    if len(params) != 26:  # 26 это количество ожидаемых параметров
        print("Количество параметров не соответствует ожидаемому. Ожидается 26, получено:", len(params))
    else:
        try:
            async with db.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    await conn.commit()
            await message.answer("Карточка недвижимости успешно создана!", reply_markup=admins_panel)
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            await message.answer(f"Произошла ошибка при создании карточки: {e}")
        await state.clear()

    # try:
    #     async with db.pool.acquire() as conn:
    #         async with conn.cursor() as cursor:
    #             await cursor.execute(query, params)
    #             await conn.commit()
    #     await message.answer("Карточка недвижимости успешно создана!", reply_markup=admins_panel)
    # except Exception as e:
    #     logging.error(f"Error executing query: {e}")
    #     await message.answer(f"Произошла ошибка при создании карточки: {e}")
    #
    # await state.clear()

async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=admins_panel)

# Начало удаления карточки
@router.message(F.text == "🗑️ Удалить карточку")
async def start_property_deletion(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    if message.from_user.id in ADMINS:
        await message.answer("Введите ID карточки недвижимости, которую вы хотите удалить (или напишите 'Отмена' для отмены действия):")
        await state.set_state(NewProperty.waiting_for_delete_id)
    else:
        await message.answer('У вас нет доступа к этой команде.')

# Ввод ID карточки для удаления
@router.message(NewProperty.waiting_for_delete_id)
async def delete_property_id_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    property_id = message.text
    await db.ensure_connection()

    query = "DELETE FROM properties WHERE property_id = %s"
    params = (property_id,)

    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            await conn.commit()

    await message.answer(f"Карточка недвижимости с ID {property_id} успешно удалена!", reply_markup=admins_panel)
    await state.clear()

# Начало редактирования карточки
edit_field_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Название", callback_data="edit_name"),
            InlineKeyboardButton(text="Фото 1", callback_data="edit_photo1"),
            InlineKeyboardButton(text="Фото 2", callback_data="edit_photo2")
        ],
        [
            InlineKeyboardButton(text="Фото 3", callback_data="edit_photo3"),
            InlineKeyboardButton(text="Фото 4", callback_data="edit_photo4"),
            InlineKeyboardButton(text="Фото 5", callback_data="edit_photo5"),
            InlineKeyboardButton(text="Фото 6", callback_data="edit_photo6")
        ],
        [
            InlineKeyboardButton(text="Фото 7", callback_data="edit_photo7"),
            InlineKeyboardButton(text="Фото 8", callback_data="edit_photo8"),
            InlineKeyboardButton(text="Фото 9", callback_data="edit_photo9")
        ],
        [
            InlineKeyboardButton(text="Расположение", callback_data="edit_location"),
            InlineKeyboardButton(text="Удаленность от моря", callback_data="edit_distance_to_sea"),
            InlineKeyboardButton(text="Тип жилья", callback_data="edit_property_type")
        ],
        [
            InlineKeyboardButton(text="Цена в месяц", callback_data="edit_monthly_price"),
            InlineKeyboardButton(text="Цена постуточно", callback_data="edit_daily_price"),
            InlineKeyboardButton(text="Мин. ночей", callback_data="edit_minimum_nights")
        ],
        [
            InlineKeyboardButton(text="Фикс. депозит", callback_data="edit_booking_deposit_fixed"),
            InlineKeyboardButton(text="Процент. депозит", callback_data="edit_booking_deposit_percent"),
            InlineKeyboardButton(text="Сохраненный депозит", callback_data="edit_security_deposit")
        ],
        [
            InlineKeyboardButton(text="Спальни", callback_data="edit_bedrooms"),
            InlineKeyboardButton(text="Кровати", callback_data="edit_beds"),
            InlineKeyboardButton(text="Ванные комнаты", callback_data="edit_bathrooms")
        ],
        [
            InlineKeyboardButton(text="Бассейн", callback_data="edit_pool"),
            InlineKeyboardButton(text="Кухня", callback_data="edit_kitchen"),
            InlineKeyboardButton(text="Кондиционеры", callback_data="edit_air_conditioners")
        ],
        [
            InlineKeyboardButton(text="Уборка", callback_data="edit_cleaning"),
            InlineKeyboardButton(text="Описание", callback_data="edit_description"),
            InlineKeyboardButton(text="Утилиты", callback_data="edit_utility_bill")
        ],
        [
            InlineKeyboardButton(text="Широта", callback_data="edit_latitude"),
            InlineKeyboardButton(text="Долгота", callback_data="edit_longitude"),
            InlineKeyboardButton(text="Координаты", callback_data="edit_coordinates")
        ]
    ]
)

# Начало редактирования карточки
@router.message(F.text == "✏️ Редактировать карточку")
async def start_property_editing(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    if message.from_user.id in ADMINS:
        await message.answer("Введите ID карточки недвижимости, которую вы хотите отредактировать(или напишите 'Отмена' для отмены действия):")
        await state.set_state(NewProperty.waiting_for_edit_id)
    else:
        await message.answer('У вас нет доступа к этой команде.')

# Ввод ID карточки для редактирования
@router.message(NewProperty.waiting_for_edit_id)
async def edit_property_id_received(message: Message, state: FSMContext):
    property_id = message.text
    await state.update_data(property_id=property_id)

    await db.ensure_connection()

    query = "SELECT * FROM properties WHERE property_id = %s"
    params = (property_id,)

    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            property = await cursor.fetchone()

    if property:
        await message.answer(f"Текущие данные карточки:\n{property}\n\nВыберите поле, которое вы хотите отредактировать:", reply_markup=edit_field_buttons)
        await state.set_state(NewProperty.waiting_for_edit_field)
    else:
        await message.answer("Карточка с указанным ID не найдена.", reply_markup=admins_panel)
        await state.clear()



# @router.callback_query(NewProperty.waiting_for_edit_field, F.data == "edit_coordinates")
# async def edit_property_coordinates(callback_query: CallbackQuery, state: FSMContext):
#     await state.set_state(NewProperty.waiting_for_edit_location_coordinates)
#     await callback_query.message.answer("Отправьте новое местоположение или координаты в формате 9°25'22.9\"N 99°59'32.5\"E (или напишите 'Отмена' для отмены действия):")
#     await callback_query.answer()


@router.callback_query(NewProperty.waiting_for_edit_field)
async def edit_property_field_received(callback_query: types.CallbackQuery, state: FSMContext):
    selected_field = callback_query.data.replace("edit_", "")

    # Проверка, если выбранное поле "coordinates"
    if selected_field == "coordinates":
        await state.update_data(selected_field="latitude_longitude")
        await callback_query.message.answer(
            "Отправьте новое местоположение или координаты в формате 9°25'22.9\"N 99°59'32.5\"E (или напишите 'Отмена' для отмены действия):")
        await state.set_state(NewProperty.waiting_for_edit_location_coordinates)
    else:
        await state.update_data(selected_field=selected_field)
        await callback_query.message.answer(
            f"Введите новое значение для поля {selected_field}(или напишите 'Отмена' для отмены действия):")
        await state.set_state(NewProperty.waiting_for_edit_value)
    await callback_query.answer()


@router.message(NewProperty.waiting_for_edit_location_coordinates, F.location)
async def property_new_location_received_location(message: Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    await state.update_data(new_value_location=(latitude, longitude))
    await message.answer(f"Вы уверены, что хотите изменить местоположение на ({latitude}, {longitude})? (Да/Нет)")
    await state.set_state(NewProperty.confirm_edit)


@router.message(NewProperty.waiting_for_edit_location_coordinates, F.text)
async def property_new_location_received_text(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    try:
        coords = message.text.split()
        if len(coords) == 2:
            latitude = coords[0].replace("°", " ").replace("'", " ").replace("\"", "").replace("N", "").replace("S",
                                                                                                                "-").strip()
            longitude = coords[1].replace("°", " ").replace("'", " ").replace("\"", "").replace("E", "").replace("W",
                                                                                                                 "-").strip()
            await state.update_data(new_value_location=(float(latitude), float(longitude)))
            await message.answer(
                f"Вы уверены, что хотите изменить местоположение на ({latitude}, {longitude})? (Да/Нет)")
            await state.set_state(NewProperty.confirm_edit)
        else:
            raise ValueError("Invalid format")
    except Exception as e:
        await message.answer("Неверный формат координат. Пожалуйста, попробуйте снова.")


@router.message(NewProperty.confirm_edit)
async def confirm_property_edit(message: Message, state: FSMContext):
    confirmation = message.text.lower()
    if confirmation == "да":
        data = await state.get_data()
        property_id = data['property_id']
        selected_field = data.get('selected_field')

        await db.ensure_connection()

        if selected_field == "latitude_longitude":
            latitude, longitude = data.get('new_value_location')
            query = f"UPDATE properties SET latitude = %s, longitude = %s WHERE property_id = %s"
            params = (latitude, longitude, property_id)
        else:
            new_value = data.get('new_value')
            query = f"UPDATE properties SET {selected_field} = %s WHERE property_id = %s"
            params = (new_value, property_id)

        try:
            async with db.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    await conn.commit()
            if selected_field == "latitude_longitude":
                await message.answer(f"Местоположение карточки недвижимости с ID {property_id} успешно обновлено!",
                                     reply_markup=admins_panel)
            else:
                await message.answer(
                    f"Поле {selected_field} карточки недвижимости с ID {property_id} успешно обновлено!",
                    reply_markup=admins_panel)
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            await message.answer(f"Произошла ошибка при обновлении карточки: {e}")
    else:
        await message.answer("Редактирование отменено.", reply_markup=admins_panel)

    await state.clear()


# Ввод поля для редактирования через кнопки
@router.callback_query(NewProperty.waiting_for_edit_field)
async def edit_property_field_received(callback_query: types.CallbackQuery, state: FSMContext):
    selected_field = callback_query.data.replace("edit_", "")
    await state.update_data(selected_field=selected_field)
    await callback_query.message.answer(f"Введите новое значение для поля {selected_field}(или напишите 'Отмена' для отмены действия)::")
    await state.set_state(NewProperty.waiting_for_edit_value)
    await callback_query.answer()


@router.message(NewProperty.waiting_for_edit_value, F.photo)
async def edit_property_value_received_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    property_id = data['property_id']
    selected_field = data['selected_field']

    await state.update_data(new_value=photo_id)
    await message.answer(f"Вы уверены, что хотите изменить поле '{selected_field}' на новое фото? (Да/Нет)")
    await state.set_state(NewProperty.confirm_edit)

@router.message(NewProperty.waiting_for_edit_value, F.text)
async def edit_property_value_received_text(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    data = await state.get_data()
    property_id = data['property_id']
    selected_field = data['selected_field']
    new_value = message.text

    await state.update_data(new_value=new_value)
    await message.answer(f"Вы уверены, что хотите изменить поле '{selected_field}' на '{new_value}'? (Да/Нет)")
    await state.set_state(NewProperty.confirm_edit)

# Подтверждение редактирования карточки
@router.message(NewProperty.confirm_edit)
async def confirm_property_edit(message: Message, state: FSMContext):
    confirmation = message.text.lower()
    if confirmation == "да":
        data = await state.get_data()
        property_id = data['property_id']
        selected_field = data['selected_field']
        new_value = data['new_value']

        await db.ensure_connection()

        query = f"UPDATE properties SET {selected_field} = %s WHERE property_id = %s"
        params = (new_value, property_id)

        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()

        await message.answer(f"Поле {selected_field} карточки недвижимости с ID {property_id} успешно обновлено!", reply_markup=admins_panel)
    else:
        await message.answer("Редактирование отменено.", reply_markup=admins_panel)

    await state.clear()

# Просмотр всех карточек
@router.message(F.text == "📜 Просмотреть все карточки")
async def view_all_properties(message: Message):
    if message.from_user.id in ADMINS:
        await db.ensure_connection()

        query = "SELECT property_id, name FROM properties"

        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                properties = await cursor.fetchall()

        if properties:
            response = "Список всех объектов недвижимости:\n\n"
            for prop in properties:
                response += f"ID: {prop[0]}, Название: {prop[1]}\n"
            await message.answer(response,reply_markup=admins_panel)
        else:
            await message.answer("Нет доступных объектов недвижимости.")
    else:
        await message.answer('У вас нет доступа к этой команде.')

# Возврат в главное меню
@router.message(F.text == "🔙 Вернуться в меню")
async def return_to_main_menu(message: Message):
    await message.answer("Возвращение в главное меню...", reply_markup=kb.main)

# Функция для создания новой рассылк


class Newsletter(StatesGroup):
    waiting_for_subject = State()
    waiting_for_message = State()
    waiting_for_photo = State()
    confirm_sending = State()



async def log_user_action(property_id: int, user_id: int, action: str):
    await db.ensure_connection()

    query = """
    INSERT INTO analytics (property_id, user_id, action)
    VALUES (%s, %s, %s)
    """
    params = (property_id, user_id, action)

    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            await conn.commit()


# Логика создания рассылки

# Функция для создания новой рассылки
async def create_newsletter(subject: str, message: str, photo: str = None):
    await db.ensure_connection()

    query = """
    INSERT INTO newsletters (subject, message, photo)
    VALUES (%s, %s, %s)
    """
    params = (subject, message, photo)

    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            await conn.commit()



# Функция для записи получателя рассылки
async def log_newsletter_recipient(newsletter_id: int, user_id: int):
    await db.ensure_connection()

    query = """
    INSERT INTO newsletter_recipients (newsletter_id, user_id)
    VALUES (%s, %s)
    """
    params = (newsletter_id, user_id)

    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            await conn.commit()


# Начало создания рассылки
@router.message(F.text == "✉️ Создать рассылку")
async def start_newsletter_creation(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Введите тему рассылки:")
        await state.set_state(Newsletter.waiting_for_subject)
    else:
        await message.answer('У вас нет доступа к этой команде.')


# Ввод темы рассылки
@router.message(Newsletter.waiting_for_subject)
async def newsletter_subject_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(subject=message.text)
    await message.answer("Введите текст рассылки:")
    await state.set_state(Newsletter.waiting_for_message)


# Ввод текста рассылки
@router.message(Newsletter.waiting_for_message)
async def newsletter_message_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(message=message.text)
    await message.answer("Отправьте фото для рассылки (если есть) или нажмите /skip:")
    await state.set_state(Newsletter.waiting_for_photo)


# Ввод фото или текста для рассылки
@router.message(Newsletter.waiting_for_photo, F.photo)
async def newsletter_photo_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    photo = message.photo[-1].file_id
    await state.update_data(photo=photo)
    await message.answer("Фото добавлено. Вы уверены, что хотите отправить эту рассылку всем пользователям? (Да/Нет)")
    await state.set_state(Newsletter.confirm_sending)


@router.message(Newsletter.waiting_for_photo, F.text)
async def newsletter_text_received(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await cancel_action(message, state)
        return
    await state.update_data(photo=None)
    await message.answer("Вы уверены, что хотите отправить эту рассылку всем пользователям? (Да/Нет)")
    await state.set_state(Newsletter.confirm_sending)


@router.message(Newsletter.confirm_sending)
async def confirm_newsletter_sending(message: Message, state: FSMContext):
    confirmation = message.text.lower()
    if confirmation == "да":
        data = await state.get_data()
        subject = data['subject']
        message_text = data['message']
        photo = data.get('photo')

        await create_newsletter(subject, message_text, photo)

        await db.ensure_connection()

        query = "SELECT user_id FROM users WHERE notifications_enabled = TRUE"

        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                users = await cursor.fetchall()

        for user in users:
            user_id = user[0]
            try:
                if photo:
                    await bot.send_photo(user_id, photo=photo, caption=f"{subject}\n\n{message_text}")
                else:
                    await bot.send_message(user_id, text=f"{subject}\n\n{message_text}")
            except Exception as e:
                logging.exception(f"Failed to send notification to user {user_id}: {e}")

        await message.answer("Рассылка успешно отправлена всем пользователям!", reply_markup=admins_panel)
    else:
        await message.answer("Рассылка отменена.", reply_markup=admins_panel)

    await state.clear()


# Функция для отправки рассылки конкретному пользователю
async def send_newsletter_to_user(user_id: int, subject: str, message_text: str, photo: str = None):
    try:
        if photo:
            await bot.send_photo(user_id, photo=photo, caption=f"{subject}\n\n{message_text}")
        else:
            await bot.send_message(user_id, text=f"{subject}\n\n{message_text}")
    except Exception as e:
        logging.exception(f"Failed to send notification to user {user_id}: {e}")






# @router.callback_query(F.data == "subscribe_notifications")
# async def subscribe_notifications(callback_query: CallbackQuery):
#     await db.ensure_connection()
#     await db.update_last_activity(callback_query.from_user.id)
#     user_id = callback_query.from_user.id
#
#     await db.subscribe_to_notifications(user_id)
#     await callback_query.message.answer("Вы успешно подписаны на уведомления!", reply_markup=kb.main)
#     await callback_query.answer()
#
#
# @router.callback_query(F.data == "unsubscribe_notifications")
# async def unsubscribe_notifications(callback_query: CallbackQuery):
#     await db.ensure_connection()
#     await db.update_last_activity(callback_query.from_user.id)
#     user_id = callback_query.from_user.id
#
#     await db.unsubscribe_from_notifications(user_id)
#     await callback_query.message.answer("Вы успешно отписаны от уведомлений.", reply_markup=kb.main)
#     await callback_query.answer()


@router.message(F.text == "📊 Аналитика")
async def show_analytics(message: Message):
    if message.from_user.id in ADMINS:
        await db.ensure_connection()

        stats = await db.get_detailed_user_statistics()
        response_text = (
            f"📊 <b>Аналитика активности пользователей:</b>\n\n"
            f"👥 <b>Всего пользователей:</b> {stats['total_users']}\n"
            f"🟢 <b>Активные пользователи (за последнюю неделю):</b> {stats['active_users']}\n"
            f"🆕 <b>Новые пользователи (за последнюю неделю):</b> {stats['new_users']}\n"
        )

        await message.answer(response_text, parse_mode="HTML",reply_markup=admins_panel)
    else:
        await message.answer('У вас нет доступа к этой команде.')


@router.message(F.text == "Отмена")
async def cancel_action(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("Действие отменено. Возвращение в панель администратора.", reply_markup=admins_panel)
    else:
        await message.answer("Нет активных действий для отмены.", reply_markup=admins_panel)



# Кнопки для экспорта данных
export_buttons = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[
        [KeyboardButton(text="📄 Экспорт карточек")],
        [KeyboardButton(text="📄 Экспорт пользователей")],
        [KeyboardButton(text="🔙 Вернуться в меню")]
    ]
)

# Меню экспорта данных
@router.message(F.text == "📄 Экспорт данных")
async def export_data_menu(message: Message):
    await message.answer("Выберите данные для экспорта:", reply_markup=export_buttons)

# Экспорт данных о карточках
@router.message(F.text == "📄 Экспорт карточек")
async def export_properties(message: Message):
    try:
        await db.ensure_connection()
        query = "SELECT * FROM properties"

        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                data = await cursor.fetchall()

        if data:
            df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
            file_path = 'properties_export.xlsx'
            df.to_excel(file_path, index=False)
            file = FSInputFile(file_path)
            await message.answer_document(
                file,
                caption=f'Актуальный на <b>{datetime.now().strftime("%d-%m-%Y")}</b>',
                parse_mode='HTML'
            )
        else:
            await message.answer("Нет данных для экспорта.")
    except Exception as e:
        await message.answer(f"Ошибка при экспорте данных: {str(e)}")

# Экспорт данных о пользователях
@router.message(F.text == "📄 Экспорт пользователей")
async def export_users(message: Message):
    try:
        await db.ensure_connection()
        query = "SELECT * FROM users"

        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                data = await cursor.fetchall()

        if data:
            df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
            file_path = 'users_export.xlsx'
            df.to_excel(file_path, index=False)
            file = FSInputFile(file_path)
            await message.answer_document(
                file,
                caption=f'Актуальный на <b>{datetime.now().strftime("%d-%m-%Y")}</b>',
                parse_mode='HTML'
            )
        else:
            await message.answer("Нет данных для экспорта.")
    except Exception as e:
        await message.answer(f"Ошибка при экспорте данных: {str(e)}")