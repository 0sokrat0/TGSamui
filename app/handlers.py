import asyncio
import json
import logging
import aiomysql
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from config import db_config, ADMINS
from database.database import Database
from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
import app.keyboards as kb
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
        await message.answer('Пожалуйста, нажмите на кнопку ниже, чтобы отправить ваш номер телефона.', reply_markup=kb.numbers)
        await message.answer('Вы успешно зарегистрированы. Добро пожаловать!', reply_markup=kb.main if user_id not in ADMINS else kb.admin_main)



@router.callback_query(F.data == "back_to_favorites")
async def back_to_favorites(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    user_id = callback_query.from_user.id
    favorite_ids = await get_favorite_properties(user_id)
    if not favorite_ids:
        await callback_query.message.answer("У вас нет избранных объектов.")
        return

    # Получить информацию о каждой избранной вилле
    favorites = []
    for property_id in favorite_ids:
        property = await get_property_by_id(property_id)
        if property:
            favorites.append(property)

    if not favorites:
        await callback_query.message.answer("У вас нет избранных объектов.")
        return

    # Создание кнопок с именами вилл
    buttons = [
        [InlineKeyboardButton(text=f"{property['name']}", callback_data=f"show_{property['property_id']}")]
        for property in favorites
    ]

    # Добавление кнопки "Возврат в меню"
    buttons.append([InlineKeyboardButton(text="🔙 Возврат в меню", callback_data="back_to_menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback_query.message.answer("Ваши избранные объекты:", reply_markup=keyboard)




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


async def get_favorites(user_id, offset=0, limit=5):
    query = """
    SELECT p.*
    FROM properties p
    WHERE p.property_id IN (
        SELECT property1 FROM favorites WHERE user_id = %s
        UNION
        SELECT property2 FROM favorites WHERE user_id = %s
        UNION
        SELECT property3 FROM favorites WHERE user_id = %s
        UNION
        SELECT property4 FROM favorites WHERE user_id = %s
        UNION
        SELECT property5 FROM favorites WHERE user_id = %s
        UNION
        SELECT property6 FROM favorites WHERE user_id = %s
        UNION
        SELECT property7 FROM favorites WHERE user_id = %s
        UNION
        SELECT property8 FROM favorites WHERE user_id = %s
    )
    LIMIT %s OFFSET %s
    """
    params = (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, limit, offset)

    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params)
            results = await cursor.fetchall()
            return results

async def get_favorite_properties(user_id):
    query = """
    SELECT property1, property2, property3, property4, property5, property6, property7, property8
    FROM favorites
    WHERE user_id = %s
    """
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, (user_id,))
            result = await cursor.fetchone()
            if result:
                return [result[key] for key in result if result[key] is not None]
            return []



@router.message(F.text == "📌 Избранное")
async def show_favorites(message: Message):
    await ensure_db_connection()
    user_id = message.from_user.id

    favorite_ids = await get_favorite_properties(user_id)
    if not favorite_ids:
        await message.answer("У вас нет избранных объектов/или объект удален")
        return

    # Получить информацию о каждой избранной вилле
    favorites = []
    for property_id in favorite_ids:
        property = await get_property_by_id(property_id)
        if property:
            favorites.append(property)

    if not favorites:
        await message.answer("У вас нет избранных объектов.")
        return

    # Создание кнопок с именами вилл
    buttons = [
        [InlineKeyboardButton(text=f"{property['name']}", callback_data=f"show_{property['property_id']}")]
        for property in favorites
    ]

    # Добавление кнопки "Возврат в меню"
    buttons.append([InlineKeyboardButton(text="🔙 Возврат в меню", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("Ваши избранные объекты:", reply_markup=keyboard)

@router.callback_query(F.data.startswith('show_'))
async def show_property_info(callback_query: CallbackQuery, state: FSMContext):
    property_id = int(callback_query.data.split('_')[1])
    property = await get_property_by_id(property_id)

    if not property:
        await callback_query.answer("Объект не найден.")
        return

    avg_rating = property.get('avg_rating', 'Нет рейтинга')
    if avg_rating != 'Нет рейтинга':
        avg_rating = f"⭐ {avg_rating:.1f}"

    text = (
        f"🏠 <b>{property['name']}</b>\n\n"
        f"📍 <b>Расположение:</b> {property['location']}\n"
        f"🌊 <b>Удаленность от моря:</b> {property['distance_to_sea']}\n"
        f"🏷️ <b>Категория:</b> {property['property_type']}\n\n"
        f"💰 <b>Стоимость в месяц:</b> {property['monthly_price']}฿\n"
        f"💰 <b>Стоимость постуточно:</b> {property['daily_price']}฿\n"
        f"💵 <b>Залог:</b> {property['booking_deposit_fixed']}฿\n"
        f"🔒 <b>Сохраненный депозит:</b> {property['security_deposit']}฿\n\n"
        f"🛏️ <b>Количество спален:</b> {property['bedrooms']}\n"
        f"🛁 <b>Количество ванных:</b> {property['bathrooms']}\n"
        f"🏊 <b>Бассейн:</b> {'Да' if property['pool'] else 'Нет'}\n"
        f"🍴 <b>Кухня:</б> {'Да' if property['kitchen'] else 'Нет'}\n"
        f"🧹 <b>Уборка:</b> {'Да' if property['cleaning'] else 'Нет'}\n"
        f"💡 <b>Утилиты:</b> {property['utility_bill']}\n\n"
        f"📜 <b>Описание:</б> {property['description']}\n\n"
        f"🌟 <b>Средний рейтинг:</б> {avg_rating}\n"
    ).replace("</б>", "</b>")

    buttons = [
        [InlineKeyboardButton(text="📞 Связь с менеджером", url="https://t.me/tropicalsamui")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del_{property['property_id']}"),
         InlineKeyboardButton(text="🗺 На карте", callback_data=f"map_{property['property_id']}")],
        [InlineKeyboardButton(text="✍️ Оставить отзыв и рейтинг", callback_data=f"review_{property['property_id']}"),
         InlineKeyboardButton(text="📖 Читать отзывы и рейтинги", callback_data=f"read_reviews_{property['property_id']}")],
        [InlineKeyboardButton(text="🔙 Возврат к избранным", callback_data="back_to_favorites")]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    photos = [property[f'photo{i}'] for i in range(1, 10) if property[f'photo{i}']]

    if photos:
        media = [InputMediaPhoto(media=photos[0], caption=text, parse_mode=ParseMode.HTML)]
        media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])

        try:
            if callback_query.message.photo:
                await callback_query.message.delete()

            await callback_query.message.answer_media_group(media=media)
            await callback_query.message.answer("Выберите действие:", reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Error sending media group: {e}")
            await callback_query.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)



@router.callback_query(F.data.startswith('map_'))
async def show_on_map(callback_query: CallbackQuery):
    property_id = int(callback_query.data.split('_')[1])
    await db.ensure_connection()
    query = "SELECT latitude, longitude FROM properties WHERE property_id = %s"
    params = (property_id,)
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params)
            result = await cursor.fetchone()

    if result:
        latitude, longitude = result['latitude'], result['longitude']
        if latitude is not None and longitude is not None:
            openstreetmap_url = f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=18/{latitude}/{longitude}"
            await callback_query.message.answer(f"Расположение на карте: {openstreetmap_url}")
        else:
            await callback_query.message.answer("Координаты для этой недвижимости не указаны.")
    else:
        await callback_query.message.answer("Недвижимость с указанным ID не найдена.")
    await callback_query.answer()


class ReviewStates(StatesGroup):
    waiting_for_review = State()
    waiting_for_rating = State()


@router.callback_query(F.data.startswith('review_'))
async def start_review(callback_query: CallbackQuery, state: FSMContext):
    property_id = int(callback_query.data.split('_')[1])
    await state.update_data(property_id=property_id)
    await callback_query.message.answer("Пожалуйста, введите ваш отзыв (вы можете использовать эмоджи):")
    await callback_query.answer()
    await state.set_state(ReviewStates.waiting_for_review)

@router.message(ReviewStates.waiting_for_review)
async def process_review(message: Message, state: FSMContext):
    review_data = await state.get_data()
    property_id = review_data["property_id"]
    review = message.text
    user_id = message.from_user.id
    username = message.from_user.username

    await db.ensure_connection()

    # Вставка нового отзыва
    insert_query = "INSERT INTO reviews (property_id, user_id, username, review, created_at) VALUES (%s, %s, %s, %s, NOW())"
    insert_params = (property_id, user_id, username, review)
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(insert_query, insert_params)
            await conn.commit()

    await message.answer("Спасибо за ваш отзыв! Теперь введите ваш рейтинг от 1 до 5 звезд:")
    await state.set_state(ReviewStates.waiting_for_rating)

@router.message(ReviewStates.waiting_for_rating)
async def process_rating(message: Message, state: FSMContext):
    rating = int(message.text)
    if rating < 1 or rating > 5:
        await message.answer("Пожалуйста, введите число от 1 до 5.")
        return

    data = await state.get_data()
    property_id = data['property_id']
    user_id = message.from_user.id

    await db.ensure_connection()

    query = """
    UPDATE reviews
    SET rating = %s
    WHERE property_id = %s AND user_id = %s
    ORDER BY created_at DESC
    LIMIT 1
    """
    params = (rating, property_id, user_id)

    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            await conn.commit()

    await message.answer("Спасибо за ваш рейтинг!", reply_markup=kb.main)
    await state.clear()

@router.callback_query(F.data.startswith('read_reviews_'))
async def read_reviews(callback_query: CallbackQuery):
    property_id = int(callback_query.data.split('_')[2])
    await db.ensure_connection()

    query_reviews = "SELECT username, review, rating, created_at FROM reviews WHERE property_id = %s"
    params = (property_id,)

    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query_reviews, params)
            reviews = await cursor.fetchall()

    if reviews:
        response = "Отзывы о недвижимости:\n\n"
        for review in reviews:
            rating = review['rating'] if review['rating'] is not None else 0
            stars = '★' * rating + '☆' * (5 - rating)
            response += f"@{review['username']} ({review['created_at']}):\n{review['review']}\nРейтинг: {stars}\n\n"
    else:
        response = "Нет отзывов для данной недвижимости."

    await callback_query.message.answer(response)
    await callback_query.answer()


async def get_property_by_id(property_id):
    query_property = "SELECT * FROM properties WHERE property_id = %s"
    query_rating = "SELECT AVG(rating) as avg_rating FROM reviews WHERE property_id = %s"

    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query_property, (property_id,))
            property = await cursor.fetchone()

            if property:
                await cursor.execute(query_rating, (property_id,))
                rating_result = await cursor.fetchone()
                property['avg_rating'] = rating_result['avg_rating'] if rating_result else None

            return property


@router.callback_query(F.data.startswith('fav_'))
async def add_to_favorites_handler(callback_query: CallbackQuery, state: FSMContext):
    property_id = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id
    await add_to_favorites(user_id, property_id)
    await callback_query.answer("Добавлено в избранное!")

async def add_to_favorites(user_id, property_id):
    query_check = "SELECT property1, property2, property3, property4, property5, property6, property7, property8 FROM favorites WHERE user_id = %s"
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query_check, (user_id,))
            result = await cursor.fetchone()

            if result:
                properties = [result[f'property{i}'] for i in range(1, 9)]
                if property_id not in properties:
                    for i in range(8):
                        if properties[i] is None:
                            properties[i] = property_id
                            break
                    update_query = """
                    UPDATE favorites 
                    SET property1 = %s, property2 = %s, property3 = %s, property4 = %s, property5 = %s, property6 = %s, property7 = %s, property8 = %s 
                    WHERE user_id = %s
                    """
                    await cursor.execute(update_query, (*properties, user_id))
            else:
                insert_query = "INSERT INTO favorites (user_id, property1) VALUES (%s, %s)"
                await cursor.execute(insert_query, (user_id, property_id))

            await conn.commit()

