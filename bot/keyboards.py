from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from aiogram.utils.keyboard import InlineKeyboardBuilder
# Kontakt yuborish tugmasi
qantaqt = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Kantaqtingizni yuboring", request_contact=True)]
    ],
    resize_keyboard=True
)

lokatsiya = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)




menyu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 mahsulotlar")],
        [KeyboardButton(text="📖 Mening buyurtmalarim")],
        [KeyboardButton(text="📞 Aloqa"), KeyboardButton(text="🛒 savat")],
        [KeyboardButton(text="🗑 savatni tozalsh")]
    ],
    resize_keyboard=True
)


@sync_to_async
def get_categories():
    return list(Category.objects.all())
from api.models import Category
from asgiref.sync import sync_to_async

@sync_to_async
def get_categories():
    return list(Category.objects.all())


rasmiylashtirish = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Rasmiylashtirish",)],
        [KeyboardButton(text="🔙 Orqaga",)]
    ],
    resize_keyboard=True
)