from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.engine import async_session_maker
from app.database.product_requests import (
    get_all_products, 
    get_product_by_id, 
    create_product, 
    update_product, 
    delete_product
)
from app.keyboards.inline import (
    get_admin_panel_keyboard,
    get_product_list_keyboard,
    get_product_edit_keyboard,
    get_product_delete_keyboard,
    get_product_detail_keyboard,
    get_confirm_delete_keyboard,
    get_cancel_keyboard
)

router = Router()


class ProductStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_type = State()
    waiting_for_description = State()
    waiting_for_image = State()
    editing_name = State()
    editing_price = State()
    editing_type = State()
    editing_description = State()
    editing_image = State()


@router.callback_query(F.data == "admin_view_products")
async def view_all_products(callback: CallbackQuery):
    async with async_session_maker() as session:
        products = await get_all_products(session)
    
    if not products:
        await callback.message.edit_text(
            "📦 <b>Products List</b>\n\n"
            "No products found. Add your first product!",
            reply_markup=get_admin_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            f"📦 <b>Products List</b>\n\n"
            f"Total products: {len(products)}\n"
            "Select a product to view details:",
            reply_markup=get_product_list_keyboard(products)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("product_view_"))
async def view_product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Product not found!", show_alert=True)
        return
    
    text = (
        f"📦 <b>{product.name}</b>\n\n"
        f"💰 Price: ${product.price}\n"
        f"🏷 Type: {product.type}\n"
        f"📝 Description: {product.description or 'No description'}\n"
        f"🖼 Image: {'Yes' if product.product_image else 'No image'}\n\n"
        f"📅 Created: {product.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"🔄 Updated: {product.updated_at.strftime('%Y-%m-%d %H:%M')}"
    )
    
    if product.product_image:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=product.product_image,
            caption=text,
            reply_markup=get_product_detail_keyboard(product_id)
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_product_detail_keyboard(product_id)
        )
    await callback.answer()


# ADD PRODUCT
@router.callback_query(F.data == "admin_add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "➕ <b>Add New Product</b>\n\n"
        "Please enter the product name:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ProductStates.waiting_for_name)
    await callback.answer()


@router.message(ProductStates.waiting_for_name)
async def process_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        f"✅ Product name: <b>{message.text}</b>\n\n"
        "Now enter the product price (numbers only, e.g., 10.99):"
    )
    await state.set_state(ProductStates.waiting_for_price)


@router.message(ProductStates.waiting_for_price)
async def process_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError()
        
        await state.update_data(price=price)
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔻 Weight Loss", callback_data="type_weight_loss")],
                [InlineKeyboardButton(text="🔺 Weight Gain", callback_data="type_weight_gain")],
                [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_panel")]
            ]
        )
        
        await message.answer(
            f"✅ Price: <b>${price}</b>\n\n"
            "Now select the product type:",
            reply_markup=keyboard
        )
        await state.set_state(ProductStates.waiting_for_type)
    except ValueError:
        await message.answer(
            "❌ Invalid price! Please enter a valid number (e.g., 10.99):"
        )


@router.callback_query(ProductStates.waiting_for_type, F.data.startswith("type_"))
async def process_product_type(callback: CallbackQuery, state: FSMContext):
    product_type = "weight_loss" if callback.data == "type_weight_loss" else "weight_gain"
    await state.update_data(type=product_type)
    
    await callback.message.edit_text(
        f"✅ Type: <b>{product_type.replace('_', ' ').title()}</b>\n\n"
        "Now enter the product description (or send /skip to skip):"
    )
    await state.set_state(ProductStates.waiting_for_description)
    await callback.answer()


@router.message(ProductStates.waiting_for_description)
async def process_product_description(message: Message, state: FSMContext):
    description = None if message.text == "/skip" else message.text
    await state.update_data(description=description)
    
    await message.answer(
        f"✅ Description: <b>{description or 'Skipped'}</b>\n\n"
        "Finally, send the product image (or send /skip to skip):"
    )
    await state.set_state(ProductStates.waiting_for_image)


