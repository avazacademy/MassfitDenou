from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.engine import async_session_maker
from app.database.product_requests import get_products_by_type, get_product_by_id

router = Router()


@router.message(F.text == "🔻 Lose Weight")
async def lose_weight_menu(message: Message):
    async with async_session_maker() as session:
        products = await get_products_by_type(session, "weight_loss")
    
    if not products:
        await message.answer(
            "🔻 <b>Weight Loss Products</b>\n\n"
            "This category of products helps your body lose excess weight.\n\n"
            "Currently, there are no products available in this category."
        )
        return
    
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name} - ${product.price}",
                callback_data=f"user_product_{product.id}"
            )
        ])
    
    await message.answer(
        "🔻 <b>Weight Loss Products</b>\n\n"
        "This category of products helps your body lose excess weight.\n\n"
        "Select a product to view details:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@router.message(F.text == "🔺 Gain Weight")
async def gain_weight_menu(message: Message):
    async with async_session_maker() as session:
        products = await get_products_by_type(session, "weight_gain")
    
    if not products:
        await message.answer(
            "🔺 <b>Weight Gain Products</b>\n\n"
            "This category of products helps your body gain healthy weight and build muscle mass.\n\n"
            "Currently, there are no products available in this category."
        )
        return
    
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name} - ${product.price}",
                callback_data=f"user_product_{product.id}"
            )
        ])
    
    await message.answer(
        "🔺 <b>Weight Gain Products</b>\n\n"
        "This category of products helps your body gain healthy weight and build muscle mass.\n\n"
        "Select a product to view details:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@router.callback_query(F.data.startswith("user_product_"))
async def view_user_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Product not found!", show_alert=True)
        return
    
    text = (
        f"📦 <b>{product.name}</b>\n\n"
        f"💰 Price: ${product.price}\n"
        f"📝 Description: {product.description or 'No description provided'}\n\n"
        "To order this product, add it to your basket!"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Add to Basket", callback_data=f"add_basket_{product.id}")],
            [InlineKeyboardButton(text="🔙 Back to Products", callback_data=f"back_to_{product.type}")]
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
                text=f"{product.name} - ${product.price}",
                callback_data=f"user_product_{product.id}"
            )
        ])
    
    if product_type == "weight_loss":
        title = "🔻 <b>Weight Loss Products</b>\n\n"
        description = "This category of products helps your body lose excess weight.\n\n"
    else:
        title = "🔺 <b>Weight Gain Products</b>\n\n"
        description = "This category of products helps your body gain healthy weight and build muscle mass.\n\n"
    
    await callback.message.edit_text(
        title + description + "Select a product to view details:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()
