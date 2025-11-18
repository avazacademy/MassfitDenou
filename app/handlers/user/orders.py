from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.database.engine import async_session_maker

router = Router()


class OrderStates(StatesGroup):
    waiting_for_delivery_location = State()


@router.message(F.text == "📦 Mening buyurtmalarim")
async def my_orders(message: Message):
    from app.database.requests import get_user_by_tg_id
    from app.database.order_requests import get_basket_items
    
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, message.from_user.id)
        
        if not user:
            await message.answer("Foydalanuvchi topilmadi!")
            return
        
        basket_items = await get_basket_items(session, user.id)
        
        if not basket_items:
            await message.answer(
                "🛒 <b>Mening savatim</b>\n\n"
                "Savatingiz bo'sh.\n"
                "Buyurtma yaratish uchun mahsulotlarni savatga qo'shing!"
            )
            return
        
        # Calculate total
        total = 0
        items_text = ""
        
        for item in basket_items:
            product = item.product
            item_total = float(product.price) * item.quantity
            total += item_total
            items_text += f"• {product.name}\n  💰 {product.price} so'm x {item.quantity} = {item_total:.2f} so'm\n\n"
        
        text = (
            f"🛒 <b>Mening savatim</b>\n\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Jami: {total:.2f} so'm</b>"
        )
        
        keyboard = []
        for item in basket_items:
            keyboard.append([
                InlineKeyboardButton(text="➖", callback_data=f"basket_dec_{item.product_id}_{item.quantity}"),
                InlineKeyboardButton(text=f"{item.product.name}: {item.quantity}", callback_data="basket_display"),
                InlineKeyboardButton(text="➕", callback_data=f"basket_inc_{item.product_id}_{item.quantity}")
            ])
        
        keyboard.append([InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="confirm_order_prompt")])
        
        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))


@router.callback_query(F.data.startswith("basket_inc_"))
async def basket_increase(callback: CallbackQuery):
    from app.database.requests import get_user_by_tg_id
    from app.database.order_requests import update_basket_quantity, get_basket_items
    
    parts = callback.data.split("_")
    product_id = int(parts[2])
    current_qty = int(parts[3])
    new_qty = current_qty + 1
    
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, callback.from_user.id)
        await update_basket_quantity(session, user.id, product_id, new_qty)
        
        basket_items = await get_basket_items(session, user.id)
        
        # Recalculate total
        total = 0
        items_text = ""
        
        for item in basket_items:
            product = item.product
            item_total = float(product.price) * item.quantity
            total += item_total
            items_text += f"• {product.name}\n  💰 {product.price} so'm x {item.quantity} = {item_total:.2f} so'm\n\n"
        
        text = (
            f"🛒 <b>Mening savatim</b>\n\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Jami: {total:.2f} so'm</b>"
        )
        
        keyboard = []
        for item in basket_items:
            keyboard.append([
                InlineKeyboardButton(text="➖", callback_data=f"basket_dec_{item.product_id}_{item.quantity}"),
                InlineKeyboardButton(text=f"{item.product.name}: {item.quantity}", callback_data="basket_display"),
                InlineKeyboardButton(text="➕", callback_data=f"basket_inc_{item.product_id}_{item.quantity}")
            ])
        
        keyboard.append([InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="confirm_order_prompt")])
        
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    
    await callback.answer()


@router.callback_query(F.data.startswith("basket_dec_"))
async def basket_decrease(callback: CallbackQuery):
    from app.database.requests import get_user_by_tg_id
    from app.database.order_requests import update_basket_quantity, get_basket_items
    
    parts = callback.data.split("_")
    product_id = int(parts[2])
    current_qty = int(parts[3])
    new_qty = max(0, current_qty - 1)
    
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, callback.from_user.id)
        await update_basket_quantity(session, user.id, product_id, new_qty)
        
        basket_items = await get_basket_items(session, user.id)
        
        if not basket_items:
            await callback.message.edit_text(
                "🛒 <b>Mening savatim</b>\n\n"
                "Savat bo'sh.\n"
                "Buyurtma yaratish uchun mahsulotlarni savatga qo'shing!"
            )
            await callback.answer()
            return
        
        # Recalculate total
        total = 0
        items_text = ""
        
        for item in basket_items:
            product = item.product
            item_total = float(product.price) * item.quantity
            total += item_total
            items_text += f"• {product.name}\n  💰 {product.price} so'm x {item.quantity} = {item_total:.2f} so'm\n\n"
        
        text = (
            f"🛒 <b>Mening savatim</b>\n\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Jami: {total:.2f} so'm</b>"
        )
        
        keyboard = []
        for item in basket_items:
            keyboard.append([
                InlineKeyboardButton(text="➖", callback_data=f"basket_dec_{item.product_id}_{item.quantity}"),
                InlineKeyboardButton(text=f"{item.product.name}: {item.quantity}", callback_data="basket_display"),
                InlineKeyboardButton(text="➕", callback_data=f"basket_inc_{item.product_id}_{item.quantity}")
            ])
        
        keyboard.append([InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="confirm_order_prompt")])
        
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    
    await callback.answer()


