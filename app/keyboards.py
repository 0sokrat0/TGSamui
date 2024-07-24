from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🏠 Поиск недвижимости", callback_data="search_property")
    ],
    [
        InlineKeyboardButton(text="📌 Избранное", callback_data="favorites"),
        InlineKeyboardButton(text="🌟 Лучшие объекты", callback_data="best_properties")
    ],
    [
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")
    ],
    [
        InlineKeyboardButton(text="🏝️ Наш сайт", web_app=WebAppInfo(url='https://tropicalsamui.com/'))
    ]
])

numbers = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отправить контакт", callback_data="send_contact")]
])

notification_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🔊 Подписаться на уведомления", callback_data="subscribe_notifications"),
        InlineKeyboardButton(text="🔈 Отписаться от уведомлений", callback_data="unsubscribe_notifications")
    ],
    [
        InlineKeyboardButton(text="🔚 Вернуться в главное меню", callback_data="back_to_main")
    ]
])

admin_main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🏠 Поиск недвижимости", callback_data="search_property")
    ],
    [
        InlineKeyboardButton(text="📌 Избранное", callback_data="favorites"),
        InlineKeyboardButton(text="🌟 Лучшие объекты", callback_data="best_properties")
    ],
    [
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")
    ],
    [
        InlineKeyboardButton(text="🏝️ Наш сайт", web_app=WebAppInfo(url='https://tropicalsamui.com/'))
    ]
])

numbers = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[  # Указываем список кнопок в конструкторе
        [KeyboardButton(text="Отправить контакт", request_contact=True)]
    ]
)

notification_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔊  Подписаться на уведомления", callback_data="subscribe_notifications"),
     InlineKeyboardButton(text="🔈 Отписаться от уведомлений", callback_data="unsubscribe_notifications")],
    [InlineKeyboardButton(text="🔚Вернуться в главное меню", callback_data="back_to_main")],
]
)
