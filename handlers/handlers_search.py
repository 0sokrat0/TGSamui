import asyncio
import logging

import aiomysql
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import db_config
from database.database import Database

router = Router()
db = Database(db_config)



class PropertyFilter(StatesGroup):
    choosing_rent_type = State()
    choosing_type = State()
    choosing_district = State()
    choosing_beds = State()
    choosing_baths = State()
    choosing_price = State()
    showing_results = State()

async def ensure_db_connection():
    if db.pool is None:
        await db.connect()
        if db.pool is None:
            raise Exception("Failed to connect to the database")
        logging.info("Database connected successfully.")



async def reset_selections(state: FSMContext):
    await state.update_data(
        selected_rent_type=None,
        selected_types=[],
        selected_districts=[],
        selected_beds=[],
        selected_baths=[],
        selected_price=None
    )

def create_keyboard(items, selected_items, prefix, continue_callback, skip_callback=None):
    keyboard = []
    for item_name, item_id in items:
        text = f"✓ {item_name}" if item_id in selected_items else f"▫ {item_name}"
        callback_data = f"{prefix}|{item_id}|{'remove' if item_id in selected_items else 'add'}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    control_buttons = [
        InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back"),
        InlineKeyboardButton(text="➡️ Продолжить", callback_data=continue_callback)
    ]

    if skip_callback:
        control_buttons.append(InlineKeyboardButton(text="⏩ Пропустить", callback_data=skip_callback))

    keyboard.append(control_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data == "start_search")
