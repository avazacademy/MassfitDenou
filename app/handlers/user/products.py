from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.engine import async_session_maker
from app.database.product_requests import get_products_by_type, get_product_by_id

router = Router()


@router.message(F.text == "🔻 Vazn yo'qotish")
async def lose_weight_menu(message: Message):
    async with async_session_maker() as session:
        products = await get_products_by_type(session, "weight_loss")
    
    if not products:
        await message.answer(
            "🔻 <b>Vazn yo'qotish mahsulotlari</b>\n\n"
            "Bu toifadagi mahsulotlar tanangizning ortiqcha vaznini yo'qotishga yordam beradi.\n\n"
            "Hozircha bu toifada mahsulotlar mavjud emas."
        )
        return
    
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name} - {product.price} so'm",
                callback_data=f"user_product_{product.id}"
            )
        ])
    
    await message.answer(
        "🔻 <b>Vazn yo'qotish mahsulotlari</b>\n\n"
        "Bu toifadagi mahsulotlar tanangizning ortiqcha vaznini yo'qotishga yordam beradi.\n\n"
        "Batafsil ma'lumot olish uchun mahsulotni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@router.message(F.text == "🔺 Vazn olish")
async def gain_weight_menu(message: Message):
    async with async_session_maker() as session:
        products = await get_products_by_type(session, "weight_gain")
    
    if not products:
        await message.answer(
            "🔺 <b>Vazn olish mahsulotlari</b>\n\n"
            "Bu toifadagi mahsulotlar tanangizga sog'lom vazn va mushak massasini oshirishga yordam beradi.\n\n"
            "Hozircha bu toifada mahsulotlar mavjud emas."
        )
        return
    
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name} - {product.price} so'm",
                callback_data=f"user_product_{product.id}"
            )
        ])
    
    await message.answer(
        "🔺 <b>Vazn olish mahsulotlari</b>\n\n"
        "Bu toifadagi mahsulotlar tanangizga sog'lom vazn va mushak massasini oshirishga yordam beradi.\n\n"
        "Batafsil ma'lumot olish uchun mahsulotni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@router.callback_query(F.data.startswith("user_product_"))
async def view_user_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    
    text = (
        f"📦 <b>{product.name}</b>\n\n"
        f"💰 Narxi: {product.price} so'm\n"
        f"📝 Tavsif: {product.description or 'Tavsif berilmagan'}\n\n"
        "Bu mahsulotni buyurtma qilish uchun savatga qo'shing!"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Savatga qo'shish", callback_data=f"add_basket_{product.id}")],
            [InlineKeyboardButton(text="🔙 Mahsulotlarga qaytish", callback_data=f"back_to_{product.type}")]
        ]
    )
    
    if product.product_image:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=product.product_image,
            caption=text,
            reply_markup=keyboard
        )
    else:
        await callback.message.edit_text(text, reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_"))
async def back_to_category(callback: CallbackQuery):
    product_type = callback.data.replace("back_to_", "")
    
    async with async_session_maker() as session:
        products = await get_products_by_type(session, product_type)
    
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name} - {product.price} so'm",
                callback_data=f"user_product_{product.id}"
            )
        ])
    
    if product_type == "weight_loss":
        title = "🔻 <b>Vazn yo'qotish mahsulotlari</b>\n\n"
        description = "Bu toifadagi mahsulotlar tanangizning ortiqcha vaznini yo'qotishga yordam beradi.\n\n"
    else:
        title = "🔺 <b>Vazn olish mahsulotlari</b>\n\n"
        description = "Bu toifadagi mahsulotlar tanangizga sog'lom vazn va mushak massasini oshirishga yordam beradi.\n\n"
    
    text = title + description + "Batafsil ma'lumot olish uchun mahsulotni tanlang:"
    
    # Check if current message has photo (no text to edit)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    await callback.answer()