@router.message(ProductStates.waiting_for_image, F.photo)
async def process_product_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(image=file_id)
    
    data = await state.get_data()
    
    async with async_session_maker() as session:
        product = await create_product(
            session,
            name=data['name'],
            price=data['price'],
            product_type=data['type'],
            description=data.get('description'),
            product_image=file_id
        )
    
    text = (
        f"✅ <b>Product Added Successfully!</b>\n\n"
        f"📦 Name: {product.name}\n"
        f"💰 Price: ${product.price}\n"
        f"🏷 Type: {product.type}\n"
        f"📝 Description: {product.description or 'No description'}"
    )
    
    await message.answer_photo(
        photo=file_id,
        caption=text,
        reply_markup=get_admin_panel_keyboard()
    )
    await state.clear()


@router.message(ProductStates.waiting_for_image, F.text == "/skip")
async def skip_product_image(message: Message, state: FSMContext):
    data = await state.get_data()
    
    async with async_session_maker() as session:
        product = await create_product(
            session,
            name=data['name'],
            price=data['price'],
            product_type=data['type'],
            description=data.get('description'),
            product_image=None
        )
    
    await message.answer(
        f"✅ <b>Product Added Successfully!</b>\n\n"
        f"📦 Name: {product.name}\n"
        f"💰 Price: ${product.price}\n"
        f"🏷 Type: {product.type}\n"
        f"📝 Description: {product.description or 'No description'}",
        reply_markup=get_admin_panel_keyboard()
    )
    await state.clear()


# EDIT PRODUCT
@router.callback_query(F.data == "admin_edit_product")
async def start_edit_product(callback: CallbackQuery):
    async with async_session_maker() as session:
        products = await get_all_products(session)
    
    if not products:
        await callback.message.edit_text(
            "📦 No products available to edit.\n"
            "Add some products first!",
            reply_markup=get_admin_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "✏️ <b>Edit Product</b>\n\n"
            "Select a product to edit:",
            reply_markup=get_product_edit_keyboard(products)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("product_edit_"))
async def edit_product_menu(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Product not found!", show_alert=True)
        return
    
    await state.update_data(product_id=product_id)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Edit Name", callback_data=f"edit_name_{product_id}")],
            [InlineKeyboardButton(text="💰 Edit Price", callback_data=f"edit_price_{product_id}")],
            [InlineKeyboardButton(text="🏷 Edit Type", callback_data=f"edit_type_{product_id}")],
            [InlineKeyboardButton(text="📄 Edit Description", callback_data=f"edit_desc_{product_id}")],
            [InlineKeyboardButton(text="🖼 Edit Image", callback_data=f"edit_image_{product_id}")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="admin_edit_product")]
        ]
    )
    
    await callback.message.edit_text(
        f"✏️ <b>Editing: {product.name}</b>\n\n"
        f"Current Price: ${product.price}\n"
        f"Current Type: {product.type}\n"
        f"Current Description: {product.description or 'No description'}\n"
        f"Current Image: {'Yes' if product.product_image else 'No image'}\n\n"
        "What would you like to edit?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_name_"))
