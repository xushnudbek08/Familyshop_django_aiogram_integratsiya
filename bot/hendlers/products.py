from aiogram import Router, types, F
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from api.models import Category, Product, Cart, TelegramUser
from bot.states import CartAddStates
from aiogram.filters import StateFilter
from bot.keyboards import rasmiylashtirish, menyu


router = Router()

# Kategoriyalarni ko'rsatish
@router.message(F.text == "🛍 mahsulotlar")
async def show_categories(message: types.Message):
    categories = await sync_to_async(list)(Category.objects.all())

    buttons = [InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}") for cat in categories]
    # 2 tadan tugma bilan satrlar hosil qilamiz
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
    
    await message.answer("Kategoriyalar ro'yxati:", reply_markup=keyboard)


# Mahsulotlarni ko'rsatish
@router.callback_query(F.data.startswith("category_"))
async def show_products(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    products = await sync_to_async(list)(Product.objects.filter(category_id=category_id).prefetch_related("images").all())

    if not products:
        await callback.message.answer("Bu kategoriyada mahsulotlar topilmadi.")
        await callback.answer()
        return

    for product in products:
        media = []
        for i, img in enumerate(product.images.all()):
            file = FSInputFile(img.image.path)
            caption = None
            if i == 0:
               caption = (
                    f"🛍️ {product.name}\n"
                    f"🎨 Rangi: {product.color}\n"
                    f"📏 Razmerlari: {product.size}\n"
                    f"📝 Tavsifi: {product.description or 'Tavsif yo‘q.'}\n"
                    f"💰 Oldin to‘lanadigan narxi: {product.prepayment_price}\n"
                    f"💳 Keyin to‘lanadigan narxi: {product.remaining_price}\n"
                    f"🧾 Umumiy narxi: {product.total_price}"
                )

            media.append(InputMediaPhoto(media=file, caption=caption))
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Savatchaga qo'shish 🛒", callback_data=f"addcart_{product.id}")]
        ])

        if media:
            await callback.message.answer_media_group(media)
            await callback.message.answer("Quyidagi tugmani bosing:", reply_markup=keyboard)

        else:
            await callback.message.answer(f"🛍️ {product.name} uchun rasm mavjud emas.", reply_markup=keyboard)

    await callback.answer()

# FSM boshlandi - rang so'rash
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class CartAddStates(StatesGroup):
    waiting_for_color = State()
    waiting_for_size = State()
    waiting_for_quantity = State()



