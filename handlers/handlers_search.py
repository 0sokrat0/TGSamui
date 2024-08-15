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


@router.callback_query(F.data == "start_search")
async def start_search(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_types = (await state.get_data()).get('selected_types', [])

    builder = InlineKeyboardBuilder()
    for t in data['types']:
        if t[1] in selected_types:
            builder.button(text=f"✅ {t[0]}", callback_data=f"toggle_type_{t[1]}")
        else:
            builder.button(text=f"▫️ {t[0]}", callback_data=f"toggle_type_{t[1]}")

    builder.adjust(1)  # Размещаем кнопки в столбик
    builder.button(text="Продолжить", callback_data="continue_type_selection")
    builder.button(text="Пропустить", callback_data="skip_type_selection")

    markup = builder.as_markup()
    await callback_query.message.edit_text("Выберите тип жилья:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_type)


@router.callback_query(F.data.startswith("toggle_type_"))
async def toggle_type_selection(callback_query: CallbackQuery, state: FSMContext):
    property_type = callback_query.data.split("_")[2]
    user_data = await state.get_data()
    selected_types = user_data.get('selected_types', [])

    if property_type in selected_types:
        selected_types.remove(property_type)
    else:
        selected_types.append(property_type)

    await state.update_data(selected_types=selected_types)
    await start_search(callback_query, state)


@router.callback_query(F.data == "continue_type_selection")
async def choose_district(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_districts = (await state.get_data()).get('selected_districts', [])

    builder = InlineKeyboardBuilder()
    for d in data['districts']:
        if d[1] in selected_districts:
            builder.button(text=f"✅ {d[0]}", callback_data=f"toggle_district_{d[1]}")
        else:
            builder.button(text=f"▫️ {d[0]}", callback_data=f"toggle_district_{d[1]}")

    builder.adjust(1)
    builder.button(text="Продолжить", callback_data="continue_district_selection")
    builder.button(text="Пропустить", callback_data="skip_district_selection")

    markup = builder.as_markup()
    await callback_query.message.edit_text("Выберите район:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_district)


@router.callback_query(F.data.startswith("toggle_district_"))
async def toggle_district_selection(callback_query: CallbackQuery, state: FSMContext):
    district = callback_query.data.split("_")[2]
    user_data = await state.get_data()
    selected_districts = user_data.get('selected_districts', [])

    if district in selected_districts:
        selected_districts.remove(district)
    else:
        selected_districts.append(district)

    await state.update_data(selected_districts=selected_districts)
    await choose_district(callback_query, state)


@router.callback_query(F.data == "continue_district_selection")
async def choose_beds(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_beds = (await state.get_data()).get('selected_beds', [])

    builder = InlineKeyboardBuilder()
    for b in data['beds']:
        if b[1] in selected_beds:
            builder.button(text=f"✅ {b[0]} спальни", callback_data=f"toggle_beds_{b[1]}")
        else:
            builder.button(text=f"▫️ {b[0]} спальни", callback_data=f"toggle_beds_{b[1]}")

    builder.adjust(1)
    builder.button(text="Продолжить", callback_data="continue_beds_selection")
    builder.button(text="Пропустить", callback_data="skip_beds_selection")

    markup = builder.as_markup()
    await callback_query.message.edit_text("Выберите количество спален:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_beds)


@router.callback_query(F.data.startswith("toggle_beds_"))
async def toggle_beds_selection(callback_query: CallbackQuery, state: FSMContext):
    beds = callback_query.data.split("_")[2]
    user_data = await state.get_data()
    selected_beds = user_data.get('selected_beds', [])

    if beds in selected_beds:
        selected_beds.remove(beds)
    else:
        selected_beds.append(beds)

    await state.update_data(selected_beds=selected_beds)
    await choose_beds(callback_query, state)


@router.callback_query(F.data == "continue_beds_selection")
async def choose_baths(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_baths = (await state.get_data()).get('selected_baths', [])

    builder = InlineKeyboardBuilder()
    for b in data['baths']:
        if b[1] in selected_baths:
            builder.button(text=f"✅ {b[0]} ванные комнаты", callback_data=f"toggle_baths_{b[1]}")
        else:
            builder.button(text=f"▫️ {b[0]} ванные комнаты", callback_data=f"toggle_baths_{b[1]}")

    builder.adjust(1)
    builder.button(text="Продолжить", callback_data="continue_baths_selection")
    builder.button(text="Пропустить", callback_data="skip_baths_selection")

    markup = builder.as_markup()
    await callback_query.message.edit_text("Выберите количество ванных комнат:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_baths)


@router.callback_query(F.data.startswith("toggle_baths_"))
async def toggle_baths_selection(callback_query: CallbackQuery, state: FSMContext):
    baths = callback_query.data.split("_")[2]
    user_data = await state.get_data()
    selected_baths = user_data.get('selected_baths', [])

    if baths in selected_baths:
        selected_baths.remove(baths)
    else:
        selected_baths.append(baths)

    await state.update_data(selected_baths=selected_baths)
    await choose_baths(callback_query, state)


@router.callback_query(F.data == "continue_baths_selection")
async def choose_price(callback_query: CallbackQuery, state: FSMContext):
    data = await get_data()
    selected_price = (await state.get_data()).get('selected_price', None)

    builder = InlineKeyboardBuilder()
    for p in data['price_ranges']:
        if p[1] == selected_price:
            builder.button(text=f"✅ {p[0]}", callback_data=f"select_price_{p[1]}")
        else:
            builder.button(text=f"▫️ {p[0]}", callback_data=f"select_price_{p[1]}")

    builder.adjust(1)
    builder.button(text="Продолжить", callback_data="continue_price_selection")
    builder.button(text="Пропустить", callback_data="skip_price_selection")

    markup = builder.as_markup()
    await callback_query.message.edit_text("Выберите диапазон цен:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_price)


@router.callback_query(F.data.startswith("select_price_"))
async def select_price(callback_query: CallbackQuery, state: FSMContext):
    price_range = callback_query.data.split("_")[2]
    await state.update_data(selected_price=price_range)
    await choose_price(callback_query, state)


@router.callback_query(F.data == "continue_price_selection")
async def show_results(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    properties = await get_properties(
        db,
        property_types=user_data.get("selected_types"),
        locations=user_data.get("selected_districts"),
        bedrooms=user_data.get("selected_beds"),
        bathrooms=user_data.get("selected_baths"),
        price_range=user_data.get("selected_price"),
    )

    await state.update_data(properties=properties, page=0)
    await show_property_page(callback_query.message, state)
    await state.set_state(PropertyFilter.showing_results)


@router.callback_query(F.data == "skip_type_selection")
async def skip_type_selection(callback_query: CallbackQuery, state: FSMContext):
    await choose_district(callback_query, state)


@router.callback_query(F.data == "skip_district_selection")
async def skip_district_selection(callback_query: CallbackQuery, state: FSMContext):
    await choose_beds(callback_query, state)


@router.callback_query(F.data == "skip_beds_selection")
async def skip_beds_selection(callback_query: CallbackQuery, state: FSMContext):
    await choose_baths(callback_query, state)


@router.callback_query(F.data == "skip_baths_selection")
async def skip_baths_selection(callback_query: CallbackQuery, state: FSMContext):
    await choose_price(callback_query, state)


@router.callback_query(F.data == "skip_price_selection")
async def skip_price_selection(callback_query: CallbackQuery, state: FSMContext):
    await show_results(callback_query, state)

async def get_data():
    types = [
        ("🏠 Вилла", 'Вилла'),
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
        ("🌴 Bang Kao", 'bang_kao'),
        ("🏖️ Bangrak", 'bangrak'),
        ("🌺 Bo Phut", 'bo_phut'),
        ("🏝️ Chaweng", 'chaweng'),
        ("🏝️ Chaweng Noi", 'chaweng_noi'),
        ("🌊 Chong Mon", 'chong_mon'),
        ("🌳 Lamai", 'lamai'),
        ("🌿 Lipa Noi", 'lipa_noi'),
        ("🌾 Maenam", 'maenam'),
        ("🏡 Na Tong", 'na_tong'),
        ("🌅 Taling Ngam", 'taling_ngnam'),
    ]

    beds = [
        ("1", '1'),
        ("2", '2'),
        ("3", '3'),
        ("4", '4'),
        ("5", '5')
    ]
    baths = [
        ("1", '1'),
        ("2", '2'),
        ("3", '3'),
        ("4", '4'),
        ("5", '5')
    ]
    price_ranges = [
        ("От 10000 ฿", "10000-30000"),
        ("От 30000 ฿", "30000-50000"),
        ("От 50000 ฿", "50000-70000"),
        ("От 70000 ฿", "70000-100000"),
        ("От 100000 ฿", "100000+")
    ]
    return {
        "types": types,
        "districts": districts,
        "beds": beds,
        "baths": baths,
        "price_ranges": price_ranges,
    }


async def get_properties(db, property_types=None, locations=None, bedrooms=None, bathrooms=None, price_range=None):
    await ensure_db_connection()

    conditions = []
    params = []

    if property_types:
        conditions.append("property_type = %s")
        params.append(property_types)

    if locations:
        conditions.append("location = %s")
        params.append(locations)

    if bedrooms:
        conditions.append("bedrooms >= %s")
        params.append(bedrooms)

    if bathrooms:
        conditions.append("bathrooms >= %s")
        params.append(bathrooms)

    if price_range:
        min_price, max_price = price_range.split('-')
        if max_price == '+':
            max_price = '2000000'
        conditions.append("monthly_price BETWEEN %s AND %s")
        params.extend([min_price, max_price])

    where_clause = " AND ".join(conditions) if conditions else "1"
    query = f"""
    SELECT property_id, name, location, distance_to_sea, property_type, monthly_price, daily_price,
           booking_deposit_fixed, security_deposit, bedrooms, bathrooms, pool, kitchen, cleaning, description, utility_bill,
           photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8, photo9, air_conditioners
    FROM properties
    WHERE {where_clause}
    """

    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params)
            result = await cursor.fetchall()

            properties = []
            for row in result:
                properties.append({
                    'id': row['property_id'],
                    'name': row['name'],
                    'location': row['location'],
                    'distance_to_sea': row['distance_to_sea'],
                    'property_type': row['property_type'],
                    'monthly_price': row['monthly_price'],
                    'daily_price': row['daily_price'],
                    'bedrooms': row['bedrooms'],
                    'bathrooms': row['bathrooms'],
                    'description': row['description'],
                    'photos': [row[f'photo{i}'] for i in range(1, 10) if row[f'photo{i}']]
                })

    return properties


async def show_property_page(message: Message, state: FSMContext):
    user_data = await state.get_data()
    properties = user_data.get('properties', [])
    page = user_data.get('page', 0)
    total_pages = len(properties)

    if properties:
        property = properties[page]
        avg_rating = property.get('avg_rating', 'Нет рейтинга')
        if avg_rating != 'Нет рейтинга':
            avg_rating = f"⭐ {avg_rating:.1f}"

        # Show only the first 3 details initially
        text = (
            f"🏠 <b>{property['name']}</b>\n\n"
            f"📍 <b>Расположение:</b> {property['location']}\n"
            f"🌊 <b>Удаленность от моря:</b> {property['distance_to_sea']}\n"
            f"🛏️ <b>Количество спален:</b> {property['bedrooms']}\n"
        ).replace("</б>", "</b>")

        photos = [property[f'photo{i}'] for i in range(1, 10) if
                  property.get(f'photo{i}') and property[f'photo{i}'].startswith('http')]

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_page"),
                InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data=f"current_page"),
                InlineKeyboardButton(text="Вперед ➡️", callback_data="next_page")
            ],
            [
                InlineKeyboardButton(text="❤️ В избранное", callback_data=f"fav_{property.get('id')}"),
                InlineKeyboardButton(text="📖 Подробнее", callback_data=f"details_{property['id']}")
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
                    media_group_message = await message.answer_media_group(media=media)
                    action_message = await message.answer("Выберите действие:", reply_markup=markup)

                    message_ids = [msg.message_id for msg in media_group_message]
                    message_ids.append(action_message.message_id)
                    await state.update_data(message_ids=message_ids)
            else:
                media_group_message = await message.answer_media_group(media=media)
                action_message = await message.answer("Выберите действие:", reply_markup=markup)

                message_ids = [msg.message_id for msg in media_group_message]
                message_ids.append(action_message.message_id)
                await state.update_data(message_ids=message_ids)
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

        # Show full details here
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
            f"🌟 <b>Средний рейтинг:</б> {avg_rating_text}\n"
        ).replace("</б>", "</b>")

        if 'message_ids' in user_data:
            delete_tasks = [
                delete_message_if_exists(callback_query.message.bot, callback_query.message.chat.id, msg_id)
                for msg_id in user_data['message_ids']
            ]
            await asyncio.gather(*delete_tasks)

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
                                                                                              callback_data=f"fav_{property['id']}"),
                                                                         InlineKeyboardButton(text="Вперед ➡️",
                                                                                              callback_data="next_page")
                                                                     ],
                                                                     [
                                                                         InlineKeyboardButton(
                                                                             text="🗺 Показать на карте",
                                                                             callback_data=f"map_{property['id']}")
                                                                     ],
                                                                     [
                                                                         InlineKeyboardButton(
                                                                             text="📖 Читать отзывы и рейтинг",
                                                                             callback_data=f"read_reviews_{property['id']}")
                                                                     ],
                                                                     [
                                                                         InlineKeyboardButton(text="🔚 Возврат в меню",
                                                                                              callback_data="back_to_main")
                                                                     ],
                                                                     [InlineKeyboardButton(
                                                                         text=f"Страница {page + 1}/{total_pages}",
                                                                         callback_data="noop")]
                                                                 ]))

            message_ids = [msg.message_id for msg in media_group_message]
            message_ids.append(action_message.message_id)
            await state.update_data(message_ids=message_ids)
        else:
            await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML,
                                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                       [
                                                           InlineKeyboardButton(text="⬅️ Назад",
                                                                                callback_data="prev_page"),
                                                           InlineKeyboardButton(text="❤️ В избранное",
                                                                                callback_data=f"fav_{property['id']}"),
                                                           InlineKeyboardButton(text="Вперед ➡️",
                                                                                callback_data="next_page")
                                                       ],
                                                       [
                                                           InlineKeyboardButton(text="🗺 Показать на карте",
                                                                                callback_data=f"map_{property['id']}")
                                                       ],
                                                       [
                                                           InlineKeyboardButton(text="📖 Читать отзывы и рейтинг",
                                                                                callback_data=f"read_reviews_{property['id']}")
                                                       ],
                                                       [
                                                           InlineKeyboardButton(text="🔚 Возврат в меню",
                                                                                callback_data="back_to_main")
                                                       ],
                                                       [InlineKeyboardButton(text=f"Страница {page + 1}/{total_pages}",
                                                                             callback_data="noop")]
                                                   ]))
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