@router.callback_query(F.data == "confirm_order_prompt")
async def confirm_order_prompt(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏢 Olish uchun", callback_data="order_pickup"),
                InlineKeyboardButton(text="🚚 Yetkazib berish", callback_data="order_delivery")
            ]
        ]
    )
    
    await callback.message.edit_text(
        "📦 <b>Buyurtmangizni qanday olishni xohlaysiz?</b>\n\n"
        "Yetkazib berish usulini tanlang:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "order_delivery")
async def order_delivery_request_location(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📍 <b>Yetkazib berish manzili</b>\n\n"
        "Iltimos, yetkazib berish uchun joylashuvingizni yuboring.\n"
        "Joylashuvingizni yuborish uchun 📎 qo'shimcha tugmasidan foydalaning."
    )
    await state.set_state(OrderStates.waiting_for_delivery_location)
    await callback.answer()


@router.message(OrderStates.waiting_for_delivery_location, F.location)
async def process_delivery_location(message: Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    
    await state.update_data(
        delivery_type='delivery',
        latitude=latitude,
        longitude=longitude
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data="confirm_order_yes_delivery"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data="confirm_order_no")
            ]
        ]
    )
    
    await message.answer(
        f"📍 <b>Joylashuv qabul qilindi</b>\n\n"
        f"Latitude: {latitude}\n"
        f"Longitude: {longitude}\n\n"
        f"❓ Buyurtmangizni tasdiqlaysizmi?",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "order_pickup")
async def order_pickup_show_branches(callback: CallbackQuery):
    from app.database.branch_requests import get_all_branches
    
    async with async_session_maker() as session:
        branches = await get_all_branches(session)
    
    if not branches:
        await callback.message.edit_text(
            "🏢 <b>Filiallar mavjud emas</b>\n\n"
            "Afsuski, hozirda olish uchun filiallar mavjud emas.\n"
            "Iltimos, qo'llab-quvvatlash xizmatiga murojaat qiling."
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "🏢 <b>Olish uchun filialni tanlang</b>\n\n"
        "Buyurtmangizni olish uchun filialni tanlang:"
    )
    no_desc = "Tavsif yo'q"
    for branch in branches:
        text = (
            f"🏢 <b>{branch.name}</b>\n\n"
            f"📝 {branch.description or no_desc}\n"
            f"📍 Joylashuv: {branch.location}"
        )
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📦 Buyurtma berish", callback_data=f"pickup_branch_{branch.id}")]
            ]
        )
        
        if branch.image:
            await callback.message.answer_photo(
                photo=branch.image,
                caption=text,
                reply_markup=keyboard
            )
        else:
            await callback.message.answer(text, reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(F.data.startswith("pickup_branch_"))
async def confirm_pickup_branch(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[2])
    
    await state.update_data(
        delivery_type='pickup',
        branch_id=branch_id
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data="confirm_order_yes_pickup"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data="confirm_order_no")
            ]
        ]
    )
    
    await callback.message.answer(
        "❓ <b>Buyurtmani tasdiqlash</b>\n\n"
        "Buyurtmangizni tasdiqlaysizmi?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_order_no")
