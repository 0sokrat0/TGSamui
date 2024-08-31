import logging

import aiomysql
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

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
        print("Successfully connected to the database.")


async def get_favorite_properties(user_id):
    query = """
    SELECT p.property_id, p.name, p.location, p.distance_to_sea, p.property_type, p.monthly_price, p.daily_price,
           p.booking_deposit_fixed, p.security_deposit, p.bedrooms, p.bathrooms, p.pool, p.kitchen, p.cleaning,
           p.utility_bill, p.description, r.avg_rating, p.photo1, p.photo2, p.photo3, p.photo4, p.photo5, 
           p.photo6, p.photo7, p.photo8, p.photo9
    FROM favorites f
    JOIN properties p ON f.property_id = p.property_id
    LEFT JOIN (SELECT property_id, AVG(rating) as avg_rating FROM reviews WHERE approved = 1 GROUP BY property_id) r
    ON p.property_id = r.property_id
    WHERE f.user_id = %s
    """
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, (user_id,))
            return await cursor.fetchall()

async def add_website_link_column():
    query = """
    ALTER TABLE properties ADD COLUMN website_link VARCHAR(255) DEFAULT NULL;
    """
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            await conn.commit()


async def get_property_by_id(property_id):
    query = """
    SELECT p.*, r.avg_rating
    FROM properties p
    LEFT JOIN (SELECT property_id, AVG(rating) as avg_rating FROM reviews WHERE approved = 1 GROUP BY property_id) r
    ON p.property_id = r.property_id
    WHERE p.property_id = %s
    """
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, (property_id,))
            return await cursor.fetchone()