@router.callback_query(F.data.startswith('del_'))
async def remove_from_favorites_handler(callback_query: CallbackQuery, state: FSMContext):
    property_id = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id
    await remove_from_favorites(user_id, property_id)
    await callback_query.answer("Удалено из избранного!")
    await show_favorites(callback_query.message)

async def remove_from_favorites(user_id, property_id):
    query_check = "SELECT property1, property2, property3, property4, property5, property6, property7, property8 FROM favorites WHERE user_id = %s"
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query_check, (user_id,))
            result = await cursor.fetchone()

            if result:
                properties = [result[f'property{i}'] for i in range(1, 9)]
                if property_id in properties:
                    properties[properties.index(property_id)] = None
                    update_query = """
                    UPDATE favorites 
                    SET property1 = %s, property2 = %s, property3 = %s, property4 = %s, property5 = %s, property6 = %s, property7 = %s, property8 = %s 
                    WHERE user_id = %s
                    """
                    await cursor.execute(update_query, (*properties, user_id))
                    await conn.commit()


class ProfileUpdate(StatesGroup):
    waiting_for_email = State()
    waiting_for_phone_number = State()
    confirming_email = State()
    confirming_phone_number = State()

@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    user_info = await db.get_user_info(message.from_user.id)
    if user_info:
        profile_info = (
            f"👤 <b>Ваш Профиль</b>\n\n"
            f"🔹 <b>Имя пользователя:</b> {user_info[1]}\n"  # username
            f"🔹 <b>Номер телефона:</b> {user_info[3]}\n"  # phone_number
            f"🔹 <b>Email:</b> {user_info[2] if user_info[2] else 'Не указан'}\n"  # email
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Обновить Email", callback_data="update_email")],
            [InlineKeyboardButton(text="Обновить номер телефона", callback_data="update_phone_number")],
            [InlineKeyboardButton(text="🔚 Вернуться в главное меню", callback_data="back_to_main")]
        ])

        await message.answer(profile_info, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await message.answer("Профиль не найден. Пожалуйста, зарегистрируйтесь.", reply_markup=kb.main)


@router.callback_query(F.data == "update_email")
async def prompt_for_email(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, введите ваш новый email:")
    await callback.answer()
    await state.set_state(ProfileUpdate.waiting_for_email)


@router.callback_query(F.data == "update_phone_number")
async def prompt_for_phone_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, нажмите на кнопку ниже, чтобы отправить ваш новый номер телефона.", reply_markup=kb.numbers)
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



class PropertyFilter(StatesGroup):
    choosing_type = State()
    choosing_beds = State()
    choosing_distance = State()
    choosing_price = State()
    showing_results = State()

@router.message(F.text == "🏠 Поиск недвижимости")
async def search_real_estate(message: Message, state: FSMContext):
    types = ["Вилла", "Кондо", "Апартаменты", "Дом в резорте", "Cтудия в резорте"]
    buttons = [[InlineKeyboardButton(text=t, callback_data=f"type_{t}")] for t in types]
    buttons.append([InlineKeyboardButton(text="Пропустить", callback_data="skip_all")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите тип жилья или пропустите:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_type)

@router.callback_query(F.data == "skip_all")
async def skip_all_filters(callback_query: CallbackQuery, state: FSMContext):
    properties = await get_properties(db)
    await state.update_data(properties=properties, page=0)
    await show_property_page(callback_query.message, state)
    await state.set_state(PropertyFilter.showing_results)

@router.callback_query(F.data.startswith('type_'))
async def choose_beds(callback_query: CallbackQuery, state: FSMContext):
    property_type = callback_query.data.split('_')[1]
    await state.update_data(property_type=property_type)

    beds_options = ["1", "2", "3", "4", "5", "Любое количество"]
    buttons = [[InlineKeyboardButton(text=f"{beds} спальни", callback_data=f"beds_{beds}")] for beds in beds_options]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.edit_text("Выберите количество спален или пропустите:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_beds)

@router.callback_query(F.data == "skip_beds")
async def skip_beds_filter(callback_query: CallbackQuery, state: FSMContext):
    await choose_distance(callback_query, state)

@router.callback_query(F.data.startswith('beds_'))
async def choose_distance(callback_query: CallbackQuery, state: FSMContext):
    number_of_beds = callback_query.data.split('_')[1]
    await state.update_data(number_of_beds=number_of_beds if number_of_beds != "Любое количество" else None)

    distances = ["<100м", "100-500м", ">500м", "Любое расстояние"]
    buttons = [[InlineKeyboardButton(text=distance, callback_data=f"distance_{distance}")] for distance in distances]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.edit_text("Выберите удаленность от моря или пропустите:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_distance)

@router.callback_query(F.data == "skip_distance")
async def skip_distance_filter(callback_query: CallbackQuery, state: FSMContext):
    await choose_price(callback_query, state)

@router.callback_query(F.data.startswith('distance_'))
async def choose_price(callback_query: CallbackQuery, state: FSMContext):
    distance = callback_query.data.split('_')[1]
    await state.update_data(distance_to_sea=distance if distance != "Любое расстояние" else None)

    await state.set_state(PropertyFilter.choosing_price)
    await callback_query.message.edit_text("Введите диапазон цен или пропустите (например: 1000-5000):", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_price")]
    ]))

@router.callback_query(F.data == "skip_price")
async def skip_price_filter(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    properties = await get_properties(
        db,
        property_type=user_data.get('property_type'),
        number_of_beds=user_data.get('number_of_beds'),
        distance_to_sea=user_data.get('distance_to_sea')
    )
    await state.update_data(properties=properties, page=0)
    await show_property_page(callback_query.message, state)
    await state.set_state(PropertyFilter.showing_results)

@router.message(PropertyFilter.choosing_price)
async def receive_price_range(message: Message, state: FSMContext):
    price_range = message.text
    await state.update_data(price_range=price_range)
    user_data = await state.get_data()
    properties = await get_properties(
        db,
        property_type=user_data.get('property_type'),
        number_of_beds=user_data.get('number_of_beds'),
        distance_to_sea=user_data.get('distance_to_sea'),
        price_range=user_data.get('price_range')
    )
    await state.update_data(properties=properties, page=0)
    await show_property_page(message, state)
    await state.set_state(PropertyFilter.showing_results)

async def get_properties(db, property_type=None, number_of_beds=None, distance_to_sea=None, price_range=None):
    await db.ensure_connection()

    # Обработка диапазонов расстояний
    distance_condition = ""
    if distance_to_sea == "<100м":
        distance_condition = "CAST(distance_to_sea AS SIGNED) < 100"
    elif distance_to_sea == "100-500м":
        distance_condition = "CAST(distance_to_sea AS SIGNED) BETWEEN 100 AND 500"
    elif distance_to_sea == ">500м":
        distance_condition = "CAST(distance_to_sea AS SIGNED) > 500"

    # Обработка диапазона цен
    price_condition = ""
    if price_range:
        min_price, max_price = price_range.split('-')
        price_condition = f"monthly_price BETWEEN {min_price} AND {max_price}"
    else:
        price_condition = "monthly_price BETWEEN 100 AND 2000000"

    query = f"""
    SELECT property_id, name, location, distance_to_sea, property_type, monthly_price, daily_price,
           booking_deposit_fixed, security_deposit, bedrooms, bathrooms, pool, kitchen, cleaning, description, utility_bill,
           photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8, photo9, air_conditioners
    FROM properties
    WHERE (%s IS NULL OR property_type = %s)
    AND (%s IS NULL OR bedrooms = %s)
    """

    # Добавляем условия
    if distance_condition:
        query += f" AND ({distance_condition})"
    if price_condition:
        query += f" AND ({price_condition})"

    params = (property_type, property_type, number_of_beds, number_of_beds)

    logging.info(f"Executing query: {query}")
    logging.info(f"With params: {params}")

    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params)
            result = await cursor.fetchall()

            logging.info(f"Query result: {result}")

            properties = []
            for row in result:
                property = {
                    'id': row['property_id'],
                    'name': row['name'],
                    'location': row['location'],
                    'distance_to_sea': row['distance_to_sea'],
                    'property_type': row['property_type'],
                    'monthly_price': row['monthly_price'],
                    'daily_price': row['daily_price'],
                    'booking_deposit_fixed': row['booking_deposit_fixed'],
                    'security_deposit': row['security_deposit'],
                    'bedrooms': row['bedrooms'],
                    'bathrooms': row['bathrooms'],
                    'pool': row['pool'],
                    'kitchen': row['kitchen'],
                    'cleaning': row['cleaning'],
                    'description': row['description'],
                    'utility_bill': row['utility_bill'],
                    'photo1': row['photo1'],
                    'photo2': row['photo2'],
                    'photo3': row['photo3'],
                    'photo4': row['photo4'],
                    'photo5': row['photo5'],
                    'photo6': row['photo6'],
                    'photo7': row['photo7'],
                    'photo8': row['photo8'],
                    'photo9': row['photo9'],
                    'air_conditioners': row['air_conditioners']
                }
                properties.append(property)

    return properties


async def show_property_page(message: Message, state: FSMContext):
    user_data = await state.get_data()
    properties = user_data.get('properties', [])
    page = user_data.get('page', 0)

    if properties:
        property = properties[page]
        avg_rating = property.get('avg_rating', 'Нет рейтинга')
        if avg_rating != 'Нет рейтинга':
            avg_rating = f"⭐ {avg_rating:.1f}"

        text = (
            f"🏠 <b>{property['name']}</b>\n\n"
        f"📍 <b>Расположение:</b> {property['location']}\n"
        f"🌊 <b>Удаленность от моря:</b> {property['distance_to_sea']}\n"
        f"🏷️ <b>Категория:</b> {property['property_type']}\n\n"
        f"💰 <b>Стоимость в месяц:</b> {property['monthly_price']}฿\n"
        f"💰 <b>Стоимость постуточно:</b> {property['daily_price']}฿\n"
        f"💵 <b>Залог:</b> {property['booking_deposit_fixed']}฿\n"
        f"🔒 <b>Сохраненный депозит:</b> {property['security_deposit']}฿\n\n"
        f"🛏️ <b>Количество спален:</b> {property['bedrooms']}\n"
        f"🛁 <b>Количество ванных:</b> {property['bathrooms']}\n"
        f"🏊 <b>Бассейн:</b> {'Да' if property['pool'] else 'Нет'}\n"
        f"🍴 <b>Кухня:</б> {'Да' if property['kitchen'] else 'Нет'}\n"
        f"🧹 <b>Уборка:</b> {'Да' if property['cleaning'] else 'Нет'}\n"
        f"💡 <b>Утилиты:</b> {property['utility_bill']}\n\n"
        f"📜 <b>Описание:</б> {property['description']}\n\n"
        f"🌟 <b>Средний рейтинг:</б> {avg_rating}\n"
        ).replace("</б>", "</b>")

        photos = [property[f'photo{i}'] for i in range(1, 10) if property[f'photo{i}']]

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️", callback_data="prev_page"),
                InlineKeyboardButton(text="❤️", callback_data=f"fav_{property['id']}"),
                InlineKeyboardButton(text="➡️", callback_data="next_page")
            ],
            [
                InlineKeyboardButton(text="🗺 Показать на карте", callback_data=f"map_{property['id']}")
            ],
            [
                InlineKeyboardButton(text="📖 Читать отзывы и рейтинг", callback_data=f"read_reviews_{property['id']}")
            ],
            [
                InlineKeyboardButton(text="🔚 Возврат в меню", callback_data="back_to_main")
            ]
        ])

        if photos:
            media = [InputMediaPhoto(media=photos[0], caption=text, parse_mode=ParseMode.HTML)]
            media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])

            try:
                # Delete previous messages
                if 'message_ids' in user_data:
                    delete_tasks = [
                        delete_message_if_exists(message.bot, message.chat.id, msg_id)
                        for msg_id in user_data['message_ids']
                    ]
                    await asyncio.gather(*delete_tasks)

                # Send media group and text message with action buttons
                media_group_message = await message.answer_media_group(media=media)
                action_message = await message.answer("Выберите действие:", reply_markup=markup)

                # Store sent message ids for future reference (to delete or edit)
                message_ids = [msg.message_id for msg in media_group_message]
                message_ids.append(action_message.message_id)
                await state.update_data(message_ids=message_ids)

            except Exception as e:
                logging.error(f"Error sending media group: {e}")
                await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=markup)
        else:
            try:
                # Delete previous messages
                if 'message_ids' in user_data:
                    delete_tasks = [
                        delete_message_if_exists(message.bot, message.chat.id, msg_id)
                        for msg_id in user_data['message_ids']
                    ]
                    await asyncio.gather(*delete_tasks)

                action_message = await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=markup)
                await state.update_data(message_ids=[action_message.message_id])
            except Exception as e:
                logging.error(f"Error editing message: {e}")
    else:
        await message.answer("Нет результатов по заданным критериям.")


