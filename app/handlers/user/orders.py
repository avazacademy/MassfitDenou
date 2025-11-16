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


@router.message(F.text == "📦 My Orders")
async def my_orders(message: Message):
    from app.database.requests import get_user_by_tg_id
    from app.database.order_requests import get_basket_items
    
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, message.from_user.id)
        
        if not user:
            await message.answer("User not found!")
            return
        
        basket_items = await get_basket_items(session, user.id)
        
        if not basket_items:
            await message.answer(
                "🛒 <b>My Basket</b>\n\n"
                "Your basket is empty.\n"
                "Add products to your basket to create an order!"
            )
            return
        
        # Calculate total
        total = 0
        items_text = ""
        
        for item in basket_items:
            product = item.product
            item_total = float(product.price) * item.quantity
            total += item_total
            items_text += f"• {product.name}\n  💰 ${product.price} x {item.quantity} = ${item_total:.2f}\n\n"
        
        text = (
            f"🛒 <b>My Basket</b>\n\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Total: ${total:.2f}</b>"
        )
        
        keyboard = []
        for item in basket_items:
            keyboard.append([
                InlineKeyboardButton(text="➖", callback_data=f"basket_dec_{item.product_id}_{item.quantity}"),
                InlineKeyboardButton(text=f"{item.product.name}: {item.quantity}", callback_data="basket_display"),
                InlineKeyboardButton(text="➕", callback_data=f"basket_inc_{item.product_id}_{item.quantity}")
            ])
        
        keyboard.append([InlineKeyboardButton(text="✅ Confirm Order", callback_data="confirm_order_prompt")])
        
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
            items_text += f"• {product.name}\n  💰 ${product.price} x {item.quantity} = ${item_total:.2f}\n\n"
        
        text = (
            f"🛒 <b>My Basket</b>\n\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Total: ${total:.2f}</b>"
        )
        
        keyboard = []
        for item in basket_items:
            keyboard.append([
                InlineKeyboardButton(text="➖", callback_data=f"basket_dec_{item.product_id}_{item.quantity}"),
                InlineKeyboardButton(text=f"{item.product.name}: {item.quantity}", callback_data="basket_display"),
                InlineKeyboardButton(text="➕", callback_data=f"basket_inc_{item.product_id}_{item.quantity}")
            ])
        
        keyboard.append([InlineKeyboardButton(text="✅ Confirm Order", callback_data="confirm_order_prompt")])
        
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
                "🛒 <b>My Basket</b>\n\n"
                "Your basket is empty.\n"
                "Add products to your basket to create an order!"
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
            items_text += f"• {product.name}\n  💰 ${product.price} x {item.quantity} = ${item_total:.2f}\n\n"
        
        text = (
            f"🛒 <b>My Basket</b>\n\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Total: ${total:.2f}</b>"
        )
        
        keyboard = []
        for item in basket_items:
            keyboard.append([
                InlineKeyboardButton(text="➖", callback_data=f"basket_dec_{item.product_id}_{item.quantity}"),
                InlineKeyboardButton(text=f"{item.product.name}: {item.quantity}", callback_data="basket_display"),
                InlineKeyboardButton(text="➕", callback_data=f"basket_inc_{item.product_id}_{item.quantity}")
            ])
        
        keyboard.append([InlineKeyboardButton(text="✅ Confirm Order", callback_data="confirm_order_prompt")])
        
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    
    await callback.answer()


@router.callback_query(F.data == "confirm_order_prompt")
async def confirm_order_prompt(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏢 Pick Up", callback_data="order_pickup"),
                InlineKeyboardButton(text="🚚 Delivery", callback_data="order_delivery")
            ]
        ]
    )
    
    await callback.message.edit_text(
        "📦 <b>How would you like to receive your order?</b>\n\n"
        "Choose delivery method:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "order_delivery")
async def order_delivery_request_location(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📍 <b>Delivery Address</b>\n\n"
        "Please share your location for delivery.\n"
        "Use the 📎 attachment button to send your location."
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
                InlineKeyboardButton(text="✅ Yes", callback_data="confirm_order_yes_delivery"),
                InlineKeyboardButton(text="❌ No", callback_data="confirm_order_no")
            ]
        ]
    )
    
    await message.answer(
        f"📍 <b>Location Received</b>\n\n"
        f"Latitude: {latitude}\n"
        f"Longitude: {longitude}\n\n"
        f"❓ Do you confirm your order?",
        reply_markup=keyboard
    )
    await state.clear()


@router.callback_query(F.data == "order_pickup")
async def order_pickup_show_branches(callback: CallbackQuery):
    from app.database.branch_requests import get_all_branches
    
    async with async_session_maker() as session:
        branches = await get_all_branches(session)
    
    if not branches:
        await callback.message.edit_text(
            "🏢 <b>No Branches Available</b>\n\n"
            "Sorry, there are currently no branches available for pickup.\n"
            "Please contact support."
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "🏢 <b>Select a Branch for Pickup</b>\n\n"
        "Choose a branch to pick up your order:"
    )
    
    for branch in branches:
        text = (
            f"🏢 <b>{branch.name}</b>\n\n"
            f"📝 {branch.description or 'No description'}\n"
            f"📍 Location: {branch.location}"
        )
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📦 Order from this branch", callback_data=f"pickup_branch_{branch.id}")]
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
                InlineKeyboardButton(text="✅ Yes", callback_data="confirm_order_yes_pickup"),
                InlineKeyboardButton(text="❌ No", callback_data="confirm_order_no")
            ]
        ]
    )
    
    await callback.message.answer(
        "❓ <b>Confirm Order</b>\n\n"
        "Do you confirm your order?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_order_no")
