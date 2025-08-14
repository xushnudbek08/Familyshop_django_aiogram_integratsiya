from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from bot.states import RegisterState
from aiogram.enums import ParseMode 
from bot.keyboards import qantaqt,lokatsiya,menyu
from api.models import TelegramUser
from aiogram import F
register = Router()

# /start komandasi
@register.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    fulname = message.from_user.full_name or "Foydalanuvchi"
    user_exists = await sync_to_async(
        TelegramUser.objects.filter(telegram_id=message.from_user.id).exists
    )()
    if user_exists:
        await message.answer("✅ Siz allaqachon ro'yxatdan o'tgansiz.",reply_markup=menyu)
    else:
        
        await message.answer(f"👋 Assalomu Aleykum {fulname}!\nSiz bizning Botda Tavarlarni arzon narxlarda sotib olishingiz mumkin\nSotib olgan tvarngiz uyingizga olib borib beriladi.")
        await message.answer("📱 Iltimos, telefon raqamingizni tugma orqali yuboring:", reply_markup=qantaqt)
        await state.set_state(RegisterState.waiting_for_phone)


# Telefon raqamni qabul qilish
  # Lokatsiya tugmasi kerak

@register.message(RegisterState.waiting_for_phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    contact = message.contact
    await state.update_data(phone=contact.phone_number)

    await message.answer(
        "🏠 Endi manzilingizni yuboring:\n\n"
        "❗ Iltimos, '📍 Lokatsiyani yuborish' tugmasidan foydalaning.",
        reply_markup=lokatsiya
    )
    await state.set_state(RegisterState.waiting_for_address)


# Manzilni qabul qilish
@register.message(RegisterState.waiting_for_address)
async def get_address(message: Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get("phone")
    location = message.location
    

    await sync_to_async(TelegramUser.objects.create)(
        telegram_id=message.chat.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        phone=phone,
        latitude=location.latitude,
        longitude=location.longitude
    )

    await message.answer("✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!", reply_markup=menyu)

    await state.clear()


# Telefon raqamini noto‘g‘ri formatda yuborganlar uchun
@register.message(RegisterState.waiting_for_phone)
async def wrong_format(message: Message):
    await message.answer("❗ Iltimos, telefon raqamingizni **tugma orqali** yuboring.")


@register.message(F.text == "📞 Aloqa")
async def send_contact_info(message:Message):
    contact_text = (
        "📞 <b>Biz bilan bog'lanish uchun:</b>\n\n"
        "📱 <b>Aloqa uchun telefon raqam:</b> \n"
        "<code>+998888551166</code>\n\n"
        "👤 <b>Admin:</b> @sanjarbek455\n\n"
        "Istalgan vaqtda murojaat qilishingiz mumkin!"
    )
    
    await message.answer_photo(photo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS3A7kIZRy_HhxvxhKKH6how4vstY7ZdIMdVg&s",caption=contact_text, parse_mode=ParseMode.HTML)

# Telefon raqamini yubormaganlar uchun