def generate_property_buttons(property):
    buttons = [
        [InlineKeyboardButton(text="📞 Связь с менеджером", url="https://t.me/tropicalsamui")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del_{property['property_id']}")]
    ]

    # Добавляем кнопку со ссылкой на сайт, если ссылка указана
    if property.get('website_link'):
        buttons.append([InlineKeyboardButton(text="🌐 На сайт", url=property['website_link'])])

    # buttons.append([
    #     InlineKeyboardButton(text="✍️ Оставить отзыв и рейтинг", callback_data=f"review_{property['property_id']}"),
    #     InlineKeyboardButton(text="📖 Читать отзывы и рейтинги", callback_data=f"read_reviews_{property['property_id']}")
    # ])

    buttons.append([InlineKeyboardButton(text="🔙 Возврат к избранным", callback_data="back_to_favorites")])

    return buttons


def generate_property_text(property):


    return (
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


@router.callback_query(F.data == "favorites")
async def show_favorites(callback: CallbackQuery):
    await ensure_db_connection()
    user_id = callback.from_user.id

    favorite_properties = await get_favorite_properties(user_id)
    if not favorite_properties:
        await callback.message.answer("У вас нет избранных объектов/или объект удален")
        return

    buttons = [
        [InlineKeyboardButton(text=f"{property['name']}", callback_data=f"show_{property['property_id']}")]
        for property in favorite_properties
    ]

    buttons.append([InlineKeyboardButton(text="🔙 Возврат в меню", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer("Ваши избранные объекты:", reply_markup=keyboard)


@router.callback_query(F.data.startswith('show_'))
async def show_property_info(callback_query: CallbackQuery, state: FSMContext):
    property_id = int(callback_query.data.split('_')[1])
    property = await get_property_by_id(property_id)

    if not property:
        await callback_query.answer("Объект не найден.")
        return

    text = generate_property_text(property)
    keyboard = InlineKeyboardMarkup(inline_keyboard=generate_property_buttons(property))

    photos = [property[f'photo{i}'] for i in range(1, 10) if property.get(f'photo{i}')]

    if photos:
        media = [InputMediaPhoto(media=photos[0], caption=text, parse_mode=ParseMode.HTML)]
        media.extend([InputMediaPhoto(media=photo) for photo in photos[1:]])

        try:
            await callback_query.message.delete()
            media_group_message = await callback_query.message.answer_media_group(media=media)
            action_message = await callback_query.message.answer("Выберите действие:", reply_markup=keyboard)
            message_ids = [msg.message_id for msg in media_group_message]
            message_ids.append(action_message.message_id)
            await state.update_data(message_ids=message_ids)
        except Exception as e:
            logging.error(f"Ошибка при отправке группы медиа: {e}")
            await callback_query.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.callback_query(F.data.startswith('del_'))
async def remove_from_favorites_handler(callback_query: CallbackQuery):
    property_id = int(callback_query.data.split('_')[1])
    user_id = callback_query.from_user.id
    query = "DELETE FROM favorites WHERE user_id = %s AND property_id = %s"
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, (user_id, property_id))
            await conn.commit()
    await callback_query.answer("Удалено из избранного!")
    await show_favorites(callback_query)


@router.callback_query(F.data == "back_to_favorites")
async def back_to_favorites(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await show_favorites(callback_query)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback_query: CallbackQuery):
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=kb.main)
    await callback_query.answer()


# # Добавление нового отзыва пользователем
# class ReviewStates(StatesGroup):
#     waiting_for_review = State()
#     waiting_for_rating = State()
#
#
# @router.callback_query(F.data.startswith('review_'))
# async def start_review(callback_query: CallbackQuery, state: FSMContext):
#     property_id = int(callback_query.data.split('_')[1])
#     await state.update_data(property_id=property_id)
#     await callback_query.message.answer("Пожалуйста, введите ваш отзыв (вы можете использовать эмоджи):")
#     await callback_query.answer()
#     await state.set_state(ReviewStates.waiting_for_review)
#
#
# @router.message(ReviewStates.waiting_for_review)
# async def process_review(message: Message, state: FSMContext):
#     data = await state.get_data()
#     property_id = data["property_id"]
#     review = message.text
#     user_id = message.from_user.id
#     username = message.from_user.username
#
#     insert_query = """
#     INSERT INTO reviews (property_id, user_id, username, review, created_at, approved)
#     VALUES (%s, %s, %s, %s, NOW(), 0)
#     """
#     async with db.pool.acquire() as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute(insert_query, (property_id, user_id, username, review))
#             await conn.commit()
#
#     await message.answer("Спасибо за ваш отзыв! Теперь введите ваш рейтинг от 1 до 5 звезд:")
#     await state.set_state(ReviewStates.waiting_for_rating)
#
#
# @router.message(ReviewStates.waiting_for_rating)
# async def process_rating(message: Message, state: FSMContext):
#     try:
#         rating = int(message.text)
#         if rating < 1 or rating > 5:
#             await message.answer("Пожалуйста, введите число от 1 до 5.")
#             return
#     except ValueError:
#         await message.answer("Пожалуйста, введите число от 1 до 5.")
#         return
#
#     data = await state.get_data()
#     property_id = data['property_id']
#     user_id = message.from_user.id
#
#     update_query = """
#     UPDATE reviews
#     SET rating = %s
#     WHERE property_id = %s AND user_id = %s
#     ORDER BY created_at DESC
#     LIMIT 1
#     """
#     async with db.pool.acquire() as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute(update_query, (rating, property_id, user_id))
#             await conn.commit()
#
#     # Получение отзыва для отправки админу
#     query_get_review = """
#     SELECT review, review_id FROM reviews
#     WHERE property_id = %s AND user_id = %s
#     ORDER BY created_at DESC
#     LIMIT 1
#     """
#     async with db.pool.acquire() as conn:
#         async with conn.cursor(aiomysql.DictCursor) as cursor:
#             await cursor.execute(query_get_review, (property_id, user_id))
#             review_record = await cursor.fetchone()
#
#     review = review_record['review'] if review_record else 'Отзыв не найден'
#     review_id = review_record['review_id'] if review_record else None
#
#     # Уведомление админам
#     buttons = [
#         [InlineKeyboardButton(text="Одобрить", callback_data=f"approve_{review_id}")],
#         [InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{review_id}")]
#     ]
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
#
#     for admin_id in ADMINS:
#         try:
#             await message.bot.send_message(
#                 admin_id,
#                 f"Новый отзыв ожидает одобрения:\n\n"
#                 f"🏠 <b>Объект ID:</b> {property_id}\n"
#                 f"👤 <b>Пользователь:</b> @{message.from_user.username}\n"
#                 f"📝 <b>Отзыв:</b> {review}\n"
#                 f"⭐ <b>Рейтинг:</б> {rating}\n\n"
#                 "Перейдите в панель управления для одобрения или отклонения отзыва.",
#                 parse_mode=ParseMode.HTML,
#                 reply_markup=keyboard
#             )
#         except Exception as e:
#             logging.error(f"Не удалось отправить сообщение администратору {admin_id}: {e}")
#
#     await message.answer("Спасибо за ваш рейтинг! Ваш отзыв будет опубликован после проверки администратором.",
#                          reply_markup=kb.main)
#     await state.clear()
#
#
# @router.callback_query(F.data.startswith('read_reviews_'))
# async def read_reviews(callback_query: CallbackQuery):
#     property_id = int(callback_query.data.split('_')[2])
#
#     query_reviews = """
#     SELECT username, review, rating, created_at
#     FROM reviews
#     WHERE property_id = %s AND approved = 1
#     ORDER BY created_at DESC
#     """
#     async with db.pool.acquire() as conn:
#         async with conn.cursor(aiomysql.DictCursor) as cursor:
#             await cursor.execute(query_reviews, (property_id,))
#             reviews = await cursor.fetchall()
#
#     if reviews:
#         response = "Отзывы о недвижимости:\n\n"
#         for review in reviews:
#             stars = '★' * review['rating'] + '☆' * (5 - review['rating'])
#             response += f"👤 @{review['username']} ({review['created_at']}):\n📝 {review['review']}\n⭐ Рейтинг: {stars}\n\n"
#     else:
#         response = "Нет отзывов для данной недвижимости."
#
#     await callback_query.message.answer(response)
#     await callback_query.answer()
#
#
# # Обработка отзывов администратором
# @router.callback_query(F.data == "approve_reviews")
# async def approve_reviews(callback_query: CallbackQuery):
#     query = """
#     SELECT review_id, property_id, username, review, rating
#     FROM reviews
#     WHERE approved = 0
#     """
#     async with db.pool.acquire() as conn:
#         async with conn.cursor(aiomysql.DictCursor) as cursor:
#             await cursor.execute(query)
#             pending_reviews = await cursor.fetchall()
#
#     if not pending_reviews:
#         await callback_query.message.answer("Нет отзывов для одобрения.")
#         return
#
#     for review in pending_reviews:
#         text = (
#             f"Отзыв от @{review['username']} для объекта с ID {review['property_id']}:\n\n"
#             f"📝 Отзыв: {review['review']}\n"
#             f"⭐ Рейтинг: {'⭐' * review['rating']}\n\n"
#             f"Одобрить этот отзыв?"
#         )
#         buttons = [
#             [InlineKeyboardButton(text="Да", callback_data=f"approve_{review['review_id']}")],
#             [InlineKeyboardButton(text="Нет", callback_data=f"reject_{review['review_id']}")]
#         ]
#         keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
#         await callback_query.message.answer(text, reply_markup=keyboard)
#
#
# @router.callback_query(F.data.startswith('approve_'))
# async def approve_review(callback_query: CallbackQuery):
#     review_id = int(callback_query.data.split('_')[1])
#     query = "UPDATE reviews SET approved = 1 WHERE review_id = %s"
#     async with db.pool.acquire() as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute(query, (review_id,))
#             await conn.commit()
#     await callback_query.answer("Отзыв одобрен.", show_alert=True)
#
#
# @router.callback_query(F.data.startswith('reject_'))
# async def reject_review(callback_query: CallbackQuery):
#     review_id = int(callback_query.data.split('_')[1])
#     query = "DELETE FROM reviews WHERE review_id = %s"
#     async with db.pool.acquire() as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute(query, (review_id,))
#             await conn.commit()
#     await callback_query.answer("Отзыв отклонен.", show_alert=True)
#
