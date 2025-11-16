from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_phone_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Share Phone Number", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔻 Lose Weight"), KeyboardButton(text="🔺 Gain Weight")],
            [KeyboardButton(text="📦 My Orders")]
        ],
        resize_keyboard=True
    )
    return keyboard
