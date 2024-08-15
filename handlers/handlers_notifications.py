from aiogram import Router, F
from aiogram.types import CallbackQuery

import app.keyboards as kb
from config import db_config
from database.database import Database

router = Router()
db = Database(db_config)


@router.callback_query(F.data == "notifications")
async def manage_notifications(callback: CallbackQuery):
    await db.update_last_activity(callback.message.from_user.id)
    response_text = "Выберите, пункт меню:"
    await callback.message.answer(response_text, reply_markup=kb.notification_keyboard)


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