async def confirm_order_no(callback: CallbackQuery, state: FSMContext):
    from app.database.requests import get_user_by_tg_id
    from app.database.order_requests import get_basket_items
    
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, callback.from_user.id)
        basket_items = await get_basket_items(session, user.id)
        
        # Recalculate total
        total = 0
        items_text = ""
        
        for item in basket_items:
            product = item.product
            item_total = float(product.price) * item.quantity
            total += item_total
            items_text += f"• {product.name}\n  💰 {product.price} so'm x {item.quantity} = {item_total:.2f} so'm\n\n"
        
        text = (
            f"🛒 <b>Mening savatim</b>\n\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Jami: {total:.2f} so'm</b>"
        )
        
        keyboard = []
        for item in basket_items:
            keyboard.append([
                InlineKeyboardButton(text="➖", callback_data=f"basket_dec_{item.product_id}_{item.quantity}"),
                InlineKeyboardButton(text=f"{item.product.name}: {item.quantity}", callback_data="basket_display"),
                InlineKeyboardButton(text="➕", callback_data=f"basket_inc_{item.product_id}_{item.quantity}")
            ])
        
        keyboard.append([InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="confirm_order_prompt")])
        
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "confirm_order_yes_delivery")
async def confirm_order_yes_delivery(callback: CallbackQuery, state: FSMContext):
    from app.database.requests import get_user_by_tg_id
    from app.database.order_requests import (
        get_basket_items, 
        create_order, 
        create_order_item, 
        clear_basket
    )
    from app.config import GROUP_ID, BOT_TOKEN
    from aiogram import Bot
    
    bot = Bot(token=BOT_TOKEN)
    data = await state.get_data()
    
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, callback.from_user.id)
        basket_items = await get_basket_items(session, user.id)
        
        if not basket_items:
            await callback.answer("Savatingiz bo'sh!", show_alert=True)
            return
        
        # Calculate total
        total = 0
        items_text = ""
        
        for item in basket_items:
            product = item.product
            item_total = float(product.price) * item.quantity
            total += item_total
            items_text += f"• {product.name}\n  💰 {product.price} so'm x {item.quantity} = {item_total:.2f} so'm\n\n"
        
        # Create order with delivery details
        order = await create_order(
            session, 
            user.id, 
            total,
            delivery_type='delivery',
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        # Create order items
        for item in basket_items:
            await create_order_item(
                session,
                order.id,
                item.product_id,
                item.product.name,
                float(item.product.price),
                item.quantity
            )
        
        # Send to group with delivery location
        group_text = (
            f"🆕 <b>Yangi Buyurtma #{order.id}</b>\n\n"
            f"👤 Mijoz: {user.full_name or user.first_name}\n"
            f"📱 Telefon: {user.phone_number or 'Berilmagan'}\n"
            f"🆔 Foydalanuvchi ID: {user.tg_id}\n"
            f"🚚 Yetkazib berish turi: <b>Yetkazib berish</b>\n\n"
            f"📦 <b>Buyurtma mahsulotlari:</b>\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Jami: {total:.2f} so'm</b>\n"
            f"📊 Holati: {order.status}"
        )
        
        group_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"order_status_{order.id}_cancelled"),
                    InlineKeyboardButton(text="✅ Yetkazildi", callback_data=f"order_status_{order.id}_delivered")
                ]
            ]
        )
        
        try:
            # Send text first
            group_message = await bot.send_message(
                chat_id=GROUP_ID,
                text=group_text,
                reply_markup=group_keyboard,
                parse_mode=ParseMode.HTML
            )
            
            # Send location if available
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            if latitude is not None and longitude is not None:
                await bot.send_location(
                    chat_id=GROUP_ID,
                    latitude=latitude,
                    longitude=longitude,
                    reply_to_message_id=group_message.message_id
                )
            
            # Update order with group message id
            order.group_message_id = group_message.message_id
            await session.commit()
        except Exception as e:
            print(f"Error sending to group: {e}")
        
        # Clear basket
        await clear_basket(session, user.id)
    
    await callback.message.edit_text(
        f"✅ <b>Buyurtma tasdiqlandi!</b>\n\n"
        f"Sizning buyurtmangiz #{order.id} muvaffaqiyatli joylashtirildi.\n"
        f"Jami: {total:.2f} so'm\n"
        f"Yetkazib berish turi: Yetkazib berish\n\n"
        f"Tez orada joylashuvingizga yetkazib beramiz!"
    )
    await state.clear()
    await callback.answer()
    await bot.session.close()


