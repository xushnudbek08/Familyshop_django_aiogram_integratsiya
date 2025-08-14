# bot/main.py
import os
import django
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext  
import asyncio
import os
import django
from aiogram import Bot, Dispatcher
from aiogram import Router
from bot.hendlers.register import register as user
from bot.hendlers.products import router as products_router
from bot.hendlers.paymet import router as payment_router
from bot.config import BOT_TOKEN, id

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin.settings")
django.setup()





dp = Dispatcher()

from aiogram.fsm.storage.redis import RedisStorage
storage = RedisStorage.from_url("redis://localhost:6379/0")
dp = Dispatcher(storage=storage)

dp.include_router(user),
dp.include_router(products_router),
dp.include_router(payment_router)
bot = Bot(token=BOT_TOKEN)




async def main():
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    await dp.start_polling(bot)