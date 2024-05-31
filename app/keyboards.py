from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

main = ReplyKeyboardMarkup(keyboard=
[
    [
        KeyboardButton(text="🏠 Поиск недвижимости")
    ],
    [
        KeyboardButton(text="📌 Избранное"),
        KeyboardButton(text="🌟 Лучшие объекты")
    ],
    [
        KeyboardButton(text="👤 Профиль"),
        KeyboardButton(text="🔔 Уведомления")
    ],
    [
        KeyboardButton(text="🏝️ Наш сайт", web_app=WebAppInfo(url='https://tropicalsamui.com/'))
    ]
],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите пункт меню.'
)


numbers = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[  # Указываем список кнопок в конструкторе
        [KeyboardButton(text="Отправить контакт", request_contact=True)]
    ]
)



notification_keyboard = InlineKeyboardMarkup( inline_keyboard=[
        [InlineKeyboardButton(text="🔊  Подписаться на уведомления", callback_data="subscribe_notifications"),
         InlineKeyboardButton(text="🔈 Отписаться от уведомлений", callback_data="unsubscribe_notifications")],
        [InlineKeyboardButton(text="🔚Вернуться в главное меню", callback_data="back_to_main")],
    ]
)

admin_main = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="🏠 Поиск недвижимости")
    ],
    [
        KeyboardButton(text="📌 Избранное"),
        KeyboardButton(text="🌟 Лучшие объекты")
    ],
    [
        KeyboardButton(text="👤 Профиль"),
        KeyboardButton(text="🔔 Уведомления")
    ],
    [
        KeyboardButton(text="🏝️ Наш сайт", web_app=WebAppInfo(url='https://tropicalsamui.com/'))
    ],
    [
        KeyboardButton(text="⚙️ Админ панель")
    ],
],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите пункт меню.'
)
