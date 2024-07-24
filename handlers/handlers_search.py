import asyncio
import logging

import aiomysql
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from config import db_config
from database.database import Database

router = Router()
db = Database(db_config)


class PropertyFilter(StatesGroup):
    choosing_type = State()
    choosing_beds = State()
    choosing_distance = State()
    choosing_price = State()
    showing_results = State()


class ReviewState(StatesGroup):
    writing_review = State()


async def ensure_db_connection():
    if db.pool is None:
        await db.connect()
        if db.pool is None:
            raise Exception("Failed to connect to the database")
        logging.info("Database connected successfully.")


@router.callback_query(F.data == "search_property")
async def search_real_estate(callback_query: CallbackQuery, state: FSMContext):
    types = ["🏡 Вилла", "🏢 Кондо", "🏬 Апартаменты", "🏘 Дом в резорте", "🏚 Cтудия в резорте"]
    buttons = [[InlineKeyboardButton(text=t, callback_data=f"type_{t.split(' ')[1]}")] for t in types]
    buttons.append([InlineKeyboardButton(text="Пропустить", callback_data="skip_all")])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.answer("Выберите тип жилья или пропустите:")
    await callback_query.message.answer("Выберите тип жилья или пропустите:", reply_markup=markup)
    await state.set_state(PropertyFilter.choosing_type)


@router.callback_query(F.data == "skip_all")
async def skip_all_filters(callback_query: CallbackQuery, state: FSMContext):
    await ensure_db_connection()
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
    await callback_query.message.edit_text("Введите диапазон цен или пропустите (например: 1000-5000):",
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                               [InlineKeyboardButton(text="Пропустить", callback_data="skip_price")]
                                           ]))


@router.callback_query(F.data == "skip_price")
async def skip_price_filter(callback_query: CallbackQuery, state: FSMContext):
    await ensure_db_connection()
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
    await ensure_db_connection()
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

    distance_condition = ""
    if distance_to_sea == "<100м":
        distance_condition = "CAST(distance_to_sea AS SIGNED) < 100"
    elif distance_to_sea == "100-500м":
        distance_condition = "CAST(distance_to_sea AS SIGNED) BETWEEN 100 AND 500"
    elif distance_to_sea == ">500м":
        distance_condition = "CAST(distance_to_sea AS SIGNED) > 500"

    price_condition = ""
    if price_range:
        min_price, max_price = map(int, price_range.split('-'))
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
