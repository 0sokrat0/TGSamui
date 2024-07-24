from aiogram_dialog import Dialog, Window

start_dialog = Dialog(
    Window(
        Group(
            Column(
                Button(
                    text=Const('🏠 Поиск недвижимости'),
                    id='button_1',
                    on_click=button_clicked),
                Button(
                    text=Const('🌟 Лучшие объекты!'),
                    id='button_2',
                    on_click=button_clicked),
            ),
            Row(
                Button(
                    text=Const('👤 Профиль'),
                    id='show_profile',
                    on_click=show_profile),
                Button(
                    text=Const('❤️ Избранное'),
                    id='show_favorites',
                    on_click=button_clicked),  # Измените на свою функцию обработки
            ),
            Url(
                Const("🏝️ Наш сайт"),
                Const('https://tropicalsamui.com/'),
            ),
        ),
        Multi(
            Format('<b>Приветствую, {name}!</b>'),
            Const(
                'Добро пожаловать в нашего Telegram-бота по поиску недвижимости на острове <u><b>Самуи</b></u>! 🌴🏠\n\n'),
            Const(
                '<b>Я могу помочь вам найти идеальное место для вашего отдыха или проживания на этом прекрасном острове.</b>\n\n'),
            sep='\n\n'
        ),
        state=StartSG.start,
        getter=get_start_data,
    ),
)
