from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🏠 Поиск недвижимости", callback_data="start_search")
    ],
    [
        InlineKeyboardButton(text="📌 Избранное", callback_data="favorites")

    ],
    [
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="📸 Блог о Самуи", callback_data="best_properties")
    ],
    [
        InlineKeyboardButton(text="🏝️ Наш сайт", web_app=WebAppInfo(url='https://tropicalsamui.com/'))
    ],
    [
        InlineKeyboardButton(text="📞 Связь с менеджером", url="https://t.me/tropicalsamui")
    ]
])

numbers = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отправить контакт", callback_data="send_contact")]
])





numbers = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[  # Указываем список кнопок в конструкторе
        [KeyboardButton(text="Отправить контакт", request_contact=True)]
    ]
)


