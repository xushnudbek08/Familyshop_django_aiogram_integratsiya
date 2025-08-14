# bot/handlers/checkout.py
from decimal import Decimal, ROUND_HALF_UP
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from api.models import TelegramUser, Cart, Order
from bot.states import CheckoutState
import os
router = Router()

KARTA = "4916990311023227"
KARTA_ISMI = "Sapayev Sanjar Uzum karta"

def q1(x: Decimal) -> Decimal:
    # so'mda kasr kerak emas => 1 ga kvantizatsiya
    return (x if isinstance(x, Decimal) else Decimal(str(x))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

def money(x: Decimal) -> str:
    return f"{int(q1(x)):,}".replace(",", " ")

@router.message(F.text == "✅ Rasmiylashtirish")
async def checkout_start(message: types.Message, state: FSMContext):
    user = await sync_to_async(TelegramUser.objects.filter(telegram_id=message.from_user.id).first)()
    if not user:
        await message.answer("❌ Siz ro‘yxatdan o‘tmagansiz.")
        return

    items = await sync_to_async(list)(
        Cart.objects.filter(user=user).select_related("product")
    )
    if not items:
        await message.answer("🛒 Savatingiz bo‘sh.")
        return

    # Har bir item bo'yicha to'g'ri hisob
    total_prepayment = Decimal("0")
    total_remaining = Decimal("0")
    total_price = Decimal("0")

    lines = []
    for it in items:
        # Product modelida DecimalField bo'lgani uchun Decimal bilan ishlaymiz
        prep = q1(it.product.prepayment_price * it.quantity)
        rem  = q1(it.product.remaining_price * it.quantity)
        tot  = q1(it.product.total_price * it.quantity)  # yoki prep+rem

        total_prepayment += prep
        total_remaining  += rem
        total_price      += tot

        lines.append(f"- {it.product.name} ({it.color or '-'}, {it.size or '-'}) x{it.quantity} → {money(tot)} so‘m")

    product_list_text = "\n".join(lines)

    # State ichida Decimal saqlamaymiz: faqat STR saqlaymiz
    await state.update_data(
        total_prepayment=str(total_prepayment),
        total_remaining=str(total_remaining),
        total_price=str(total_price),
        product_list=product_list_text
    )

    txt = (
        "🧾 Buyurtma yakuniy ma’lumotlari:\n"
        f"{product_list_text}\n\n"
        f"💰 Oldindan to‘lov: **{money(total_prepayment)} so‘m**\n"
        f"💰 Qolgan to‘lov (olganingizda): **{money(total_remaining)} so‘m**\n"
        f"💵 Umumiy: **{money(total_price)} so‘m**\n\n"
        f"📌 Iltimos, quyidagi kartaga **{money(total_prepayment)} so‘m** o‘tkazing va chekningizni (screenshot) yuboring.\n"
        f"💳 Karta: {KARTA}\n👤 Egasi: {KARTA_ISMI}"
    )
    await message.answer(txt, parse_mode="Markdown")
    await state.set_state(CheckoutState.waiting_for_screenshot)

@router.message(CheckoutState.waiting_for_screenshot, F.photo)
async def checkout_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    total_prepayment = q1(Decimal(data["total_prepayment"]))
    total_remaining  = q1(Decimal(data["total_remaining"]))
    total_price      = q1(Decimal(data["total_price"]))
    product_list_text = data["product_list"]

    user = await sync_to_async(
        TelegramUser.objects.filter(telegram_id=message.from_user.id).first
    )()
    if not user:
        await message.answer("❌ Profil topilmadi.")
        return

    # Faylni olish va saqlash
    photo = message.photo[-1]  # eng katta sifatli versiya
    file = await message.bot.get_file(photo.file_id)

    save_dir = "media/payments"
    os.makedirs(save_dir, exist_ok=True)  # Papka mavjud bo‘lmasa yaratadi

    relative_path = f"payments/{photo.file_unique_id}.jpg"  # DB uchun nisbiy path
    save_path = os.path.join("media", relative_path)        # fayl tizimi uchun to‘liq path

    await message.bot.download_file(file.file_path, save_path)

    # Buyurtmani yaratish
    order = Order(
        user=user,
        product_list=product_list_text,
        total_price=total_price,
        prepayment_amount=total_prepayment,
        remaining_amount=total_remaining,
        latitude=user.latitude,
        longitude=user.longitude,
        phone_number=user.phone,
        payment_screenshot=relative_path,  # ImageField uchun nisbiy yo‘l
        status="pending",
    )
    await sync_to_async(order.save)()

    # Savatni bo‘shatish
    await sync_to_async(Cart.objects.filter(user=user).delete)()

    await message.answer(
        "✅ To‘lov cheki qabul qilindi.\n"
        "⏳ Buyurtmangiz ko‘rib chiqilmoqda, iltimos 15 daqiqa kuting."
    )
    await state.clear()



@router.message(F.text == "📖 Mening buyurtmalarim")
async def get_orders_handler(message: types.Message):
    # Foydalanuvchiga tegishli buyurtmalarni olish
    orders = await sync_to_async(list)(
        Order.objects.filter(user__telegram_id=message.from_user.id)
        .order_by('-created_at')[:10]
    )

    if not orders:
        await message.answer("📭 Buyurtmalar mavjud emas")
        return

    def money_format(amount):
        return f"{int(amount):,}".replace(",", " ")

    for order in orders:
        text = (
            f"🆔 Buyurtma ID: {order.id}\n\n"
            f"📦 Mahsulotlar:\n{order.product_list or 'Noma’lum'}\n\n"
            f"💵 Oldindan to‘langan summa: {money_format(order.prepayment_amount)} so‘m\n"
            f"💵 Qolgan to‘lov: {money_format(order.remaining_amount)} so‘m\n"
            f"💵 Umumiy summa: {money_format(order.total_price)} so‘m\n\n"
            f"📌 Holat: {order.get_status_display()}\n"
            f"📅 Sana: {order.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        await message.answer(text)

    # (ixtiyoriy) Admin'ga yuborish
    # ADMIN_CHAT_ID = 123456789
    # await message.bot.send_message(
    #     ADMIN_CHAT_ID,
    #     f"🆕 Buyurtma #{order.id}\n👤 {user.full_name}\n📞 {user.phone_number}\n"
    #     f"💰 Oldindan: {money(total_prepayment)} so‘m\n"
    #     f"💰 Qolgan: {money(total_remaining)} so‘m\n"
    #     f"🧾:\n{product_list_text}"
    # )
    # await message.bot.send_photo(ADMIN_CHAT_ID, photo.file_id)