@router.callback_query(F.data == "confirm_order_yes_pickup")
async def confirm_order_yes_pickup(callback: CallbackQuery, state: FSMContext):
    from app.database.requests import get_user_by_tg_id
    from app.database.order_requests import (
        get_basket_items, 
        create_order, 
        create_order_item, 
        clear_basket
    )
    from app.database.branch_requests import get_branch_by_id
    from app.config import GROUP_ID, BOT_TOKEN
    from aiogram import Bot
    
    bot = Bot(token=BOT_TOKEN)
    data = await state.get_data()
    branch_id = data.get('branch_id')
    
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, callback.from_user.id)
        basket_items = await get_basket_items(session, user.id)
        branch = await get_branch_by_id(session, branch_id)
        
        if not basket_items:
            await callback.answer("Savatingiz bo'sh!", show_alert=True)
            return
        
        # Calculate total
        total = 0
        items_text = ""
        
        for item in basket_items:
            product = item.product
            item_total = float(product.price) * item.quantity
            total += item_total
            items_text += f"• {product.name}\n  💰 {product.price} so'm x {item.quantity} = {item_total:.2f} so'm\n\n"
        
        # Create order with pickup details
        order = await create_order(
            session, 
            user.id, 
            total,
            delivery_type='pickup',
            branch_id=branch_id
        )
        
        # Create order items
        for item in basket_items:
            await create_order_item(
                session,
                order.id,
                item.product_id,
                item.product.name,
                float(item.product.price),
                item.quantity
            )
        
        # Send to group with branch info
        group_text = (
            f"🆕 <b>Yangi Buyurtma #{order.id}</b>\n\n"
            f"👤 Mijoz: {user.full_name or user.first_name}\n"
            f"📱 Telefon: {user.phone_number or 'Berilmagan'}\n"
            f"🆔 Foydalanuvchi ID: {user.tg_id}\n"
            f"🏢 Olib ketish filiali: <b>{branch.name}</b>\n"
            f"📍 Filial manzili: {branch.location}\n\n"
            f"📦 <b>Buyurtma mahsulotlari:</b>\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Jami: {total:.2f} so'm</b>\n"
            f"📊 Holati: {order.status}"
        )
        
        group_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"order_status_{order.id}_cancelled"),
                    InlineKeyboardButton(text="✅ Yetkazildi", callback_data=f"order_status_{order.id}_delivered")
                ]
            ]
        )
        
        try:
            group_message = await bot.send_message(
                chat_id=GROUP_ID,
                text=group_text,
                reply_markup=group_keyboard,
                parse_mode=ParseMode.HTML
            )
            
            # Update order with group message id
            order.group_message_id = group_message.message_id
            await session.commit()
        except Exception as e:
            print(f"Error sending to group: {e}")
        
        # Clear basket
        await clear_basket(session, user.id)
    
    await callback.message.edit_text(
        f"✅ <b>Buyurtma tasdiqlandi!</b>\n\n"
        f"Mahsulotingiz haqida ma'lumot filialga yuborildi.\n"
        f"Ular tez orada siz bilan bog'lanishadi!\n\n"
        f"📦 Buyurtma #{order.id}\n"
        f"💵 Jami: {total:.2f} so'm\n"
        f"🏢 Filial: {branch.name}"
    )
    await state.clear()
    await callback.answer()
    await bot.session.close()


@router.callback_query(F.data.startswith("order_status_"))
async def update_order_status_handler(callback: CallbackQuery):
    from app.database.order_requests import update_order_status, get_order_by_id, get_order_items, get_user_by_id
    from app.config import BOT_TOKEN
    from aiogram import Bot
    
    parts = callback.data.split("_")
    order_id = int(parts[2])
    new_status = parts[3]
    
    bot = Bot(token=BOT_TOKEN)
    
    async with async_session_maker() as session:
        order = await update_order_status(session, order_id, new_status)
        
        if not order:
            await callback.answer("Buyurtma topilmadi!", show_alert=True)
            return
        
        # Get order details
        order_items = await get_order_items(session, order_id)
        user = await get_user_by_id(session, order.user_id)
        
        items_text = ""
        for item in order_items:
            item_total = float(item.product_price) * item.quantity
            items_text += f"• {item.product_name}\n  💰 {item.product_price} so'm x {item.quantity} = {item_total:.2f} so'm\n\n"
        
        # Update group message with HTML parse mode
        group_text = (
            f"🆕 <b>Yangi Buyurtma #{order.id}</b>\n\n"
            f"👤 Mijoz: {user.full_name or user.first_name}\n"
            f"📱 Telefon: {user.phone_number or 'Berilmagan'}\n"
            f"🆔 Foydalanuvchi ID: {user.tg_id}\n\n"
            f"📦 <b>Buyurtma mahsulotlari:</b>\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Jami: {order.total_price} so'm</b>\n"
            f"📊 Holati: <b>{new_status.upper()}</b>"
        )
        
        group_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"order_status_{order.id}_cancelled"),
                    InlineKeyboardButton(text="✅ Yetkazildi", callback_data=f"order_status_{order.id}_delivered")
                ]
            ]
        )
        
        try:
            await callback.message.edit_text(group_text, reply_markup=group_keyboard, parse_mode=ParseMode.HTML)
        except:
            pass
        
        # Notify user with HTML parse mode
        try:
            status_emoji = "❌" if new_status == "cancelled" else "✅"
            await bot.send_message(
                chat_id=user.tg_id,
                text=f"{status_emoji} <b>Buyurtma #{order.id} holati yangilandi</b>\n\n"
                     f"Buyurtma holati yangilandi: <b>{new_status.upper()}</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Error notifying user: {e}")
    
    await callback.answer(f"Buyurtma holati yangilandi: {new_status}!")
    await bot.session.close()
