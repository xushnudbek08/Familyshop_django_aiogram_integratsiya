# bot/routers/register.py
from aiogram import Router, types
from aiogram.types import Message
from buttons import qantaqt

router = Router()

@router.message(commands=['start'])
async def start_handler(message: Message):
    fulname = message.from_user.full_name
    await message.answer(f"Salom, {fulname}! Botga xush kelibsiz!")
    await message.answer("Telefon raqamingizni yuboring, iltimos:", reply_markup=qantaqt)
    