# 1️⃣ Callback bosilganda product_id ni olish va rang so‘rash
@router.callback_query(F.data.startswith("addcart_"))
async def add_to_cart_start(callback: types.CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await state.update_data(product_id=product_id)
    await state.set_state(CartAddStates.waiting_for_color)
    await callback.message.answer("🎨 Mahsulot rangi (color) ni kiriting:")
    await callback.answer()

# 🎨 2. Rang qabul qilish
@router.message(StateFilter(CartAddStates.waiting_for_color))
async def color_received(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text.strip())
    await state.set_state(CartAddStates.waiting_for_size)
    await message.answer("📏 Mahsulot o‘lchamini (size) kiriting:")

# 📏 3. O‘lcham qabul qilish
@router.message(StateFilter(CartAddStates.waiting_for_size))
async def size_received(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text.strip())
    await state.set_state(CartAddStates.waiting_for_quantity)
    await message.answer("🔢 Mahsulot miqdorini kiriting:")

# 🔢 4. Miqdor qabul qilish va bazaga yozish
@router.message(StateFilter(CartAddStates.waiting_for_quantity))
async def quantity_received(message: types.Message, state: FSMContext):
    qty = message.text.strip()
    if not qty.isdigit() or int(qty) < 1:
        await message.answer("❌ Iltimos, to‘g‘ri raqam kiriting.")
        return

    data = await state.get_data()
    product_id = data["product_id"]

    # Foydalanuvchini tekshirish
    user = await sync_to_async(TelegramUser.objects.filter(telegram_id=message.from_user.id).first)()
    if not user:
        await message.answer("❌ Siz ro‘yxatdan o‘tmagansiz.")
        await state.clear()
        return

    # Mahsulotni tekshirish
    product = await sync_to_async(Product.objects.filter(id=product_id).first)()
    if not product:
        await message.answer("❌ Mahsulot topilmadi.")
        await state.clear()
        return

    # Cart ga qo‘shish
    await sync_to_async(Cart.objects.create)(
        user=user,
        product=product,
        color=data["color"],
        size=data["size"],
        quantity=int(qty)
    )

    await message.answer(
        f"✅ Savatga qo‘shildi:\n"
        f"🖌 Rang: {data['color']}\n📏 O‘lcham: {data['size']}\n🔢 Miqdor: {qty}"
    )
    await state.clear()





@router.message(F.text == "🛒 savat")
async def view_cart(message: types.Message):
    # Foydalanuvchini olish
    user = await sync_to_async(TelegramUser.objects.filter(telegram_id=message.from_user.id).first)()
    if not user:
        await message.answer("❌ Siz ro‘yxatdan o‘tmagansiz.")
        return

    # Savatdagi mahsulotlarni olish
    cart_items = await sync_to_async(list)(
        Cart.objects.filter(user=user).select_related("product")
    )

    if not cart_items:
        await message.answer("🛒 Savatingiz bo‘sh.")
        return

    total_sum = 0
    prepayment_price = 0
    remaining_price = 0
    
    text = "🛒 **Sizning savatingiz:**\n\n"

    for idx, item in enumerate(cart_items, start=1):
        prepayment_pricee = item.quantity * item.product.prepayment_price
        item_remaining_price = item.quantity * item.product.remaining_price
        item_total = item.quantity * item.product.total_price
        prepayment_price += prepayment_pricee
        remaining_price += item_remaining_price
        total_sum += item_total
        text += (
            f"{idx}. {item.product.name}\n"
            f"   🎨 Rang: {item.color}\n"
            f"   📏 O‘lcham: {item.size}\n"
            f"   🔢 Miqdor: {item.quantity}\n"
            f"   💵 Narx oldin: {item.product.prepayment_price} so‘m\n"
            f"   💵 Narx keyin: {item.product.remaining_price} so‘m\n"
            f"   💵 Narx umumiy: {item.product.total_price} so‘m\n"
            
        )

    text += f"**Oldindan tolanaigan summa:** {prepayment_price} so‘m\n"
    text += f"**Tavarni olgandan keyin tolanaigan summa:** {remaining_price} so‘m\n"
    text += f"**Umumiy tolanadigan summa:** {total_sum} so‘m"

    await message.answer(text, parse_mode="Markdown",reply_markup=rasmiylashtirish)




@router.message(F.text == "🗑 savatni tozalsh")
async def clear_cart(message: types.Message):
    tg_id = message.from_user.id

    # Userni topish
    user = await sync_to_async(TelegramUser.objects.filter(telegram_id=tg_id).first)()
    if not user:
        await message.answer("Siz ro‘yxatdan o‘tmagansiz.")
        return

    # Savatni tozalash
    deleted_count = await sync_to_async(Cart.objects.filter(user=user).delete)()
    if deleted_count[0] > 0:
        await message.answer("🗑 Savat tozalandi!")
    else:
        await message.answer("Savat allaqachon bo‘sh edi.")


@router.message(F.text == "🔙 Orqaga")
async def back_to_menu(message: types.Message):
    await message.answer("Siz bosh menyuga qaytdingiz", reply_markup=menyu)

# from aiogram import Router, types
# from aiogram.types import FSInputFile, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.filters import Command
# from asgiref.sync import sync_to_async


# router = Router()

# @router.message(Command("products"))
# async def show_products(message: types.Message):
#     products = await sync_to_async(list)(Product.objects.prefetch_related("images").all())
    
#     for product in products:
#         media = []
#         for i, img in enumerate(product.images.all()):
#             file = FSInputFile(img.image.path)
#             caption = f"🛍️ {product.name}\n{product.description}" if i == 0 else None
#             media.append(InputMediaPhoto(media=file, caption=caption))
        
#         if media:
#             await message.answer_media_group(media)
        
#         # Har bir product ostida inline tugma
#         keyboard = InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="Savatchaga qo'shish 🛒", callback_data=f"addcart_{product.id}")]
#         ])
        
#         await message.answer("Mahsulotni savatchaga qo'shish uchun quyidagi tugmani bosing:", reply_markup=keyboard)


# @router.callback_query(lambda c: c.data and c.data.startswith("addcart_"))
# async def add_to_cart(callback: CallbackQuery):
#     product_id = int(callback.data.split("_")[1])
#     user_id = callback.from_user.id
    
#     # Mana shu yerda siz savatga qo'shish logikasini yozasiz
#     # Masalan oddiy dict yoki DB ga yozish
    
#     await callback.answer("Mahsulot savatchaga qo'shildi ✅", show_alert=True)
