import asyncio
import logging
import logging
import sys

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат логов
    handlers=[
        logging.StreamHandler(sys.stdout)  # Вывод логов в консоль
    ]
)

logger = logging.getLogger(__name__)
from aiogram_dialog.widgets.kbd import Select, Column
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm import state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, \
    InputMediaPhoto

from aiogram_dialog import Dialog, DialogManager, setup_dialogs, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput
from config import TOKEN, ADMINS, db_config, CHANNEL_ID
from database.database import Database
import pandas as pd
from datetime import datetime


class ScheduleAnnouncementSG(StatesGroup):
    waiting_for_announcement_selection = State()
    waiting_for_schedule_time = State()
    confirming_scheduled_announcement = State()


class EditPropertySG(StatesGroup):
    waiting_for_property_selection = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()
    confirm_edit = State()  # Добавляем недостающее состояние

class StartSG(StatesGroup):
    start = State()

class ViewPropertiesSG(StatesGroup):
    view_properties = State()
    view_properties_page = State()

class ViewAnalyticsSG(StatesGroup):
    view_analytics = State()

class NewAnnouncementSG(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_photo_count = State()  # Добавлено
    waiting_for_photo = State()  # Добавлено
    waiting_for_button_count = State()  # Добавлено
    waiting_for_button_text = State()  # Добавлено
    waiting_for_button_url = State()  # Добавлено
    confirming_announcement = State()


class ExportDataSG(StatesGroup):
    export_menu = State()
    export_properties = State()
    export_users = State()

class DeletePropertySG(StatesGroup):
    waiting_for_property_selection = State()
    confirming_deletion = State()

class NewPropertySG(StatesGroup):
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
    waiting_for_minimum_nights = State()
    waiting_for_booking_deposit_fixed = State()
    waiting_for_booking_deposit_percentage = State()
    waiting_for_security_deposit = State()
    waiting_for_bedrooms = State()
    waiting_for_beds = State()
    waiting_for_bathrooms = State()
    waiting_for_pool = State()
    waiting_for_kitchen = State()
    waiting_for_air_conditioners = State()
    waiting_for_cleaning = State()
    waiting_for_description = State()
    waiting_for_utility_bill = State()
    waiting_for_latitude = State()
    waiting_for_longitude = State()
    waiting_for_reviews = State()
    confirming_data = State()


db = Database(db_config)





async def update_data_and_next(message: Message, dialog_manager: DialogManager, key: str, value: str):
    logging.info(f"Updating {key} with value: {value}")
    dialog_manager.current_context().dialog_data[key] = value
    await dialog_manager.next()

async def on_success_property_name(message: Message, widget: TextInput, dialog_manager: DialogManager, name: str):
    await update_data_and_next(message, dialog_manager, 'name', name)

async def on_success_property_photo1(message: Message, widget: TextInput, dialog_manager: DialogManager, photo1: str):
    await update_data_and_next(message, dialog_manager, 'photo1', photo1)

async def on_success_property_photo2(message: Message, widget: TextInput, dialog_manager: DialogManager, photo2: str):
    await update_data_and_next(message, dialog_manager, 'photo2', photo2)

async def on_success_property_photo3(message: Message, widget: TextInput, dialog_manager: DialogManager, photo3: str):
    await update_data_and_next(message, dialog_manager, 'photo3', photo3)

async def on_success_property_photo4(message: Message, widget: TextInput, dialog_manager: DialogManager, photo4: str):
    await update_data_and_next(message, dialog_manager, 'photo4', photo4)

async def on_success_property_photo5(message: Message, widget: TextInput, dialog_manager: DialogManager, photo5: str):
    await update_data_and_next(message, dialog_manager, 'photo5', photo5)

async def on_success_property_photo6(message: Message, widget: TextInput, dialog_manager: DialogManager, photo6: str):
    await update_data_and_next(message, dialog_manager, 'photo6', photo6)

async def on_success_property_photo7(message: Message, widget: TextInput, dialog_manager: DialogManager, photo7: str):
    await update_data_and_next(message, dialog_manager, 'photo7', photo7)

async def on_success_property_photo8(message: Message, widget: TextInput, dialog_manager: DialogManager, photo8: str):
    await update_data_and_next(message, dialog_manager, 'photo8', photo8)

async def on_success_property_photo9(message: Message, widget: TextInput, dialog_manager: DialogManager, photo9: str):
    await update_data_and_next(message, dialog_manager, 'photo9', photo9)

async def on_success_property_location(message: Message, widget: TextInput, dialog_manager: DialogManager, location: str):
    await update_data_and_next(message, dialog_manager, 'location', location)

async def on_success_property_distance_to_sea(message: Message, widget: TextInput, dialog_manager: DialogManager, distance_to_sea: str):
    if not distance_to_sea.isdigit():
        await message.answer("Введите корректное числовое значение для расстояния до моря.")
        return
    await update_data_and_next(message, dialog_manager, 'distance_to_sea', distance_to_sea)

async def on_success_property_type(message: Message, widget: TextInput, dialog_manager: DialogManager, property_type: str):
    await update_data_and_next(message, dialog_manager, 'property_type', property_type)

async def on_success_property_monthly_price(message: Message, widget: TextInput, dialog_manager: DialogManager, monthly_price: str):
    if not monthly_price.isdigit():
        await message.answer("Введите корректное числовое значение для ежемесячной стоимости.")
        return
    await update_data_and_next(message, dialog_manager, 'monthly_price', monthly_price)

async def on_success_property_daily_price(message: Message, widget: TextInput, dialog_manager: DialogManager, daily_price: str):
    if not daily_price.isdigit():
        await message.answer("Введите корректное числовое значение для ежедневной стоимости.")
        return
    await update_data_and_next(message, dialog_manager, 'daily_price', daily_price)

async def on_success_property_minimum_nights(message: Message, widget: TextInput, dialog_manager: DialogManager, minimum_nights: str):
    if not minimum_nights.isdigit():
        await message.answer("Введите корректное числовое значение для минимального количества ночей.")
        return
    await update_data_and_next(message, dialog_manager, 'minimum_nights', minimum_nights)

async def on_success_property_booking_deposit_fixed(message: Message, widget: TextInput, dialog_manager: DialogManager, booking_deposit_fixed: str):
    if not booking_deposit_fixed.isdigit():
        await message.answer("Введите корректное числовое значение для фиксированного депозита.")
        return
    await update_data_and_next(message, dialog_manager, 'booking_deposit_fixed', booking_deposit_fixed)

async def on_success_property_booking_deposit_percentage(message: Message, widget: TextInput, dialog_manager: DialogManager, booking_deposit_percentage: str):
    if not booking_deposit_percentage.isdigit():
        await message.answer("Введите корректное числовое значение для процентного депозита.")
        return
    await update_data_and_next(message, dialog_manager, 'booking_deposit_percentage', booking_deposit_percentage)

async def on_success_property_security_deposit(message: Message, widget: TextInput, dialog_manager: DialogManager, security_deposit: str):
    if not security_deposit.isdigit():
        await message.answer("Введите корректное числовое значение для депозита безопасности.")
        return
    await update_data_and_next(message, dialog_manager, 'security_deposit', security_deposit)

async def on_success_property_bedrooms(message: Message, widget: TextInput, dialog_manager: DialogManager, bedrooms: str):
    if not bedrooms.isdigit():
        await message.answer("Введите корректное числовое значение для количества спален.")
        return
    await update_data_and_next(message, dialog_manager, 'bedrooms', bedrooms)

async def on_success_property_beds(message: Message, widget: TextInput, dialog_manager: DialogManager, beds: str):
    if not beds.isdigit():
        await message.answer("Введите корректное числовое значение для количества кроватей.")
        return
    await update_data_and_next(message, dialog_manager, 'beds', beds)

async def on_success_property_bathrooms(message: Message, widget: TextInput, dialog_manager: DialogManager, bathrooms: str):
    if not bathrooms.isdigit():
        await message.answer("Введите корректное числовое значение для количества ванных комнат.")
        return
    await update_data_and_next(message, dialog_manager, 'bathrooms', bathrooms)

async def on_success_property_pool(message: Message, widget: TextInput, dialog_manager: DialogManager, pool: str):
    await update_data_and_next(message, dialog_manager, 'pool', pool)

async def on_success_property_kitchen(message: Message, widget: TextInput, dialog_manager: DialogManager, kitchen: str):
    await update_data_and_next(message, dialog_manager, 'kitchen', kitchen)

async def on_success_property_air_conditioners(message: Message, widget: TextInput, dialog_manager: DialogManager, air_conditioners: str):
    await update_data_and_next(message, dialog_manager, 'air_conditioners', air_conditioners)

async def on_success_property_cleaning(message: Message, widget: TextInput, dialog_manager: DialogManager, cleaning: str):
    await update_data_and_next(message, dialog_manager, 'cleaning', cleaning)

async def on_success_property_description(message: Message, widget: TextInput, dialog_manager: DialogManager, description: str):
    await update_data_and_next(message, dialog_manager, 'description', description)

async def on_success_property_utility_bill(message: Message, widget: TextInput, dialog_manager: DialogManager, utility_bill: str):
    await update_data_and_next(message, dialog_manager, 'utility_bill', utility_bill)


async def save_property_data(dialog_manager: DialogManager):
    property_data = dialog_manager.current_context().dialog_data
    logging.info(f"Saving property data: {property_data}")
    await db.ensure_connection()

    query = """
    INSERT INTO properties (
        name, photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8, photo9,
        location, distance_to_sea, property_type, monthly_price, daily_price, minimum_nights,
        booking_deposit_fixed, booking_deposit_percentage, security_deposit, bedrooms,
        beds, bathrooms, pool, kitchen, air_conditioners, cleaning, description, utility_bill
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    params = (
        property_data.get('name'), property_data.get('photo1'), property_data.get('photo2'),
        property_data.get('photo3'), property_data.get('photo4'), property_data.get('photo5'),
        property_data.get('photo6'), property_data.get('photo7'), property_data.get('photo8'),
        property_data.get('photo9'), property_data.get('location'), property_data.get('distance_to_sea'),
        property_data.get('property_type'), property_data.get('monthly_price'), property_data.get('daily_price'),
        property_data.get('minimum_nights'), property_data.get('booking_deposit_fixed'), property_data.get('booking_deposit_percentage'), property_data.get('security_deposit'),
        property_data.get('bedrooms'), property_data.get('beds'), property_data.get('bathrooms'), property_data.get('pool'),
        property_data.get('kitchen'), property_data.get('air_conditioners'), property_data.get('cleaning'), property_data.get('description'),
        property_data.get('utility_bill')
    )

    if len(params) != 28:  # 27 это количество ожидаемых параметров
        logging.error(f"Количество параметров не соответствует ожидаемому. Ожидается 27, получено: {len(params)}")
    else:
        try:
            async with db.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    await conn.commit()
            await dialog_manager.event.answer("Карточка недвижимости успешно создана!")
            await dialog_manager.done()
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            await dialog_manager.event.answer(f"Произошла ошибка при создании карточки: {e}")
            await dialog_manager.done()

async def on_confirm_data(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await save_property_data(dialog_manager)

async def on_create_property(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(NewPropertySG.waiting_for_name)

async def cancel_action(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await callback.message.answer("❌ Действие отменено.")

async def on_skip_photo(callback: CallbackQuery, dialog_manager: DialogManager, key: str):
    logging.info(f"Skipping {key} and setting value to NULL")
    dialog_manager.current_context().dialog_data[key] = None
    await dialog_manager.next()


async def go_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def on_delete_property(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(DeletePropertySG.waiting_for_property_selection)


async def on_edit_property(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(EditPropertySG.waiting_for_property_selection)

async def view_all_properties(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    if user_id in ADMINS:
        await db.ensure_connection()
        query = "SELECT property_id, name FROM properties"
        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                properties = await cursor.fetchall()
        dialog_manager.current_context().dialog_data['properties'] = properties
        return {"properties": properties}
    else:
        return {"properties": []}

async def on_property_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    current_data = dialog_manager.current_context().dialog_data
    properties = current_data.get("properties", [])
    selected_property = next((item for item in properties if str(item[0]) == item_id), None)
    if selected_property:
        dialog_manager.current_context().dialog_data['selected_property_id'] = selected_property[0]
        dialog_manager.current_context().dialog_data['selected_property_name'] = selected_property[1]
        await dialog_manager.next()
    else:
        await callback.message.answer("Ошибка: выбранный объект недвижимости не найден.")

async def on_edit_field_selected(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    selected_field = callback.data.replace("edit_", "")
    property_id = dialog_manager.current_context().dialog_data.get('selected_property_id')

    # Получаем текущее значение поля из базы данных
    await db.ensure_connection()
    query = f"SELECT {selected_field} FROM properties WHERE property_id = %s"
    params = (property_id,)
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            current_value = await cursor.fetchone()

    dialog_manager.current_context().dialog_data['selected_field'] = selected_field
    current_value_text = current_value[0] if current_value else "Не задано"

    await callback.message.answer(
        f"Текущее значение для поля {selected_field}: {current_value_text}\nВведите новое значение:")
    await dialog_manager.switch_to(EditPropertySG.waiting_for_edit_value)
    await callback.answer()


async def on_new_value_received(message: Message, widget: TextInput, dialog_manager: DialogManager, new_value: str):
    dialog_manager.current_context().dialog_data['new_value'] = new_value

    confirm_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_edit"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")
        ]
    ])

    await message.answer(f"Вы уверены, что хотите изменить значение на '{new_value}'?", reply_markup=confirm_buttons)
    await dialog_manager.switch_to(EditPropertySG.confirm_edit)  # Переход в состояние подтверждения








async def on_edit_confirmed(message: Message, dialog_manager: DialogManager):
    confirmation = message.text.lower()
    if confirmation == "да":
        data = dialog_manager.current_context().dialog_data
        property_id = data['selected_property_id']
        selected_field = data['selected_field']
        new_value = data['new_value']
        await db.ensure_connection()
        query = f"UPDATE properties SET {selected_field} = %s WHERE property_id = %s"
        params = (new_value, property_id)
        try:
            async with db.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    await conn.commit()
            await message.answer(f"Поле {selected_field} успешно обновлено!")
        except Exception as e:
            logging.error(f"Ошибка выполнения запроса: {e}")
            await message.answer(f"Произошла ошибка при обновлении: {e}")
    else:
        await message.answer("Редактирование отменено.")
    await dialog_manager.done()

async def on_view_properties(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(ViewPropertiesSG.view_properties)




async def view_all_properties(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    if user_id in ADMINS:
        await db.ensure_connection()

        query = "SELECT property_id, name FROM properties"
        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                properties = await cursor.fetchall()

        if properties:
            dialog_manager.current_context().dialog_data['properties'] = properties
            return {"properties": properties}
        else:
            dialog_manager.current_context().dialog_data['properties'] = []
            return {"properties": []}
    else:
        dialog_manager.current_context().dialog_data['properties'] = []
        return {"properties": []}




async def view_properties_page_getter(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    if user_id in ADMINS:
        await db.ensure_connection()

        query = "SELECT property_id, name, location, monthly_price, daily_price FROM properties"
        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                properties = await cursor.fetchall()

        # Получаем текущую страницу из данных диалога
        current_page = dialog_manager.current_context().dialog_data.get("current_page", 0)
        items_per_page = 5
        total_pages = (len(properties) + items_per_page - 1) // items_per_page

        # Срез для текущей страницы
        start_index = current_page * items_per_page
        end_index = start_index + items_per_page
        page_properties = properties[start_index:end_index]

        response = "Список всех объектов недвижимости:\n\n" + "\n".join(
            [
                (
                    f"ID: {prop[0]}\n"
                    f"Название: {prop[1]}\n"
                    f"Расположение: {prop[2]}\n"
                    f"Ежемесячная цена: {prop[3]} THB\n"
                    f"Ежедневная цена: {prop[4]} THB\n"
                    "--------------------------"
                )
                for prop in page_properties
            ]
        )

        return {
            "properties_list": response,
            "current_page": current_page,
            "total_pages": total_pages,
        }
    else:
        return {"properties_list": "У вас нет доступа к этой команде."}

async def on_next_page(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    current_page = dialog_manager.current_context().dialog_data.get("current_page", 0)
    dialog_manager.current_context().dialog_data["current_page"] = current_page + 1
    await dialog_manager.switch_to(ViewPropertiesSG.view_properties_page)

async def on_previous_page(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    current_page = dialog_manager.current_context().dialog_data.get("current_page", 0)
    if current_page > 0:
        dialog_manager.current_context().dialog_data["current_page"] = current_page - 1
    await dialog_manager.switch_to(ViewPropertiesSG.view_properties_page)




async def on_back_to_menu(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(StartSG.start)

async def on_view_analytics(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(ViewAnalyticsSG.view_analytics)

async def show_analytics(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    if user_id in ADMINS:
        await db.ensure_connection()

        stats = await db.get_detailed_user_statistics()
        response_text = (
            f"📊 <b>Аналитика активности пользователей:</b>\n\n"
            f"👥 <b>Всего пользователей:</b> {stats['total_users']}\n"
            f"🟢 <b>Активные пользователи (за последнюю неделю):</b> {stats['active_users']}\n"
            f"🆕 <b>Новые пользователи (за последнюю неделю):</b> {stats['new_users']}\n"
        )
        return {"analytics_data": response_text}
    else:
        return {"analytics_data": "У вас нет доступа к этой команде."}

async def on_view_properties(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(ViewPropertiesSG.view_properties_page)

async def on_export_data(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(ExportDataSG.export_menu)


async def on_property_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    current_data = dialog_manager.current_context().dialog_data
    properties = current_data.get("properties", [])
    selected_property = next((item for item in properties if str(item[0]) == item_id), None)

    if selected_property:
        dialog_manager.current_context().dialog_data['selected_property_id'] = selected_property[0]
        dialog_manager.current_context().dialog_data['selected_property_name'] = selected_property[1]
        await dialog_manager.update(
            {"selected_property_id": selected_property[0], "selected_property_name": selected_property[1]})
        await dialog_manager.next()
    else:
        await callback.message.answer("Ошибка: выбранный объект недвижимости не найден.")


async def on_confirm_deletion(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    property_id = dialog_manager.current_context().dialog_data.get('selected_property_id')
    await db.ensure_connection()

    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Удаление всех связанных записей в таблице reviews
            delete_reviews_query = "DELETE FROM reviews WHERE property_id = %s"
            await cursor.execute(delete_reviews_query, (property_id,))

            # Удаление записи из таблицы properties
            delete_property_query = "DELETE FROM properties WHERE property_id = %s"
            await cursor.execute(delete_property_query, (property_id,))

            await conn.commit()

    await callback.message.answer(f"Карточка недвижимости с ID {property_id} успешно удалена!")
    await dialog_manager.done()


async def on_export_properties(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
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

            await callback.message.answer_document(
                file,
                caption=f'Актуальный на <b>{datetime.now().strftime("%d-%m-%Y")}</b>',
                parse_mode='HTML'
            )
        else:
            await callback.message.answer("Нет данных для экспорта.")
    except Exception as e:
        await callback.message.answer(f"Ошибка при экспорте данных: {str(e)}")

    await dialog_manager.start(StartSG.start)

async def on_export_users(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
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

            await callback.message.answer_document(
                file,
                caption=f'Актуальный на <b>{datetime.now().strftime("%d-%m-%Y")}</b>',
                parse_mode='HTML'
            )
        else:
            await callback.message.answer("Нет данных для экспорта.")
    except Exception as e:
        await callback.message.answer(f"Ошибка при экспорте данных: {str(e)}")

    await dialog_manager.start(StartSG.start)

async def on_success_announcement_title(message: Message, widget: TextInput, dialog_manager: DialogManager, title: str):
    dialog_manager.current_context().dialog_data['announcement_title'] = title
    await dialog_manager.switch_to(NewAnnouncementSG.waiting_for_content)

async def on_success_announcement_content(message: Message, widget: TextInput, dialog_manager: DialogManager, content: str):
    dialog_manager.current_context().dialog_data['announcement_content'] = content
    await dialog_manager.switch_to(NewAnnouncementSG.waiting_for_photo_count)

async def on_success_photo_count(message: Message, widget: TextInput, dialog_manager: DialogManager, count: str):
    try:
        count = int(count)
        if count < 0 or count > 4:
            raise ValueError("Invalid number of photos")
        dialog_manager.current_context().dialog_data['photo_count'] = count
        dialog_manager.current_context().dialog_data['photos'] = []
        if count > 0:
            await dialog_manager.switch_to(NewAnnouncementSG.waiting_for_photo)
        else:
            await dialog_manager.switch_to(NewAnnouncementSG.waiting_for_button_count)
    except ValueError:
        await message.answer("Введите корректное число от 0 до 4.")

async def on_success_button_count(message: Message, widget: TextInput, dialog_manager: DialogManager, count: str):
    try:
        count = int(count)
        if count < 1 or count > 3:
            raise ValueError("Invalid number of buttons")
        dialog_manager.current_context().dialog_data['button_count'] = count
        dialog_manager.current_context().dialog_data['buttons'] = []
        await dialog_manager.switch_to(NewAnnouncementSG.waiting_for_button_text)
    except ValueError:
        await message.answer("Введите корректное число от 1 до 3.")

async def on_success_photo(message: Message, widget: TextInput, dialog_manager: DialogManager, photo: str):
    photos = dialog_manager.current_context().dialog_data.get('photos', [])
    photos.append(photo)
    dialog_manager.current_context().dialog_data['photos'] = photos
    if len(photos) < dialog_manager.current_context().dialog_data['photo_count']:
        await message.answer("Отправьте еще одну ссылку на фото или нажмите 'Пропустить'.")
    else:
        await dialog_manager.switch_to(NewAnnouncementSG.waiting_for_button_count)
async def on_skip_photo(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    photos = dialog_manager.current_context().dialog_data.get('photos', [])
    photos.append(None)
    dialog_manager.current_context().dialog_data['photos'] = photos
    if len(photos) < dialog_manager.current_context().dialog_data['photo_count']:
        await callback.message.answer("Пропущено. Отправьте следующую ссылку на фото или нажмите 'Пропустить'.")
    else:
        await dialog_manager.switch_to(NewAnnouncementSG.waiting_for_button_count)
    await callback.answer()
async def on_success_button_text(message: Message, widget: TextInput, dialog_manager: DialogManager, button_text: str):
    buttons = dialog_manager.current_context().dialog_data.get('buttons', [])
    buttons.append({'text': button_text, 'url': None})
    dialog_manager.current_context().dialog_data['buttons'] = buttons
    await dialog_manager.switch_to(NewAnnouncementSG.waiting_for_button_url)

async def on_success_button_url(message: Message, widget: TextInput, dialog_manager: DialogManager, button_url: str):
    buttons = dialog_manager.current_context().dialog_data['buttons']
    buttons[-1]['url'] = button_url
    if len(buttons) < dialog_manager.current_context().dialog_data['button_count']:
        await dialog_manager.switch_to(NewAnnouncementSG.waiting_for_button_text)
    else:
        await dialog_manager.switch_to(NewAnnouncementSG.confirming_announcement)

async def on_skip_button(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    buttons = dialog_manager.current_context().dialog_data.get('buttons', [])
    buttons.append({'text': None, 'url': None})
    dialog_manager.current_context().dialog_data['buttons'] = buttons
    if len(buttons) < dialog_manager.current_context().dialog_data['button_count']:
        await callback.message.answer("Пропущено. Отправьте следующий текст кнопки или нажмите 'Пропустить'.")
    else:
        await dialog_manager.switch_to(NewAnnouncementSG.confirming_announcement)
    await callback.answer()

async def on_confirm_announcement(callback_query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.current_context().dialog_data
    title = data['announcement_title']
    content = data['announcement_content']
    photos = [photo for photo in data.get('photos', []) if photo is not None]
    buttons = [btn for btn in data.get('buttons', []) if btn['text'] is not None and btn['url'] is not None]

    announcement_text = f"<b>{title}</b>\n\n{content}"
    post_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn['text'], url=btn['url']) for btn in buttons]
    ])

    try:
        if photos:
            media = [InputMediaPhoto(media=photo) for photo in photos]
            media[0].caption = announcement_text
            media[0].parse_mode = "HTML"
            await bot.send_media_group(chat_id=CHANNEL_ID, media=media)
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=announcement_text, parse_mode="HTML", reply_markup=post_buttons)
        await callback_query.message.answer("Объявление успешно опубликовано!")
    except Exception as e:
        logging.error(f"Ошибка публикации объявления: {e}")
        await callback_query.message.answer(f"Произошла ошибка при публикации: {e}")

    await dialog_manager.done()


async def get_recent_announcements(dialog_manager: DialogManager, **kwargs):
    await db.ensure_connection()
    query = """
    SELECT property_id, name, location, distance_to_sea, property_type, monthly_price, daily_price, 
           booking_deposit_fixed, security_deposit, bedrooms, bathrooms, pool, kitchen, cleaning, utility_bill, description,
           photo1, photo2, photo3, photo4
    FROM properties
    ORDER BY created_at DESC
    LIMIT 10
    """
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            properties = await cursor.fetchall()
    dialog_manager.current_context().dialog_data['properties'] = properties
    return {"properties": properties}



async def on_property_selected_for_schedule(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    current_data = dialog_manager.current_context().dialog_data
    properties = current_data.get("properties", [])
    selected_property = next((item for item in properties if str(item[0]) == item_id), None)

    if selected_property:
        dialog_manager.current_context().dialog_data['selected_property_id'] = selected_property[0]
        dialog_manager.current_context().dialog_data['selected_property_name'] = selected_property[1]
        dialog_manager.current_context().dialog_data['selected_property_details'] = {
            "name": selected_property[1],
            "location": selected_property[2],
            "distance_to_sea": selected_property[3],
            "property_type": selected_property[4],
            "monthly_price": selected_property[5],
            "daily_price": selected_property[6],
            "booking_deposit_fixed": selected_property[7],
            "security_deposit": selected_property[8],
            "bedrooms": selected_property[9],
            "bathrooms": selected_property[10],
            "pool": selected_property[11],
            "kitchen": selected_property[12],
            "cleaning": selected_property[13],
            "utility_bill": selected_property[14],
            "description": selected_property[15],
            "photos": [selected_property[16], selected_property[17], selected_property[18], selected_property[19]]
        }
        await dialog_manager.switch_to(ScheduleAnnouncementSG.waiting_for_schedule_time)
    else:
        await callback.message.answer("Ошибка: выбранный объект недвижимости не найден.")


async def on_schedule_time_received(message: Message, widget: TextInput, dialog_manager: DialogManager, schedule_time: str):
    try:
        schedule_time = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
        if schedule_time < datetime.now():
            raise ValueError("Scheduled time is in the past.")
        dialog_manager.current_context().dialog_data['schedule_time'] = schedule_time
        await dialog_manager.switch_to(ScheduleAnnouncementSG.confirming_scheduled_announcement)
    except ValueError:
        await message.answer("Введите корректную дату и время в формате YYYY-MM-DD HH:MM.")

async def create_post_with_last_property(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(ScheduleAnnouncementSG.waiting_for_announcement_selection)


async def on_confirm_scheduled_announcement(callback_query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.current_context().dialog_data
    property = data['selected_property_details']
    schedule_time = data['schedule_time']

    text = (
        f"🏠 <b>{property['name']}</b>\n\n"
        f"📍 <b>Расположение:</b> {property['location']}\n"
        f"🌊 <b>Удаленность от моря:</б> {property['distance_to_sea']}\n"
        f"🏷️ <b>Категория:</б> {property['property_type']}\n\n"
        f"💰 <b>Стоимость в месяц:</b> {property['monthly_price']}฿\n"
        f"💰 <b>Стоимость постуточно:</б> {property['daily_price']}฿\n"
        f"💵 <b>Залог:</б> {property['booking_deposit_fixed']}฿\n"
        f"🔒 <b>Сохраненный депозит:</б> {property['security_deposit']}฿\n\n"
        f"🛏️ <b>Количество спален:</б> {property['bedrooms']}\n"
        f"🛁 <b>Количество ванных:</б> {property['bathrooms']}\n"
        f"🏊 <b>Бассейн:</б> {'Да' if property['pool'] else 'Нет'}\n"
        f"🍴 <b>Кухня:</б> {'Да' if property['kitchen'] else 'Нет'}\n"
        f"🧹 <b>Уборка:</б> {'Да' if property['cleaning'] else 'Нет'}\n"
        f"💡 <b>Утилиты:</б> {property['utility_bill']}\n\n"
        f"📜 <b>Описание:</б> {property['description']}\n"
    ).replace("</б>", "</b>")

    async def schedule_post():
        try:
            await asyncio.sleep((schedule_time - datetime.now()).total_seconds())

            # Prepare media group
            media = []
            for idx, photo in enumerate(property['photos']):
                if photo:
                    if idx == 0:
                        media.append(InputMediaPhoto(media=photo, caption=text, parse_mode="HTML"))
                    else:
                        media.append(InputMediaPhoto(media=photo))

            # Send media group if there are photos
            if media:
                await bot.send_media_group(chat_id=CHANNEL_ID, media=media)
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML")

            await bot.send_message(callback_query.from_user.id, "Объявление успешно опубликовано!")
        except Exception as e:
            logging.error(f"Ошибка публикации объявления: {e}")
            await bot.send_message(callback_query.from_user.id, f"Произошла ошибка при публикации: {e}")

    asyncio.create_task(schedule_post())
    await callback_query.message.answer(f"Публикация объявления запланирована на {schedule_time.strftime('%Y-%m-%d %H:%M')}.")
    await dialog_manager.done()



async def on_create_announcement(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(NewAnnouncementSG.waiting_for_title)

async def on_success_photo(message: Message, widget: TextInput, dialog_manager: DialogManager, photo: str):
    photos = dialog_manager.current_context().dialog_data.get('photos', [])
    photos.append(photo)
    dialog_manager.current_context().dialog_data['photos'] = photos
    if len(photos) < 4:
        await message.answer("Отправьте еще одну ссылку на фото или нажмите 'Пропустить'.")
        await dialog_manager.next()
    else:
        await dialog_manager.next()

async def on_skip_photo(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.next()
    await callback.message.answer("Пропущено. Продолжаем...")


start_dialog = Dialog(
    Window(
        Const('Это панель администратора'),
        Button(
            text=Const('📋 Создать карточку'),
            id='button_1',
            on_click=on_create_property),
        Button(
            text=Const('🗑️ Удалить карточку'),
            id='button_2',
            on_click=on_delete_property),
        Button(
            text=Const('✏️ Редактировать карточку'),
            id='button_3',
            on_click=on_edit_property),
        Button(
            text=Const('📜 Просмотреть все карточки'),
            id='button_4',
            on_click=on_view_properties),
        Button(
            text=Const('📊 Аналитика'),
            id='button_5',
            on_click=on_view_analytics),
        Button(
            text=Const('📄 Экспорт данных'),
            id='button_7',
            on_click=on_export_data),
        Button(
            text=Const('📢 Создать объявление'),
            id='button_8',
            on_click=on_create_announcement),
        Button(
            text=Const('🕒 Запланировать публикацию'),
            id='button_9',
            on_click=create_post_with_last_property),
        state=StartSG.start,
    ),
)


schedule_announcement_dialog = Dialog(
    Window(
        Const("Выберите одно из последних 10 объявлений для публикации:"),
        Column(
            Select(
                Format("{item[1]}"),  # Assuming item is a tuple (property_id, name)
                id="property_select_schedule",
                items="properties",  # The key for the getter function
                item_id_getter=lambda x: x[0],  # Get the property_id
                on_click=on_property_selected_for_schedule
            )
        ),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)
        ),
        state=ScheduleAnnouncementSG.waiting_for_announcement_selection,
        getter=get_recent_announcements  # Ensure this getter is properly referenced
    ),
    Window(
        Const("Введите дату и время для публикации в формате YYYY-MM-DD HH:MM:"),
        TextInput(id="schedule_time_input", on_success=on_schedule_time_received),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)
        ),
        state=ScheduleAnnouncementSG.waiting_for_schedule_time
    ),
    Window(
        Format("Публикация объявления '{dialog_data[selected_property_name]}' запланирована на {dialog_data[schedule_time]}.\n\n"
               "Подтвердите действие:"),
        Row(
            Button(Const("✅ Подтвердить"), id="confirm_schedule", on_click=on_confirm_scheduled_announcement),
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)
        ),
        state=ScheduleAnnouncementSG.confirming_scheduled_announcement
    )
)

view_properties_dialog = Dialog(
    Window(
        Const("Выберите действие:"),
        Button(Const("Просмотр всех объектов"), id="view_all_properties", on_click=on_view_properties),
        state=ViewPropertiesSG.view_properties
    ),
    Window(
        Format("{properties_list}"),
        Row(
            Button(Const('⬅️ Назад'), id='previous_page', on_click=on_previous_page),
            Button(Const('➡️ Вперед'), id='next_page', on_click=on_next_page),
        ),
        Button(Const('🔙 Назад'), id='back_to_menu', on_click=on_back_to_menu),
        getter=view_properties_page_getter,
        state=ViewPropertiesSG.view_properties_page,
    ),
)


view_analytics_dialog = Dialog(
    Window(
        Format("{analytics_data}"),
        Button(Const('🔙 Назад'), id='back_to_menu', on_click=on_back_to_menu),
        getter=show_analytics,
        state=ViewAnalyticsSG.view_analytics,
        parse_mode="HTML"
    ),
)

export_data_dialog = Dialog(
    Window(
        Const("Выберите данные для экспорта:"),
        Row(
            Button(Const('📄 Экспорт карточек'), id='export_properties', on_click=on_export_properties),
            Button(Const('📄 Экспорт пользователей'), id='export_users', on_click=on_export_users)
        ),
        Button(Const('🔙 Вернуться в меню'), id='back_to_menu', on_click=on_back_to_menu),
        state=ExportDataSG.export_menu
    )
)

property_creation_dialog = Dialog(
    Window(
        Const("Введите название объекта:"),
        TextInput(id="property_name", on_success=on_success_property_name),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_name
    ),
    Window(
        Const("Отправьте ссылку на фото объекта 1:"),
        TextInput(id="property_photo1", on_success=on_success_property_photo1),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩Пропустить"), id="skip", on_click=lambda c, b, d: on_skip_photo(c, d, 'photo1')),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_photo1
    ),
    Window(
        Const("Отправьте ссылку на фото объекта 2:"),
        TextInput(id="property_photo2", on_success=on_success_property_photo2),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩Пропустить"), id="skip", on_click=lambda c, b, d: on_skip_photo(c, d, 'photo2')),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_photo2
    ),
    Window(
        Const("Отправьте ссылку на фото объекта 3:"),
        TextInput(id="property_photo3", on_success=on_success_property_photo3),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩Пропустить"), id="skip", on_click=lambda c, b, d: on_skip_photo(c, d, 'photo3')),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_photo3
    ),
    Window(
        Const("Отправьте ссылку на фото объекта 4:"),
        TextInput(id="property_photo4", on_success=on_success_property_photo4),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩Пропустить"), id="skip", on_click=lambda c, b, d: on_skip_photo(c, d, 'photo4')),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_photo4
    ),
    Window(
        Const("Отправьте ссылку на фото объекта 5:"),
        TextInput(id="property_photo5", on_success=on_success_property_photo5),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩Пропустить"), id="skip", on_click=lambda c, b, d: on_skip_photo(c, d, 'photo5')),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_photo5
    ),
    Window(
        Const("Отправьте ссылку на фото объекта 6:"),
        TextInput(id="property_photo6", on_success=on_success_property_photo6),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩Пропустить"), id="skip", on_click=lambda c, b, d: on_skip_photo(c, d, 'photo6')),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_photo6
    ),
    Window(
        Const("Отправьте ссылку на фото объекта 7:"),
        TextInput(id="property_photo7", on_success=on_success_property_photo7),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩Пропустить"), id="skip", on_click=lambda c, b, d: on_skip_photo(c, d, 'photo7')),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_photo7
    ),
    Window(
        Const("Отправьте ссылку на фото объекта 8:"),
        TextInput(id="property_photo8", on_success=on_success_property_photo8),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩Пропустить"), id="skip", on_click=lambda c, b, d: on_skip_photo(c, d, 'photo8')),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_photo8
    ),
    Window(
        Const("Отправьте ссылку на фото объекта 9:"),
        TextInput(id="property_photo9", on_success=on_success_property_photo9),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩Пропустить"), id="skip", on_click=lambda c, b, d: on_skip_photo(c, d, 'photo9')),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_photo9
    ),
    Window(
        Const("Введите расположение объекта:"),
        TextInput(id="property_location", on_success=on_success_property_location),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_location
    ),
    Window(
        Const("Введите удаленность от моря (в метрах):"),
        TextInput(id="property_distance_to_sea", on_success=on_success_property_distance_to_sea),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_distance_to_sea
    ),
    Window(
        Const("Выберите тип недвижимости:"),
        Column(
            Select(
                Format("{item}"),
                id="property_type_select",
                items=["Вилла", "Кондо", "Апартаменты", "Дом в резорте", "Студия в резорте", "Комната"],
                item_id_getter=lambda x: x,
                on_click=on_success_property_type
            )
        ),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_property_type

),
    Window(
        Const("Введите ежемесячную стоимость:"),
        TextInput(id="property_monthly_price", on_success=on_success_property_monthly_price),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_monthly_price
    ),
    Window(
        Const("Введите ежедневную стоимость:"),
        TextInput(id="property_daily_price", on_success=on_success_property_daily_price),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_daily_price
    ),
    Window(
        Const("Введите минимальное количество ночей:"),
        TextInput(id="property_minimum_nights", on_success=on_success_property_minimum_nights),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_minimum_nights
    ),
    Window(
        Const("Введите фиксированный депозит:"),
        TextInput(id="property_booking_deposit_fixed", on_success=on_success_property_booking_deposit_fixed),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_booking_deposit_fixed
    ),
    Window(
        Const("Введите процентный депозит:"),
        TextInput(id="property_booking_deposit_percentage", on_success=on_success_property_booking_deposit_percentage),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_booking_deposit_percentage
    ),
    Window(
        Const("Введите депозит безопасности:"),
        TextInput(id="property_security_deposit", on_success=on_success_property_security_deposit),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_security_deposit
    ),
    Window(
        Const("Введите количество спален:"),
        TextInput(id="property_bedrooms", on_success=on_success_property_bedrooms),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_bedrooms
    ),
    Window(
        Const("Введите количество кроватей:"),
        TextInput(id="property_beds", on_success=on_success_property_beds),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_beds
    ),
    Window(
        Const("Введите количество ванных комнат:"),
        TextInput(id="property_bathrooms", on_success=on_success_property_bathrooms),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_bathrooms
    ),
    Window(
        Const("Есть ли бассейн?"),
        Select(
            Format("{item}"),
            id="property_pool_select",
            items=["Да", "Нет"],
            item_id_getter=lambda x: x,
            on_click=on_success_property_pool
        ),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_pool
    ),
    Window(
        Const("Есть ли кухня?"),
        Select(
            Format("{item}"),
            id="property_kitchen_select",
            items=["Да", "Нет"],
            item_id_getter=lambda x: x,
            on_click=on_success_property_kitchen
        ),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_kitchen
    ),
    Window(
        Const("Есть ли кондиционеры?"),
        Select(
            Format("{item}"),
            id="property_air_conditioners_select",
            items=["Да", "Нет"],
            item_id_getter=lambda x: x,
            on_click=on_success_property_air_conditioners
        ),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_air_conditioners
    ),
    Window(
        Const("Есть ли уборка?"),
        Select(
            Format("{item}"),
            id="property_cleaning_select",
            items=["Да", "Нет"],
            item_id_getter=lambda x: x,
            on_click=on_success_property_cleaning
        ),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_cleaning
    ),
    Window(
        Const("Введите описание объекта:"),
        TextInput(id="property_description", on_success=on_success_property_description),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_description
    ),
    Window(
        Const("Есть ли коммунальные платежи?"),
        Select(
            Format("{item}"),
            id="property_utility_bill_select",
            items=["Да", "Нет"],
            item_id_getter=lambda x: x,
            on_click=on_success_property_utility_bill
        ),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back),
        ),
        state=NewPropertySG.waiting_for_utility_bill
    ),
    Window(
        Const("Пожалуйста, подтвердите данные объекта недвижимости:"),
        Format("Название: {dialog_data[name]}\n"
               "Фото 1: {dialog_data[photo1]}\n"
               "Фото 2: {dialog_data[photo2]}\n"
               "Фото 3: {dialog_data[photo3]}\n"
               "Фото 4: {dialog_data[photo4]}\n"
               "Фото 5: {dialog_data[photo5]}\n"
               "Фото 6: {dialog_data[photo6]}\n"
               "Фото 7: {dialog_data[photo7]}\n"
               "Фото 8: {dialog_data[photo8]}\n"
               "Фото 9: {dialog_data[photo9]}\n"
               "Расположение: {dialog_data[location]}\n"
               "Удаленность от моря: {dialog_data[distance_to_sea]}\n"
               "Тип недвижимости: {dialog_data[property_type]}\n"
               "Ежемесячная стоимость: {dialog_data[monthly_price]}\n"
               "Ежедневная стоимость: {dialog_data[daily_price]}\n"
               "Минимальное количество ночей: {dialog_data[minimum_nights]}\n"
               "Фиксированный депозит: {dialog_data[booking_deposit_fixed]}\n"
               "Процентный депозит: {dialog_data[booking_deposit_percentage]}\n"
               "Депозит безопасности: {dialog_data[security_deposit]}\n"
               "Количество спален: {dialog_data[bedrooms]}\n"
               "Количество кроватей: {dialog_data[beds]}\n"
               "Количество ванных комнат: {dialog_data[bathrooms]}\n"
               "Бассейн: {dialog_data[pool]}\n"
               "Кухня: {dialog_data[kitchen]}\n"
               "Кондиционеры: {dialog_data[air_conditioners]}\n"
               "Уборка: {dialog_data[cleaning]}\n"
               "Описание: {dialog_data[description]}\n"
               "Коммунальные платежи: {dialog_data[utility_bill]}\n"),
        Row(
            Button(Const("✅Подтвердить"), id="confirm", on_click=on_confirm_data),
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
        ),
        state=NewPropertySG.confirming_data,
    )
)
delete_property_dialog = Dialog(
    Window(
        Const("Выберите карточку недвижимости для удаления:"),
        Column(
            Select(
                Format("{item[1]}"),  # Assuming item is a tuple (property_id, property_name)
                id="property_select",
                items="properties",  # The key for the getter function
                item_id_getter=lambda x: x[0],  # Get the property_id
                on_click=on_property_selected
            )
        ),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)
        ),
        state=DeletePropertySG.waiting_for_property_selection,
        getter=view_all_properties  # Make sure this getter is properly referenced
    ),
    Window(
        Format("Вы уверены, что хотите удалить карточку недвижимости с названием: {dialog_data[selected_property_name]}?"),
        Row(
            Button(Const("✅ Да"), id="confirm", on_click=on_confirm_deletion),
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("◀️ Назад"), id="back", on_click=go_back)
        ),
        state=DeletePropertySG.confirming_deletion
    )
)

async def on_confirm_edit(callback_query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.current_context().dialog_data
    property_id = data['selected_property_id']
    selected_field = data['selected_field']
    new_value = data['new_value']

    await db.ensure_connection()
    query = f"UPDATE properties SET {selected_field} = %s WHERE property_id = %s"
    params = (new_value, property_id)
    try:
        async with db.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
        await callback_query.message.answer(f"Поле {selected_field} успешно обновлено!")
    except Exception as e:
        logging.error(f"Ошибка выполнения запроса: {e}")
        await callback_query.message.answer(f"Произошла ошибка при обновлении: {e}")
    await dialog_manager.done()

async def on_cancel_edit(callback_query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback_query.message.answer("Редактирование отменено.")
    await dialog_manager.done()


edit_property_dialog = Dialog(
    Window(
        Const("Выберите карточку недвижимости для редактирования:"),
        Column(
            Select(
                Format("{item[1]}"),
                id="property_select",
                items="properties",
                item_id_getter=lambda x: x[0],
                on_click=on_property_selected
            )
        ),
        Row(Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)),
        state=EditPropertySG.waiting_for_property_selection,
        getter=view_all_properties
    ),
    Window(
        Const("Выберите поле для редактирования:"),
        Row(
            Button(Const("Название"), id="edit_name", on_click=on_edit_field_selected),
            Button(Const("Фото 1"), id="edit_photo1", on_click=on_edit_field_selected),
            Button(Const("Фото 2"), id="edit_photo2", on_click=on_edit_field_selected),
            Button(Const("Фото 3"), id="edit_photo3", on_click=on_edit_field_selected),
        ),
        Row(
            Button(Const("Расположение"), id="edit_location", on_click=on_edit_field_selected),
            Button(Const("Удаленность от моря"), id="edit_distance_to_sea", on_click=on_edit_field_selected),
            Button(Const("Тип недвижимости"), id="edit_property_type", on_click=on_edit_field_selected),
            Button(Const("Ежемесячная стоимость"), id="edit_monthly_price", on_click=on_edit_field_selected),
        ),
        Row(
            Button(Const("Ежедневная стоимость"), id="edit_daily_price", on_click=on_edit_field_selected),
            Button(Const("Минимальное количество ночей"), id="edit_minimum_nights", on_click=on_edit_field_selected),
            Button(Const("Фиксированный депозит"), id="edit_booking_deposit_fixed", on_click=on_edit_field_selected),
            Button(Const("Процентный депозит"), id="edit_booking_deposit_percentage", on_click=on_edit_field_selected),
        ),
        Row(
            Button(Const("Депозит безопасности"), id="edit_security_deposit", on_click=on_edit_field_selected),
            Button(Const("Количество спален"), id="edit_bedrooms", on_click=on_edit_field_selected),
            Button(Const("Количество кроватей"), id="edit_beds", on_click=on_edit_field_selected),
            Button(Const("Количество ванных комнат"), id="edit_bathrooms", on_click=on_edit_field_selected),
        ),
        Row(
            Button(Const("Бассейн"), id="edit_pool", on_click=on_edit_field_selected),
            Button(Const("Кухня"), id="edit_kitchen", on_click=on_edit_field_selected),
            Button(Const("Кондиционеры"), id="edit_air_conditioners", on_click=on_edit_field_selected),
            Button(Const("Уборка"), id="edit_cleaning", on_click=on_edit_field_selected),
        ),
        Row(
            Button(Const("Описание"), id="edit_description", on_click=on_edit_field_selected),
            Button(Const("Коммунальные платежи"), id="edit_utility_bill", on_click=on_edit_field_selected),
        ),
        Row(Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)),
        state=EditPropertySG.waiting_for_edit_field,
    ),
    Window(
        Const("Введите новое значение и подтвердите:"),
        TextInput(id="edit_value_input", on_success=on_new_value_received),
        Row(
            Button(Const("✅ Подтвердить"), id="confirm_edit", on_click=on_confirm_edit),
            Button(Const("❌ Отмена"), id="cancel_edit", on_click=on_cancel_edit)
        ),
        state=EditPropertySG.waiting_for_edit_value,
    )
)

announcement_creation_dialog = Dialog(
    Window(
        Const("Введите заголовок объявления:"),
        TextInput(id="announcement_title", on_success=on_success_announcement_title),
        Row(Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)),
        state=NewAnnouncementSG.waiting_for_title
    ),
    Window(
        Const("Введите содержимое объявления:"),
        TextInput(id="announcement_content", on_success=on_success_announcement_content),
        Row(Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)),
        state=NewAnnouncementSG.waiting_for_content
    ),
    Window(
        Const("Сколько фото вы хотите добавить? (0-4):"),
        TextInput(id="photo_count", on_success=on_success_photo_count),
        Row(Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)),
        state=NewAnnouncementSG.waiting_for_photo_count
    ),
    Window(
        Const("Отправьте ссылку на фото или нажмите 'Пропустить':"),
        TextInput(id="announcement_photo", on_success=on_success_photo),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩ Пропустить"), id="skip_photo", on_click=on_skip_photo)
        ),
        state=NewAnnouncementSG.waiting_for_photo
    ),
    Window(
        Const("Сколько кнопок вы хотите добавить? (1-3):"),
        TextInput(id="button_count", on_success=on_success_button_count),
        Row(Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)),
        state=NewAnnouncementSG.waiting_for_button_count
    ),
    Window(
        Const("Введите текст кнопки или нажмите 'Пропустить':"),
        TextInput(id="button_text", on_success=on_success_button_text),
        Row(
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action),
            Button(Const("⏩ Пропустить"), id="skip_button", on_click=on_skip_button)
        ),
        state=NewAnnouncementSG.waiting_for_button_text
    ),
    Window(
        Const("Введите URL кнопки:"),
        TextInput(id="button_url", on_success=on_success_button_url),
        Row(Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)),
        state=NewAnnouncementSG.waiting_for_button_url
    ),
    Window(
        Const("Пожалуйста, подтвердите объявление:"),
        Format("Заголовок: {dialog_data[announcement_title]}\n"
               "Содержание: {dialog_data[announcement_content]}\n"
               "Фото: {dialog_data[photos]}\n"
               "Кнопки: {dialog_data[buttons]}\n"),
        Row(
            Button(Const("✅ Подтвердить"), id="confirm", on_click=on_confirm_announcement),
            Button(Const("❌ Отмена"), id="cancel", on_click=cancel_action)
        ),
        state=NewAnnouncementSG.confirming_announcement
    )
)









storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)
setup_dialogs(dp)

dp.include_router(start_dialog)
dp.include_router(view_properties_dialog)
dp.include_router(view_analytics_dialog)
dp.include_router(export_data_dialog)
dp.include_router(property_creation_dialog)
dp.include_router(delete_property_dialog)
dp.include_router(edit_property_dialog)
dp.include_router(announcement_creation_dialog)
dp.include_router(schedule_announcement_dialog)

# Роутинг для планирования публикации
dp.callback_query(create_post_with_last_property, lambda c: c.data == "button_9", state=StartSG.start)


# Роутинг для нового объявления
dp.callback_query(on_create_announcement, lambda c: c.data == "button_8", state=StartSG.start)


dp.callback_query(on_confirm_edit, lambda c: c.data == "confirm_edit", state=EditPropertySG.confirm_edit)
dp.callback_query(on_cancel_edit, lambda c: c.data == "cancel_edit", state=EditPropertySG.confirm_edit)

@dp.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=True)