async def start_search(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await delete_previous_messages(state, callback_query.message)
    await reset_selections(state)

    data = await get_data()
    selected_rent_type = (await state.get_data()).get('selected_rent_type', None)
    markup = create_keyboard(data['rent_types'], [selected_rent_type], "select_rent_type", "continue_rent_type_selection", "skip_rent_type_selection")
    await callback_query.message.edit_text("Выберите тип аренды:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_rent_type)

@router.callback_query(F.data.startswith("select_rent_type|"))
async def select_rent_type(callback_query: CallbackQuery, state: FSMContext):
    _, rent_type, _ = callback_query.data.split("|")
    await delete_previous_messages(state, callback_query.message)

    user_data = await state.get_data()
    selected_rent_type = user_data.get('selected_rent_type', None)

    if selected_rent_type == rent_type:
        await callback_query.answer("Тип аренды уже выбран.")
        return

    await state.update_data(selected_rent_type=rent_type)

    data = await get_data()
    markup = create_keyboard(data['rent_types'], [rent_type], "select_rent_type", "continue_rent_type_selection", "skip_rent_type_selection")
    await callback_query.message.edit_reply_markup(reply_markup=markup)

@router.callback_query(F.data == "continue_rent_type_selection")
async def choose_type(callback_query: CallbackQuery, state: FSMContext):
    await delete_previous_messages(state, callback_query.message)
    await state.set_state(PropertyFilter.choosing_type)
    await show_type_selection(callback_query, state)

@router.callback_query(F.data == "skip_rent_type_selection")
async def skip_rent_type_selection(callback_query: CallbackQuery, state: FSMContext):
    await choose_type(callback_query, state)

async def show_type_selection(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_types = (await state.get_data()).get('selected_types', [])
    markup = create_keyboard(data['types'], selected_types, "toggle_type", "continue_type_selection", "skip_type_selection")
    await callback_query.message.edit_text("Выберите тип жилья:", reply_markup=markup)

@router.callback_query(F.data.startswith("toggle_type|"))
async def toggle_type_selection(callback_query: CallbackQuery, state: FSMContext):
    _, property_type, action = callback_query.data.split("|")
    await delete_previous_messages(state, callback_query.message)
    user_data = await state.get_data()
    selected_types = user_data.get('selected_types', [])

    if action == "add":
        selected_types.append(property_type)
    elif action == "remove":
        selected_types.remove(property_type)

    await state.update_data(selected_types=selected_types)
    data = await get_data()
    markup = create_keyboard(data["types"], selected_types, "toggle_type", "continue_type_selection", "skip_type_selection")
    await callback_query.message.edit_reply_markup(reply_markup=markup)

@router.callback_query(F.data == "continue_type_selection")
async def choose_district(callback_query: CallbackQuery, state: FSMContext):
    await delete_previous_messages(state, callback_query.message)
    user_data = await state.get_data()
    if not user_data.get('selected_types'):
        await callback_query.answer("Выберите хотя бы один тип недвижимости.")
        return
    await state.set_state(PropertyFilter.choosing_district)
    await show_district_selection(callback_query, state)

@router.callback_query(F.data == "skip_type_selection")
async def skip_type_selection(callback_query: CallbackQuery, state: FSMContext):
    await delete_previous_messages(state, callback_query.message)
    await state.set_state(PropertyFilter.choosing_district)
    await show_district_selection(callback_query, state)

async def show_district_selection(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_districts = (await state.get_data()).get('selected_districts', [])
    markup = create_keyboard(data['districts'], selected_districts, "toggle_district", "continue_district_selection", "skip_district_selection")
    await callback_query.message.edit_text("Выберите район:", reply_markup=markup)

@router.callback_query(F.data.startswith("toggle_district|"))
async def toggle_district_selection(callback_query: CallbackQuery, state: FSMContext):
    _, district, action = callback_query.data.split("|")
    user_data = await state.get_data()
    selected_districts = user_data.get('selected_districts', [])

    if action == "add":
        selected_districts.append(district)
    elif action == "remove":
        selected_districts.remove(district)

    await state.update_data(selected_districts=selected_districts)
    data = await get_data()
    markup = create_keyboard(data["districts"], selected_districts, "toggle_district", "continue_district_selection", "skip_district_selection")
    await callback_query.message.edit_reply_markup(reply_markup=markup)

@router.callback_query(F.data == "continue_district_selection")
async def choose_beds(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if not user_data.get('selected_districts'):
        await callback_query.answer("Выберите хотя бы один район.")
        return
    await state.set_state(PropertyFilter.choosing_beds)
    await show_beds_selection(callback_query, state)

@router.callback_query(F.data == "skip_district_selection")
async def skip_district_selection(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(PropertyFilter.choosing_beds)
    await show_beds_selection(callback_query, state)

async def show_beds_selection(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_beds = (await state.get_data()).get('selected_beds', [])
    markup = create_keyboard(data['beds'], selected_beds, "select_beds", "continue_beds_selection", "skip_beds_selection")
    await callback_query.message.edit_text("Выберите количество спален:", reply_markup=markup)

@router.callback_query(F.data.startswith("select_beds|"))
async def select_beds(callback_query: CallbackQuery, state: FSMContext):
    _, beds, action = callback_query.data.split("|")
    user_data = await state.get_data()
    selected_beds = user_data.get('selected_beds', [])

    if action == "add":
        selected_beds.append(beds)
    elif action == "remove":
        selected_beds.remove(beds)

    await state.update_data(selected_beds=selected_beds)
    data = await get_data()
    markup = create_keyboard(data["beds"], selected_beds, "select_beds", "continue_beds_selection", "skip_beds_selection")
    await callback_query.message.edit_reply_markup(reply_markup=markup)

@router.callback_query(F.data == "continue_beds_selection")
async def choose_baths(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if not user_data.get('selected_beds'):
        await callback_query.answer("Выберите хотя бы одно количество спален.")
        return
    await state.set_state(PropertyFilter.choosing_baths)
    await show_baths_selection(callback_query, state)

@router.callback_query(F.data == "skip_beds_selection")
async def skip_beds_selection(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(PropertyFilter.choosing_baths)
    await show_baths_selection(callback_query, state)

async def show_baths_selection(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_baths = (await state.get_data()).get('selected_baths', [])
    markup = create_keyboard(data['baths'], selected_baths, "select_baths", "continue_baths_selection", "skip_baths_selection")
    await callback_query.message.edit_text("Выберите количество ванных комнат:", reply_markup=markup)

@router.callback_query(F.data.startswith("select_baths|"))
async def select_baths(callback_query: CallbackQuery, state: FSMContext):
    _, baths, action = callback_query.data.split("|")
    user_data = await state.get_data()
    selected_baths = user_data.get('selected_baths', [])

    if action == "add":
        selected_baths.append(baths)
    elif action == "remove":
        selected_baths.remove(baths)

    await state.update_data(selected_baths=selected_baths)
    data = await get_data()
    markup = create_keyboard(data["baths"], selected_baths, "select_baths", "continue_baths_selection", "skip_baths_selection")
    await callback_query.message.edit_reply_markup(reply_markup=markup)

@router.callback_query(F.data == "continue_baths_selection")
async def choose_price(callback_query: CallbackQuery, state: FSMContext):
    await delete_previous_messages(state, callback_query.message)
    user_data = await state.get_data()
    if not user_data.get('selected_baths'):
        await callback_query.answer("Выберите хотя бы одно количество ванных комнат.")
        return
    await state.set_state(PropertyFilter.choosing_price)
    await show_price_selection(callback_query, state)

@router.callback_query(F.data == "skip_baths_selection")
async def skip_baths_selection(callback_query: CallbackQuery, state: FSMContext):
    await delete_previous_messages(state, callback_query.message)
    await state.set_state(PropertyFilter.choosing_price)
    await show_price_selection(callback_query, state)

async def show_price_selection(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_price = (await state.get_data()).get('selected_price', None)
    markup = create_keyboard(data['price_ranges'], [selected_price], "select_price", "continue_price_selection", "skip_price_selection")
    await callback_query.message.edit_text("Выберите диапазон цен:", reply_markup=markup)

@router.callback_query(F.data.startswith("select_price|"))
async def select_price(callback_query: CallbackQuery, state: FSMContext):
    _, price_range, _ = callback_query.data.split("|")
    await delete_previous_messages(state, callback_query.message)
    await state.update_data(selected_price=price_range)
    data = await get_data()
    markup = create_keyboard(data["price_ranges"], [price_range], "select_price", "continue_price_selection")
    await callback_query.message.edit_reply_markup(reply_markup=markup)

@router.callback_query(F.data == "continue_price_selection")
async def show_results(callback_query: CallbackQuery, state: FSMContext):
    await delete_previous_messages(state, callback_query.message)
    user_data = await state.get_data()

    properties = await get_properties_with_suggestions(
        db,
        property_types=user_data.get("selected_types"),
        locations=user_data.get("selected_districts"),
        bedrooms=user_data.get("selected_beds"),
        bathrooms=user_data.get("selected_baths"),
        price_range=user_data.get("selected_price"),
        rent_type=user_data.get("selected_rent_type")
    )

    if not properties:
        await callback_query.message.answer("Нет результатов по заданным критериям. Попробуйте изменить параметры поиска.")
        return

    await state.update_data(properties=properties, page=0)
    await show_property_page(callback_query.message, state)
    await reset_selections(state)
    await state.set_state(PropertyFilter.showing_results)

@router.callback_query(F.data == "skip_price_selection")
async def skip_price_selection(callback_query: CallbackQuery, state: FSMContext):
    await delete_previous_messages(state, callback_query.message)
    await show_results(callback_query, state)

@router.callback_query(F.data == "go_back")
async def go_back(callback_query: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == PropertyFilter.choosing_district.state:
        await choose_type(callback_query, state)
    elif current_state == PropertyFilter.choosing_beds.state:
        await choose_district(callback_query, state)
    elif current_state == PropertyFilter.choosing_baths.state:
        await choose_beds(callback_query, state)
    elif current_state == PropertyFilter.choosing_price.state:
        await choose_baths(callback_query, state)

async def get_data():
    types = [
        ("🏠 Вилла", 'вилла'),
        ("🏢 Кондо", 'condo'),
        ("🛏️ Апартаменты", 'apartment'),
        ("🏡 Дом в резорте", 'resort_house'),
        ("🏠 Дом в резиденции", 'house_in_residence'),
        ("🏠 Вилла в резиденции", 'villa_in_residence'),
        ("🛏️ Комната", 'room'),
        ("🏡 Бунгало", 'bungalo'),
        ("🏢 Резиденция", 'residence'),
        ("🏨 Хостел", 'hostel'),
        ("🏠 Дом", 'house'),
    ]

    districts = [
        ("🌴 Bang Kao", 'bang kao'),
        ("🏖️ Bangrak", 'bangrak'),
        ("🌺 Bo Phut", 'bo phut'),
        ("🏝️ Chaweng", 'chaweng'),
        ("🏝️ Chaweng Noi", 'chaweng noi'),
        ("🌊 Chong Mon", 'chong mon'),
        ("🌳 Lamai", 'lamai'),
        ("🌿 Lipa Noi", 'lipa noi'),
        ("🌾 Maenam", 'maenam'),
        ("🏡 Na Tong", 'na tong'),
        ("🌅 Taling Ngam", 'taling ngnam'),
    ]

    rent_types = [
        ("Помесячно", 'monthly'),
        ("Посуточно", 'daily'),
        ("Помесячно и посуточно", 'both'),
    ]

    beds = [("1", '1'), ("2", '2'), ("3", '3'), ("4", '4'), ("5", '5')]
    baths = [("1", '1'), ("2", '2'), ("3", '3'), ("4", '4'), ("5", '5')]
    price_ranges = [("От 10000 ฿", "10000-30000"), ("От 30000 ฿", "30000-50000"), ("От 50000 ฿", "50000-70000"), ("От 70000 ฿", "70000-100000"), ("От 100000 ฿", "100000+")]

    return {
        "types": types,
        "districts": districts,
        "beds": beds,
        "baths": baths,
        "price_ranges": price_ranges,
        "rent_types": rent_types,
    }

async def get_properties_with_suggestions(db, property_types=None, locations=None, bedrooms=None, bathrooms=None, price_range=None, rent_type=None):
    await ensure_db_connection()

    conditions = []
    params = []

    if rent_type:
        if rent_type == 'monthly':
            conditions.append("(rent_type = 'monthly' OR rent_type = 'both')")
        elif rent_type == 'daily':
            conditions.append("(rent_type = 'daily' OR rent_type = 'both')")
        elif rent_type == 'both':
            conditions.append("(rent_type = 'monthly' OR rent_type = 'daily' OR rent_type = 'both')")

    if property_types:
        type_conditions = " OR ".join(["LOWER(property_type) LIKE LOWER(%s)"] * len(property_types))
        conditions.append(f"({type_conditions})")
        params.extend([f"%{ptype}%" for ptype in property_types])

    if locations:
        location_conditions = " OR ".join(["LOWER(location) = LOWER(%s)"] * len(locations))
        conditions.append(f"({location_conditions})")
        params.extend(locations)

    if bedrooms:
        conditions.append("bedrooms >= %s")
        params.append(min(bedrooms))

    if bathrooms:
        conditions.append("bathrooms >= %s")
        params.append(min(bathrooms))

    if price_range:
        min_price, max_price = map(int, price_range.split('-')) if '-' in price_range else (int(price_range), 2000000)
        conditions.append("monthly_price BETWEEN %s AND %s")
        params.extend([min_price, max_price])

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    logging.info(f"SQL Query: SELECT * FROM properties WHERE {where_clause}")
    logging.info(f"Parameters: {params}")

    query = f"""
    SELECT property_id, name, location, distance_to_sea, property_type, monthly_price, daily_price,
           booking_deposit_fixed, security_deposit, bedrooms, bathrooms, pool, kitchen, cleaning, description, utility_bill,
           photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8, photo9, air_conditioners
    FROM properties
    WHERE {where_clause}
    ORDER BY monthly_price DESC
    """

    async with db.pool.acquire() as conn:
        try:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()
        except aiomysql.MySQLError as e:
            logging.error(f"Database error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    return []


async def show_property_page(message: Message, state: FSMContext):
    user_data = await state.get_data()
    properties = user_data.get('properties', [])
    page = user_data.get('page', 0)
    total_pages = len(properties)

    if properties:
        property = properties[page]

        # Проверяем, что property_id существует и корректен
        property_id = property.get('property_id')
        if not property_id:
            logging.error("Property ID is missing or invalid.")
            await message.answer("Ошибка: ID недвижимости отсутствует или некорректен.")
            return

        # Обрабатываем возможное отсутствие данных
        avg_rating = property.get('avg_rating', 'Нет рейтинга')
        if avg_rating != 'Нет рейтинга':
            avg_rating = f"⭐ {avg_rating:.1f}"

        booking_deposit_fixed = property.get('booking_deposit_fixed', 'Нет данных')
        security_deposit = property.get('security_deposit', 'Нет данных')

        text = (
            f"🏠 <b>{property['name']}</b>\n\n"
            f"📍 <b>Расположение:</b> {property['location']}\n"
            f"🌊 <b>Удаленность от моря:</б> {property['distance_to_sea']}\n"
            f"🛏️ <b>Количество спален:</б> {property['bedrooms']}\n"
            f"🛁 <b>Количество ванных:</б> {property['bathrooms']}\n"
            f"💵 <b>Залог:</б> {booking_deposit_fixed}฿\n"
            f"🔒 <b>Сохраненный депозит:</б> {security_deposit}฿\n"
        ).replace("</б>", "</b>")

        photos = [property[f'photo{i}'] for i in range(1, 10) if
                  property.get(f'photo{i}') and property[f'photo{i}'].startswith('http')]

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_page"),
                InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="current_page"),
                InlineKeyboardButton(text="Вперед ➡️", callback_data="next_page")
            ],
            [
                InlineKeyboardButton(text="❤️ В избранное", callback_data=f"fav_{property_id}"),
                InlineKeyboardButton(text="📖 Подробнее", callback_data=f"details_{property_id}")
            ],
            [
                InlineKeyboardButton(text="🔚 Возврат в меню", callback_data="back_to_main")
            ]
        ])

        if photos:
            media = [InputMediaPhoto(media=photos[0], caption=text, parse_mode=ParseMode.HTML)]
            media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])

            if 'message_ids' in user_data and user_data['message_ids']:
                try:
                    for i in range(len(media)):
                        if i < len(user_data['message_ids']):
                            await message.bot.edit_message_media(
                                chat_id=message.chat.id,
                                message_id=user_data['message_ids'][i],
                                media=media[i]
                            )
                    await message.bot.edit_message_text(
                        text="Выберите действие:",
                        chat_id=message.chat.id,
                        message_id=user_data['message_ids'][-1],
                        reply_markup=markup
                    )
                except Exception as e:
                    logging.error(f"Error editing media group: {e}")
                    await send_new_media_group(message, media, markup, state)
            else:
                await send_new_media_group(message, media, markup, state)
        else:
            try:
                if 'message_ids' in user_data and user_data['message_ids']:
                    await message.bot.edit_message_text(
                        text=text,
                        chat_id=message.chat.id,
                        message_id=user_data['message_ids'][0],
                        parse_mode=ParseMode.HTML,
                        reply_markup=markup
                    )
                else:
                    action_message = await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=markup)
                    await state.update_data(message_ids=[action_message.message_id])
            except Exception as e:
                logging.error(f"Error editing message: {e}")
                action_message = await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=markup)
                await state.update_data(message_ids=[action_message.message_id])
    else:
        await message.answer("Нет результатов по заданным критериям.")


async def send_new_media_group(message, media, markup, state):
    """Helper function to send a new media group with actions."""
    media_group_message = await message.answer_media_group(media=media)
    action_message = await message.answer("Выберите действие:", reply_markup=markup)

    message_ids = [msg.message_id for msg in media_group_message]
    message_ids.append(action_message.message_id)
    await state.update_data(message_ids=message_ids)

async def delete_message_if_exists(bot, chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            logging.warning(f"Message {message_id} not found for deletion")
        else:
            raise e

async def delete_previous_messages(state: FSMContext, message: Message):
    """Удаление всех связанных сессий сообщений"""
    user_data = await state.get_data()
    if 'message_ids' in user_data:
        delete_tasks = [
            delete_message_if_exists(message.bot, message.chat.id, msg_id)
            for msg_id in user_data['message_ids']
        ]
        await asyncio.gather(*delete_tasks)
        await state.update_data(message_ids=[])


@router.callback_query(F.data == 'prev_page')
async def paginate_prev(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    page = user_data['page']

    if page > 0:
        page -= 1
        await state.update_data(page=page)

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

        if 'message_ids' in user_data:
            delete_tasks = [
                delete_message_if_exists(callback_query.message.bot, callback_query.message.chat.id, msg_id)
                for msg_id in user_data['message_ids']
            ]
            await asyncio.gather(*delete_tasks)

        await show_property_page(callback_query.message, state)
    else:
        await callback_query.answer("Это последняя страница.")


@router.callback_query(F.data == 'current_page')
async def show_current_page(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    page = user_data['page'] + 1
    total_pages = len(user_data.get('properties', []))
    await callback_query.answer(f"Страница {page}/{total_pages}")


@router.callback_query(F.data.startswith('fav_'))
async def add_to_favorites_handler(callback_query: CallbackQuery, state: FSMContext):
    await ensure_db_connection()

    logging.info(f"Callback data received: {callback_query.data}")

    # Получаем строковое значение property_id из callback_data
    property_id_str = callback_query.data.split('_')[1]

    # Проверяем, является ли это значение числом
    if property_id_str.isdigit():
        property_id = int(property_id_str)
        logging.info(f"Valid property_id: {property_id}")
        user_id = callback_query.from_user.id
        is_added = await add_to_favorites(user_id, property_id)
        if is_added:
            await callback_query.answer("Добавлено в избранное!")
        else:
            await callback_query.answer("Не удалось добавить в избранное. Возможно, объект уже есть в списке.")
    else:
        logging.error(f"Invalid property_id: {property_id_str}")
        await callback_query.answer("Ошибка: Неверный ID недвижимости.")



async def add_to_favorites(user_id, property_id):
    query = """
    INSERT INTO favorites (user_id, property_id)
    SELECT %s, %s FROM DUAL
    WHERE NOT EXISTS (
        SELECT 1 FROM favorites WHERE user_id = %s AND property_id = %s
    )
    """

    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, (user_id, property_id, user_id, property_id))
            affected_rows = cursor.rowcount
            await conn.commit()

    return affected_rows > 0


# Пример кода, где исправлено обращение к 'property_id'
@router.callback_query(F.data.startswith('details_'))
async def show_property_details(callback_query: CallbackQuery, state: FSMContext):
    await ensure_db_connection()
    user_data = await state.get_data()
    properties = user_data.get('properties', [])
    page = user_data.get('page', 0)
    total_pages = len(properties)

    if properties:
        property = properties[page]
        avg_rating = property.get('avg_rating', None)
        avg_rating_text = f"⭐ {avg_rating:.1f}" if avg_rating is not None else "Нет рейтинга"

        text = (
            f"🏠 <b>{property['name']}</b>\n\n"
            f"📍 <b>Расположение:</b> {property['location']}\n"
            f"🌊 <b>Удаленность от моря:</б> {property['distance_to_sea']}\n"
            f"🏷️ <b>Категория:</б> {property['property_type']}\n\n"
            f"💰 <b>Стоимость в месяц:</б> {property['monthly_price']}฿\n"
            f"💰 <b>Стоимость постуточно:</б> {property['daily_price']}฿\n"
            f"💵 <b>Залог:</б> {property['booking_deposit_fixed']}฿\n"
            f"🔒 <b>Сохраненный депозит:</б> {property['security_deposit']}฿\n\n"
            f"🛏️ <b>Количество спален:</б> {property['bedrooms']}\n"
            f"🛁 <b>Количество ванных:</б> {property['bathrooms']}\n"
            f"🏊 <b>Бассейн:</б> {'Да' if property['pool'] else 'Нет'}\n"
            f"🍴 <b>Кухня:</б> {'Да' if property['kitchen'] else 'Нет'}\n"
            f"🧹 <b>Уборка:</б> {'Да' if property['cleaning'] else 'Нет'}\n"
            f"💡 <b>Утилиты:</б> {property['utility_bill']}\n\n"
            f"📜 <b>Описание:</б> {property['description']}\n\n"
        ).replace("</б>", "</b>")

        photos = [property[f'photo{i}'] for i in range(1, 10) if
                  property.get(f'photo{i}') and property[f'photo{i}'].startswith('http')]

        if photos:
            media = [InputMediaPhoto(media=photos[0], caption=text, parse_mode=ParseMode.HTML)]
            media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])

            media_group_message = await callback_query.message.answer_media_group(media=media)
            action_message = await callback_query.message.answer("Выберите действие:",
                                                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                                     [
                                                                         InlineKeyboardButton(text="⬅️ Назад",
                                                                                              callback_data="prev_page"),
                                                                         InlineKeyboardButton(text="❤️ В избранное",
                                                                                              callback_data=f"fav_{property['property_id']}"),
                                                                         InlineKeyboardButton(text="Вперед ➡️",
                                                                                              callback_data="next_page")
                                                                     ],
                                                                     [
                                                                         InlineKeyboardButton(text="🔚 Возврат в меню",
                                                                                              callback_data="back_to_main")
                                                                     ],
                                                                     [InlineKeyboardButton(
                                                                         text=f"Страница {page + 1}/{total_pages}",
                                                                         callback_data="noop")]
                                                                 ]))

            # Сохраняем идентификаторы сообщений для последующего удаления
            message_ids = [msg.message_id for msg in media_group_message]
            message_ids.append(action_message.message_id)
            await state.update_data(message_ids=message_ids)
        else:
            # Если фотографий нет, отправляем новое сообщение, а не редактируем
            if 'message_ids' in user_data:
                delete_tasks = [
                    delete_message_if_exists(callback_query.message.bot, callback_query.message.chat.id, msg_id)
                    for msg_id in user_data['message_ids']
                ]
                await asyncio.gather(*delete_tasks)

            action_message = await callback_query.message.answer(text, parse_mode=ParseMode.HTML,
                                                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                                     [
                                                                         InlineKeyboardButton(text="⬅️ Назад",
                                                                                              callback_data="prev_page"),
                                                                         InlineKeyboardButton(text="❤️ В избранное",
                                                                                              callback_data=f"fav_{property['property_id']}"),
                                                                         InlineKeyboardButton(text="Вперед ➡️",
                                                                                              callback_data="next_page")
                                                                     ],
                                                                     [
                                                                         InlineKeyboardButton(text="🔚 Возврат в меню",
                                                                                              callback_data="back_to_main")
                                                                     ],
                                                                     [InlineKeyboardButton(
                                                                         text=f"Страница {page + 1}/{total_pages}",
                                                                         callback_data="noop")]
                                                                 ]))
            # Сохраняем идентификатор сообщения
            await state.update_data(message_ids=[action_message.message_id])
    else:
        await callback_query.message.answer("Недвижимость не найдена.")





@router.callback_query(F.data.startswith('page_'))
async def go_to_page(callback_query: CallbackQuery, state: FSMContext):
    page = int(callback_query.data.split('_')[1])
    await state.update_data(page=page)

    user_data = await state.get_data()
    if 'message_ids' in user_data:
        delete_tasks = [
            delete_message_if_exists(callback_query.message.bot, callback_query.message.chat.id, msg_id)
            for msg_id in user_data['message_ids']
        ]
        await asyncio.gather(*delete_tasks)

    await show_property_page(callback_query.message, state)