async def delete_message_if_exists(bot, chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            logging.warning(f"Message {message_id} not found for deletion")
        else:
            raise e


@router.callback_query(F.data == 'prev_page')
async def paginate_prev(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    page = user_data['page']

    if page > 0:
        page -= 1
        await state.update_data(page=page)

        # Delete previous messages
        if 'message_ids' in user_data:
            delete_tasks = [
                delete_message_if_exists(callback_query.message.bot, callback_query.message.chat.id, msg_id)
                for msg_id in user_data['message_ids']
            ]
            await asyncio.gather(*delete_tasks)

        await show_property_page(callback_query.message, state)
    else:
        await callback_query.answer("Это первая страница.")


@router.callback_query(F.data == 'next_page')
async def paginate_next(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    page = user_data['page']
    properties = user_data.get('properties', [])

    if page < len(properties) - 1:
        page += 1
        await state.update_data(page=page)

        # Delete previous messages
        if 'message_ids' in user_data:
            delete_tasks = [
                delete_message_if_exists(callback_query.message.bot, callback_query.message.chat.id, msg_id)
                for msg_id in user_data['message_ids']
            ]
            await asyncio.gather(*delete_tasks)

        await show_property_page(callback_query.message, state)
    else:
        await callback_query.answer("Это последняя страница.")

@router.callback_query(F.data.startswith('fav_'))
async def add_to_favorites(user_id, property_id):
    # Получение текущего состояния избранных свойств пользователя
    query_check = "SELECT property1, property2, property3, property4, property5, property6, property7, property8 FROM favorites WHERE user_id = %s"
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query_check, (user_id,))
            result = await cursor.fetchone()

            if result:
                properties = [result[f'property{i}'] for i in range(1, 9)]
                if property_id not in properties:
                    for i in range(8):
                        if properties[i] is None:
                            properties[i] = property_id
                            break
                    update_query = """
                    UPDATE favorites 
                    SET property1 = %s, property2 = %s, property3 = %s, property4 = %s, property5 = %s, property6 = %s, property7 = %s, property8 = %s 
                    WHERE user_id = %s
                    """
                    await cursor.execute(update_query, (*properties, user_id))
            else:
                insert_query = "INSERT INTO favorites (user_id, property1) VALUES (%s, %s)"
                await cursor.execute(insert_query, (user_id, property_id))

            await conn.commit()


@router.message(F.text == "🔔 Уведомления")
async def manage_notifications(message: Message):
    await db.update_last_activity(message.from_user.id)
    response_text = "Выберите, пункт меню:"
    await message.answer(response_text, reply_markup=kb.notification_keyboard)

@router.callback_query(F.data == "subscribe_notifications")
async def subscribe_notifications(callback_query: CallbackQuery):
    await db.update_last_activity(callback_query.from_user.id)
    user_id = callback_query.from_user.id

    await db.subscribe_to_notifications(user_id)
    await callback_query.message.answer("Вы успешно подписаны на уведомления!", reply_markup=kb.main)
    await callback_query.answer()

@router.callback_query(F.data == "unsubscribe_notifications")
async def unsubscribe_notifications(callback_query: CallbackQuery):
    await db.update_last_activity(callback_query.from_user.id)
    user_id = callback_query.from_user.id

    await db.unsubscribe_from_notifications(user_id)
    await callback_query.message.answer("Вы успешно отписаны от уведомлений.", reply_markup=kb.main)
    await callback_query.answer()

@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback_query: CallbackQuery):
    await db.update_last_activity(callback_query.from_user.id)
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=kb.main)
    await callback_query.answer()


@router.message(F.text == "🌟 Лучшие объекты")
async def show_top_properties(message: Message):
    await ensure_db_connection()

    query = """
    SELECT p.property_id, p.name, AVG(r.rating) as avg_rating
    FROM properties p
    JOIN reviews r ON p.property_id = r.property_id
    GROUP BY p.property_id, p.name
    ORDER BY avg_rating DESC
    LIMIT 10
    """

    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            top_properties = await cursor.fetchall()

    if not top_properties:
        await message.answer("Нет объектов с отзывами.")
        return

    buttons = [
        [InlineKeyboardButton(text=f"{property['name']} - ⭐ {property['avg_rating']:.1f}", callback_data=f"show_{property['property_id']}")]
        for property in top_properties
    ]
    buttons.append([InlineKeyboardButton(text="🔚 Возврат в меню", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("🌟 Лучшие объекты недвижимости:", reply_markup=keyboard)
