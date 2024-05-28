# app/admin.py
import logging

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery
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
            KeyboardButton(text="🗑️ Удалить карточку"),
            KeyboardButton(text="✏️ Редактировать карточку"),
            KeyboardButton(text="📜 Просмотреть все карточки")
        ],
        [
            KeyboardButton(text="📊 Аналитика"),
            KeyboardButton(text="✉️ Создать рассылку")
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
@router.message(Command('panel'))
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
    waiting_for_delete_id = State()
    waiting_for_edit_id = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()
    confirm_deletion = State()
    confirm_edit = State()

# Начало создания карточки
@router.message(F.text == "📋 Создать карточку")
async def start_property_creation(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Введите название объекта:")
        await state.set_state(NewProperty.waiting_for_name)
    else:
        await message.answer('У вас нет доступа к этой команде.')

# Ввод названия объекта
@router.message(NewProperty.waiting_for_name)
async def property_name_received(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отправьте ссылку на первое фото:")
    await state.set_state(NewProperty.waiting_for_photo1)

# Ввод первого фото
@router.message(NewProperty.waiting_for_photo1)
async def property_photo1_received(message: Message, state: FSMContext):
    await state.update_data(photo1=message.text)
    await message.answer("Отправьте ссылку на второе фото:")
    await state.set_state(NewProperty.waiting_for_photo2)

# Ввод второго фото
@router.message(NewProperty.waiting_for_photo2)
async def property_photo2_received(message: Message, state: FSMContext):
    await state.update_data(photo2=message.text)
    await message.answer("Отправьте ссылку на третье фото:")
    await state.set_state(NewProperty.waiting_for_photo3)

# Ввод третьего фото
@router.message(NewProperty.waiting_for_photo3)
async def property_photo3_received(message: Message, state: FSMContext):
    await state.update_data(photo3=message.text)
    await message.answer("Введите расположение объекта:")
    await state.set_state(NewProperty.waiting_for_location)

# Ввод расположения объекта
@router.message(NewProperty.waiting_for_location)
async def property_location_received(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Введите удаленность от моря:")
    await state.set_state(NewProperty.waiting_for_distance_to_sea)

# Ввод удаленности от моря
@router.message(NewProperty.waiting_for_distance_to_sea)
async def property_distance_to_sea_received(message: Message, state: FSMContext):
    await state.update_data(distance_to_sea=message.text)
    await message.answer("Введите тип жилья:")
    await state.set_state(NewProperty.waiting_for_property_type)

# Ввод типа жилья
@router.message(NewProperty.waiting_for_property_type)
async def property_type_received(message: Message, state: FSMContext):
    await state.update_data(property_type=message.text)
    await message.answer("Введите стоимость в месяц:")
    await state.set_state(NewProperty.waiting_for_monthly_price)

# Ввод стоимости в месяц
@router.message(NewProperty.waiting_for_monthly_price)
async def property_monthly_price_received(message: Message, state: FSMContext):
    await state.update_data(monthly_price=message.text)
    await message.answer("Введите стоимость постуточно:")
    await state.set_state(NewProperty.waiting_for_daily_price)

# Ввод стоимости постуточно
@router.message(NewProperty.waiting_for_daily_price)
async def property_daily_price_received(message: Message, state: FSMContext):
    await state.update_data(daily_price=message.text)
    await message.answer("Введите фиксированный депозит для брони:")
    await state.set_state(NewProperty.waiting_for_booking_deposit_fixed)

# Ввод фиксированного депозита
@router.message(NewProperty.waiting_for_booking_deposit_fixed)
async def property_booking_deposit_fixed_received(message: Message, state: FSMContext):
    await state.update_data(booking_deposit_fixed=message.text)
    await message.answer("Введите сохраненный депозит:")
    await state.set_state(NewProperty.waiting_for_security_deposit)

# Ввод сохраненного депозита
@router.message(NewProperty.waiting_for_security_deposit)
async def property_security_deposit_received(message: Message, state: FSMContext):
    await state.update_data(security_deposit=message.text)
    await message.answer("Введите количество спален:")
    await state.set_state(NewProperty.waiting_for_bedrooms)

# Ввод количества спален
@router.message(NewProperty.waiting_for_bedrooms)
async def property_bedrooms_received(message: Message, state: FSMContext):
    await state.update_data(bedrooms=message.text)
    await message.answer("Введите количество ванных комнат:")
    await state.set_state(NewProperty.waiting_for_bathrooms)

# Ввод количества ванных комнат
@router.message(NewProperty.waiting_for_bathrooms)
async def property_bathrooms_received(message: Message, state: FSMContext):
    await state.update_data(bathrooms=message.text)
    await message.answer("Есть ли бассейн? (Да/Нет):")
    await state.set_state(NewProperty.waiting_for_pool)

# Ввод информации о бассейне
@router.message(NewProperty.waiting_for_pool)
async def property_pool_received(message: Message, state: FSMContext):
    await state.update_data(pool=message.text)
    await message.answer("Есть ли кухня? (Да/Нет):")
    await state.set_state(NewProperty.waiting_for_kitchen)

# Ввод информации о кухне
@router.message(NewProperty.waiting_for_kitchen)
async def property_kitchen_received(message: Message, state: FSMContext):
    await state.update_data(kitchen=message.text)
    await message.answer("Есть ли уборка? (Да/Нет):")
    await state.set_state(NewProperty.waiting_for_cleaning)

# Ввод информации об уборке
@router.message(NewProperty.waiting_for_cleaning)
async def property_cleaning_received(message: Message, state: FSMContext):
    await state.update_data(cleaning=message.text)
    await message.answer("Введите описание:")
    await state.set_state(NewProperty.waiting_for_description)

# Ввод описания объекта
@router.message(NewProperty.waiting_for_description)
async def property_description_received(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите утилиты (вода, электричество и т.д.):")
    await state.set_state(NewProperty.waiting_for_utility_bill)

# Ввод информации об утилитах
@router.message(NewProperty.waiting_for_utility_bill)
async def property_utility_bill_received(message: Message, state: FSMContext):
    await state.update_data(utility_bill=message.text)

    await db.ensure_connection()

    property_data = await state.get_data()

    query = """
    INSERT INTO properties (name, photo1, photo2, photo3, location, distance_to_sea, property_type,
                            monthly_price, daily_price, booking_deposit_fixed, security_deposit, bedrooms,
                            bathrooms, pool, kitchen, cleaning, description, utility_bill)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        property_data['name'], property_data['photo1'], property_data['photo2'], property_data['photo3'],
        property_data['location'], property_data['distance_to_sea'], property_data['property_type'],
        property_data['monthly_price'], property_data['daily_price'], property_data['booking_deposit_fixed'],
        property_data['security_deposit'], property_data['bedrooms'], property_data['bathrooms'],
        property_data['pool'], property_data['kitchen'], property_data['cleaning'],
        property_data['description'], property_data['utility_bill']
    )

    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            await conn.commit()

    await message.answer("Карточка недвижимости успешно создана!", reply_markup=admins_panel)
    await state.clear()

# Начало удаления карточки
@router.message(F.text == "🗑️ Удалить карточку")
async def start_property_deletion(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Введите ID карточки недвижимости, которую вы хотите удалить:")
        await state.set_state(NewProperty.waiting_for_delete_id)
    else:
        await message.answer('У вас нет доступа к этой команде.')

# Ввод ID карточки для удаления
@router.message(NewProperty.waiting_for_delete_id)
async def delete_property_id_received(message: Message, state: FSMContext):
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
            InlineKeyboardButton(text="Фото 2", callback_data="edit_photo2"),
            InlineKeyboardButton(text="Фото 3", callback_data="edit_photo3")
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
        ]
    ]
)

# Начало редактирования карточки
@router.message(F.text == "✏️ Редактировать карточку")
async def start_property_editing(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer("Введите ID карточки недвижимости, которую вы хотите отредактировать:")
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

# Ввод поля для редактирования через кнопки
@router.callback_query(NewProperty.waiting_for_edit_field)
async def edit_property_field_received(callback_query: types.CallbackQuery, state: FSMContext):
    selected_field = callback_query.data.replace("edit_", "")
    await state.update_data(selected_field=selected_field)
    await callback_query.message.answer(f"Введите новое значение для поля {selected_field}:")
    await state.set_state(NewProperty.waiting_for_edit_value)
    await callback_query.answer()

# Ввод нового значения для выбранного поля
@router.message(NewProperty.waiting_for_edit_value)
async def edit_property_value_received(message: Message, state: FSMContext):
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
    await state.update_data(subject=message.text)
    await message.answer("Введите текст рассылки:")
    await state.set_state(Newsletter.waiting_for_message)


# Ввод текста рассылки
@router.message(Newsletter.waiting_for_message)
async def newsletter_message_received(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await message.answer("Отправьте фото для рассылки (если есть) или нажмите /skip:")
    await state.set_state(Newsletter.waiting_for_photo)


# Ввод фото или текста для рассылки
@router.message(Newsletter.waiting_for_photo, F.photo)
async def newsletter_photo_received(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data(photo=photo)
    await message.answer("Фото добавлено. Вы уверены, что хотите отправить эту рассылку всем пользователям? (Да/Нет)")
    await state.set_state(Newsletter.confirm_sending)


@router.message(Newsletter.waiting_for_photo, F.text)
async def newsletter_text_received(message: Message, state: FSMContext):
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




@router.message(F.text == "🔔 Уведомления")
async def manage_notifications(message: Message):
    await db.ensure_connection()
    await db.update_last_activity(message.from_user.id)

    response_text = "Выберите, что вы хотите сделать с уведомлениями:"
    await message.answer(response_text, reply_markup=kb.notification_keyboard)


@router.callback_query(F.data == "subscribe_notifications")
async def subscribe_notifications(callback_query: CallbackQuery):
    await db.ensure_connection()
    await db.update_last_activity(callback_query.from_user.id)
    user_id = callback_query.from_user.id

    await db.subscribe_to_notifications(user_id)
    await callback_query.message.answer("Вы успешно подписаны на уведомления!", reply_markup=kb.main)
    await callback_query.answer()


@router.callback_query(F.data == "unsubscribe_notifications")
async def unsubscribe_notifications(callback_query: CallbackQuery):
    await db.ensure_connection()
    await db.update_last_activity(callback_query.from_user.id)
    user_id = callback_query.from_user.id

    await db.unsubscribe_from_notifications(user_id)
    await callback_query.message.answer("Вы успешно отписаны от уведомлений.", reply_markup=kb.main)
    await callback_query.answer()


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
