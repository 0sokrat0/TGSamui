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
# @router.message(ReviewStates.waiting_for_review)
# async def process_review(message: Message, state: FSMContext):
#     review_data = await state.get_data()
#     property_id = review_data["property_id"]
#     review = message.text
#     user_id = message.from_user.id
#     username = message.from_user.username
#
#     await db.ensure_connection()
#
#     # Вставка нового отзыва
#     insert_query = "INSERT INTO reviews (property_id, user_id, username, review, created_at) VALUES (%s, %s, %s, %s, NOW())"
#     insert_params = (property_id, user_id, username, review)
#     async with db.pool.acquire() as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute(insert_query, insert_params)
#             await conn.commit()
#
#     await message.answer("Спасибо за ваш отзыв! Теперь введите ваш рейтинг от 1 до 5 звезд:")
#     await state.set_state(ReviewStates.waiting_for_rating)
#
# @router.message(ReviewStates.waiting_for_rating)
# async def process_rating(message: Message, state: FSMContext):
#     rating = int(message.text)
#     if rating < 1 or rating > 5:
#         await message.answer("Пожалуйста, введите число от 1 до 5.")
#         return
#
#     data = await state.get_data()
#     property_id = data['property_id']
#     user_id = message.from_user.id
#
#     await db.ensure_connection()
#
#     query = """
#     UPDATE reviews
#     SET rating = %s
#     WHERE property_id = %s AND user_id = %s
#     ORDER BY created_at DESC
#     LIMIT 1
#     """
#     params = (rating, property_id, user_id)
#
#     async with db.pool.acquire() as conn:
#         async with conn.cursor() as cursor:
#             await cursor.execute(query, params)
#             await conn.commit()
#
#     await message.answer("Спасибо за ваш рейтинг!", reply_markup=kb.main)
#     await state.clear()
#
# @router.callback_query(F.data.startswith('read_reviews_'))
# async def read_reviews(callback_query: CallbackQuery):
#     property_id = int(callback_query.data.split('_')[2])
#     await db.ensure_connection()
#
#     query_reviews = "SELECT username, review, rating, created_at FROM reviews WHERE property_id = %s"
#     params = (property_id,)
#
#     async with db.pool.acquire() as conn:
#         async with conn.cursor(aiomysql.DictCursor) as cursor:
#             await cursor.execute(query_reviews, params)
#             reviews = await cursor.fetchall()
#
#     if reviews:
#         response = "Отзывы о недвижимости:\n\n"
#         for review in reviews:
#             rating = review['rating'] if review['rating'] is not None else 0
#             stars = '★' * rating + '☆' * (5 - rating)
#             response += f"@{review['username']} ({review['created_at']}):\n{review['review']}\nРейтинг: {stars}\n\n"
#     else:
#         response = "Нет отзывов для данной недвижимости."
#
#     await callback_query.message.answer(response)
#     await callback_query.answer()


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


@router.callback_query(F.data == "best_properties")
async def show_top_properties(callback: CallbackQuery):
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
        await callback.answer("Нет объектов с отзывами.")
        await callback.message.answer("Нет объектов с отзывами.")
        return

    buttons = [
        [InlineKeyboardButton(text=f"{property['name']} - ⭐ {property['avg_rating']:.1f}",
                              callback_data=f"show_{property['property_id']}")]
        for property in top_properties
    ]
    buttons.append([InlineKeyboardButton(text="🔚 Возврат в меню", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.answer("🌟 Лучшие объекты недвижимости")
    await callback.message.answer("🌟 Лучшие объекты недвижимости:", reply_markup=keyboard)


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback_query: CallbackQuery):
    await db.update_last_activity(callback_query.from_user.id)
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=kb.main)
    await callback_query.answer()
