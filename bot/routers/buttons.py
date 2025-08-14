from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Kontakt yuborish tugmasi
qantaqt = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Kantaqtingizni yuboring", request_contact=True)]
    ],
    resize_keyboard=True
)

# Asosiy menyu
menyu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 mahsulotlar")],
        
        [KeyboardButton(text="📞 Aloqa"), KeyboardButton(text="🛒 savat")],
        [KeyboardButton(text="🗑 savatni tozalsh")]
    ],
    resize_keyboard=True
)


ortga = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Orqaga",)]
    ],
    resize_keyboard=True
)


rasmiylashtirish = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Rasmiylashtirish",)],
        [KeyboardButton(text="🔙 Orqaga",)]
    ],
    resize_keyboard=True
)