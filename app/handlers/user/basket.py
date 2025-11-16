from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.engine import async_session_maker
from app.database.product_requests import get_product_by_id

router = Router()


@router.callback_query(F.data.startswith("add_basket_"))
async def add_to_basket_view(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    
    quantity = 1
    total_price = float(product.price) * quantity
    
    text = (
        f"📦 <b>{product.name}</b>\n\n"
        f"💰 Bir dona narxi: {product.price} so'm\n"
        f"📊 Miqdori: {quantity}\n"
        f"💵 Jami: {total_price:.2f} so'm\n\n"
        "Miqdorni sozlang va savatga saqlang:"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➖", callback_data=f"qty_dec_{product.id}_1"),
                InlineKeyboardButton(text=f"{quantity}", callback_data="qty_display"),
                InlineKeyboardButton(text="➕", callback_data=f"qty_inc_{product.id}_1")
            ],
            [InlineKeyboardButton(text="💾 Savatga saqlash", callback_data=f"save_basket_{product.id}_1")],
            [InlineKeyboardButton(text="🔙 Mahsulotlarga qaytish", callback_data=f"back_to_{product.type}")]
        ]
    )
    
    if product.product_image:
        try:
            await callback.message.edit_caption(caption=text, reply_markup=keyboard)
        except:
            await callback.message.delete()
            await callback.message.answer_photo(photo=product.product_image, caption=text, reply_markup=keyboard)
    else:
        await callback.message.edit_text(text, reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(F.data.startswith("qty_inc_"))
async def increase_quantity(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[2])
    current_qty = int(parts[3])
    new_qty = current_qty + 1
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    
    total_price = float(product.price) * new_qty
    
    text = (
        f"📦 <b>{product.name}</b>\n\n"
        f"💰 Bir dona narxi: {product.price} so'm\n"
        f"📊 Miqdori: {new_qty}\n"
        f"💵 Jami: {total_price:.2f} so'm\n\n"
        "Miqdorni sozlang va savatga saqlang:"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➖", callback_data=f"qty_dec_{product.id}_{new_qty}"),
                InlineKeyboardButton(text=f"{new_qty}", callback_data="qty_display"),
                InlineKeyboardButton(text="➕", callback_data=f"qty_inc_{product.id}_{new_qty}")
            ],
            [InlineKeyboardButton(text="💾 Savatga saqlash", callback_data=f"save_basket_{product.id}_{new_qty}")],
            [InlineKeyboardButton(text="🔙 Mahsulotlarga qaytish", callback_data=f"back_to_{product.type}")]
        ]
    )
    
    try:
        if product.product_image:
            await callback.message.edit_caption(caption=text, reply_markup=keyboard)
        else:
            await callback.message.edit_text(text, reply_markup=keyboard)
    except:
        pass
    
    await callback.answer()


@router.callback_query(F.data.startswith("qty_dec_"))
async def decrease_quantity(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[2])
    current_qty = int(parts[3])
    new_qty = max(1, current_qty - 1)
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    
    if new_qty < 1:
        # Return to initial state
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
    else:
        total_price = float(product.price) * new_qty
        
        text = (
            f"📦 <b>{product.name}</b>\n\n"
            f"💰 Bir dona narxi: {product.price} so'm\n"
            f"📊 Miqdori: {new_qty}\n"
            f"💵 Jami: {total_price:.2f} so'm\n\n"
            "Miqdorni sozlang va savatga saqlang:"
        )
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="➖", callback_data=f"qty_dec_{product.id}_{new_qty}"),
                    InlineKeyboardButton(text=f"{new_qty}", callback_data="qty_display"),
                    InlineKeyboardButton(text="➕", callback_data=f"qty_inc_{product.id}_{new_qty}")
                ],
                [InlineKeyboardButton(text="💾 Savatga saqlash", callback_data=f"save_basket_{product.id}_{new_qty}")],
                [InlineKeyboardButton(text="🔙 Mahsulotlarga qaytish", callback_data=f"back_to_{product.type}")]
            ]
        )
    
    try:
        if product.product_image:
            await callback.message.edit_caption(caption=text, reply_markup=keyboard)
        else:
            await callback.message.edit_text(text, reply_markup=keyboard)
    except:
        pass
    
    await callback.answer()


@router.callback_query(F.data.startswith("save_basket_"))
async def save_to_basket(callback: CallbackQuery):
    from app.database.requests import get_user_by_tg_id
    from app.database.order_requests import add_to_basket
    
    parts = callback.data.split("_")
    product_id = int(parts[2])
    quantity = int(parts[3])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
        user = await get_user_by_tg_id(session, callback.from_user.id)
        
        if not product or not user:
            await callback.answer("Savatga saqlashda xatolik!", show_alert=True)
            return
        
        await add_to_basket(session, user.id, product_id, quantity)
    
    await callback.answer("✅ Savatga qo'shildi!", show_alert=True)
    
    # Return to product view
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
    
    try:
        if product.product_image:
            await callback.message.edit_caption(caption=text, reply_markup=keyboard)
        else:
            await callback.message.edit_text(text, reply_markup=keyboard)
    except:
        pass