async def edit_name_start(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(
        "✏️ <b>Edit Product Name</b>\n\n"
        "Please enter the new product name:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ProductStates.editing_name)
    await callback.answer()


@router.message(ProductStates.editing_name)
async def process_edit_name(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    
    async with async_session_maker() as session:
        product = await update_product(session, product_id, name=message.text)
    
    await message.answer(
        f"✅ <b>Product name updated!</b>\n\n"
        f"New name: {product.name}",
        reply_markup=get_admin_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_price_"))
async def edit_price_start(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(
        "✏️ <b>Edit Product Price</b>\n\n"
        "Please enter the new price (e.g., 10.99):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ProductStates.editing_price)
    await callback.answer()


@router.message(ProductStates.editing_price)
async def process_edit_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError()
        
        data = await state.get_data()
        product_id = data['product_id']
        
        async with async_session_maker() as session:
            product = await update_product(session, product_id, price=price)
        
        await message.answer(
            f"✅ <b>Product price updated!</b>\n\n"
            f"New price: ${product.price}",
            reply_markup=get_admin_panel_keyboard()
        )
        await state.clear()
    except ValueError:
        await message.answer(
            "❌ Invalid price! Please enter a valid number (e.g., 10.99):"
        )


@router.callback_query(F.data.startswith("edit_desc_"))
async def edit_description_start(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(
        "✏️ <b>Edit Product Description</b>\n\n"
        "Please enter the new description:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ProductStates.editing_description)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_type_"))
async def edit_type_start(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔻 Weight Loss", callback_data=f"edittype_weight_loss_{product_id}")],
            [InlineKeyboardButton(text="🔺 Weight Gain", callback_data=f"edittype_weight_gain_{product_id}")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_panel")]
        ]
    )
    
    await callback.message.edit_text(
        "✏️ <b>Edit Product Type</b>\n\n"
        "Please select the new product type:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edittype_"))
async def process_edit_type(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    product_type = "weight_loss" if parts[1] == "weight" and parts[2] == "loss" else "weight_gain"
    product_id = int(parts[-1])
    
    async with async_session_maker() as session:
        product = await update_product(session, product_id, product_type=product_type)
    
    await callback.message.edit_text(
        f"✅ <b>Product type updated!</b>\n\n"
        f"New type: {product.type}",
        reply_markup=get_admin_panel_keyboard()
    )
    await state.clear()
    await callback.answer()


@router.message(ProductStates.editing_description)
async def process_edit_description(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    
    async with async_session_maker() as session:
        product = await update_product(session, product_id, description=message.text)
    
    await message.answer(
        f"✅ <b>Product description updated!</b>\n\n"
        f"New description: {product.description}",
        reply_markup=get_admin_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_image_"))
async def edit_image_start(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(
        "✏️ <b>Edit Product Image</b>\n\n"
        "Please send the new product image (or send /skip to remove image):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ProductStates.editing_image)
    await callback.answer()


@router.message(ProductStates.editing_image, F.photo)
async def process_edit_image(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    
    photo = message.photo[-1]
    file_id = photo.file_id
    
    async with async_session_maker() as session:
        product = await update_product(session, product_id, product_image=file_id)
    
    await message.answer_photo(
        photo=file_id,
        caption=f"✅ <b>Product image updated!</b>\n\n"
                f"Product: {product.name}",
        reply_markup=get_admin_panel_keyboard()
    )
    await state.clear()


@router.message(ProductStates.editing_image, F.text == "/skip")
async def remove_product_image(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    
    async with async_session_maker() as session:
        product = await update_product(session, product_id, product_image=None)
    
    await message.answer(
        f"✅ <b>Product image removed!</b>\n\n"
        f"Product: {product.name}",
        reply_markup=get_admin_panel_keyboard()
    )
    await state.clear()


# DELETE PRODUCT
@router.callback_query(F.data == "admin_delete_product")
async def start_delete_product(callback: CallbackQuery):
    async with async_session_maker() as session:
        products = await get_all_products(session)
    
    if not products:
        await callback.message.edit_text(
            "📦 No products available to delete.",
            reply_markup=get_admin_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "🗑 <b>Delete Product</b>\n\n"
            "⚠️ Select a product to delete:",
            reply_markup=get_product_delete_keyboard(products)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("product_delete_"))
async def confirm_delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Product not found!", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"⚠️ <b>Confirm Deletion</b>\n\n"
        f"Are you sure you want to delete this product?\n\n"
        f"📦 Name: {product.name}\n"
        f"💰 Price: ${product.price}",
        reply_markup=get_confirm_delete_keyboard(product_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product_confirm_delete_"))
async def process_delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[3])
    
    async with async_session_maker() as session:
        success = await delete_product(session, product_id)
    
    if success:
        await callback.message.edit_text(
            "✅ <b>Product deleted successfully!</b>",
            reply_markup=get_admin_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ <b>Failed to delete product.</b>",
            reply_markup=get_admin_panel_keyboard()
        )
    await callback.answer()