async def confirm_order_no(callback: CallbackQuery):
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
            items_text += f"• {product.name}\n  💰 ${product.price} x {item.quantity} = ${item_total:.2f}\n\n"
        
        text = (
            f"🛒 <b>My Basket</b>\n\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Total: ${total:.2f}</b>"
        )
        
        keyboard = []
        for item in basket_items:
            keyboard.append([
                InlineKeyboardButton(text="➖", callback_data=f"basket_dec_{item.product_id}_{item.quantity}"),
                InlineKeyboardButton(text=f"{item.product.name}: {item.quantity}", callback_data="basket_display"),
                InlineKeyboardButton(text="➕", callback_data=f"basket_inc_{item.product_id}_{item.quantity}")
            ])
        
        keyboard.append([InlineKeyboardButton(text="✅ Confirm Order", callback_data="confirm_order_prompt")])
        
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    
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
            await callback.answer("Your basket is empty!", show_alert=True)
            return
        
        # Calculate total
        total = 0
        items_text = ""
        
        for item in basket_items:
            product = item.product
            item_total = float(product.price) * item.quantity
            total += item_total
            items_text += f"• {product.name}\n  💰 ${product.price} x {item.quantity} = ${item_total:.2f}\n\n"
        
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
            f"🆕 <b>New Order #{order.id}</b>\n\n"
            f"👤 Customer: {user.full_name or user.first_name}\n"
            f"📱 Phone: {user.phone_number or 'Not provided'}\n"
            f"🆔 User ID: {user.tg_id}\n"
            f"🚚 Delivery Type: <b>Delivery</b>\n\n"
            f"📦 <b>Order Items:</b>\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Total: ${total:.2f}</b>\n"
            f"📊 Status: {order.status}"
        )
        
        group_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="❌ Cancel", callback_data=f"order_status_{order.id}_cancelled"),
                    InlineKeyboardButton(text="✅ Delivered", callback_data=f"order_status_{order.id}_delivered")
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
            
            # Send location
            await bot.send_location(
                chat_id=GROUP_ID,
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
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
        f"✅ <b>Order Confirmed!</b>\n\n"
        f"Your order #{order.id} has been placed successfully.\n"
        f"Total: ${total:.2f}\n"
        f"Delivery Type: Delivery\n\n"
        f"We will deliver to your location soon!"
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
            await callback.answer("Your basket is empty!", show_alert=True)
            return
        
        # Calculate total
        total = 0
        items_text = ""
        
        for item in basket_items:
            product = item.product
            item_total = float(product.price) * item.quantity
            total += item_total
            items_text += f"• {product.name}\n  💰 ${product.price} x {item.quantity} = ${item_total:.2f}\n\n"
        
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
            f"🆕 <b>New Order #{order.id}</b>\n\n"
            f"👤 Customer: {user.full_name or user.first_name}\n"
            f"📱 Phone: {user.phone_number or 'Not provided'}\n"
            f"🆔 User ID: {user.tg_id}\n"
            f"🏢 Pickup Branch: <b>{branch.name}</b>\n"
            f"📍 Branch Location: {branch.location}\n\n"
            f"📦 <b>Order Items:</b>\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Total: ${total:.2f}</b>\n"
            f"📊 Status: {order.status}"
        )
        
        group_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="❌ Cancel", callback_data=f"order_status_{order.id}_cancelled"),
                    InlineKeyboardButton(text="✅ Delivered", callback_data=f"order_status_{order.id}_delivered")
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
        f"✅ <b>Order Confirmed!</b>\n\n"
        f"Information about your product has been sent to the branch.\n"
        f"They will contact you shortly!\n\n"
        f"📦 Order #{order.id}\n"
        f"💵 Total: ${total:.2f}\n"
        f"🏢 Branch: {branch.name}"
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
            await callback.answer("Order not found!", show_alert=True)
            return
        
        # Get order details
        order_items = await get_order_items(session, order_id)
        user = await get_user_by_id(session, order.user_id)
        
        items_text = ""
        for item in order_items:
            item_total = float(item.product_price) * item.quantity
            items_text += f"• {item.product_name}\n  💰 ${item.product_price} x {item.quantity} = ${item_total:.2f}\n\n"
        
        # Update group message with HTML parse mode
        group_text = (
            f"🆕 <b>New Order #{order.id}</b>\n\n"
            f"👤 Customer: {user.full_name or user.first_name}\n"
            f"📱 Phone: {user.phone_number or 'Not provided'}\n"
            f"🆔 User ID: {user.tg_id}\n\n"
            f"📦 <b>Order Items:</b>\n"
            f"{items_text}"
            f"━━━━━━━━━━━━━━━\n"
            f"💵 <b>Total: ${order.total_price}</b>\n"
            f"📊 Status: <b>{new_status.upper()}</b>"
        )
        
        group_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="❌ Cancel", callback_data=f"order_status_{order.id}_cancelled"),
                    InlineKeyboardButton(text="✅ Delivered", callback_data=f"order_status_{order.id}_delivered")
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
                text=f"{status_emoji} <b>Order #{order.id} Status Update</b>\n\n"
                     f"Your order status has been updated to: <b>{new_status.upper()}</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Error notifying user: {e}")
    
    await callback.answer(f"Order status updated to {new_status}!")
    await bot.session.close()
