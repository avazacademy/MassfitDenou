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
        text = (
            "📦 <b>Mahsulotlar ro'yxati</b>\n\n"
            "Mahsulotlar topilmadi. Birinchi mahsulotingizni qo'shing!"
        )
        markup = get_admin_panel_keyboard()
    else:
        text = (
            f"📦 <b>Mahsulotlar ro'yxati</b>\n\n"
            f"Jami mahsulotlar: {len(products)}\n"
            "Batafsil ma'lumot olish uchun mahsulotni tanlang:"
        )
        markup = get_product_list_keyboard(products)
    
    # Check if current message has photo (no text to edit)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=markup)
    else:
        await callback.message.edit_text(text, reply_markup=markup)
    
    await callback.answer()


@router.callback_query(F.data.startswith("product_view_"))
async def view_product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    
    no_desc = 'Tavsif yo\'q'
    no_img = 'Rasm yo\'q'
    has_img = 'Ha'
    
    text = (
        f"📦 <b>{product.name}</b>\n\n"
        f"💰 Narxi: {product.price} so'm\n"
        f"🏷 Turi: {product.type}\n"
        f"📝 Tavsif: {product.description or no_desc}\n"
        f"🖼 Rasm: {has_img if product.product_image else no_img}\n\n"
        f"📅 Yaratilgan: {product.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"🔄 Yangilangan: {product.updated_at.strftime('%Y-%m-%d %H:%M')}"
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
        "➕ <b>Yangi mahsulot qo'shish</b>\n\n"
        "Iltimos, mahsulot nomini kiriting:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ProductStates.waiting_for_name)
    await callback.answer()


@router.message(ProductStates.waiting_for_name)
async def process_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        f"✅ Mahsulot nomi: <b>{message.text}</b>\n\n"
        "Endi mahsulot narxini kiriting (faqat raqamlar, masalan, 10.99):"
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
            f"✅ Narxi: <b>{price} so'm</b>\n\n"
            "Endi mahsulot turini tanlang:",
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
        f"✅ Turi: <b>{product_type.replace('_', ' ').title()}</b>\n\n"
        "Endi mahsulot tavsifini kiriting (yoki o'tkazib yuborish uchun /skip yuboring):"
    )
    await state.set_state(ProductStates.waiting_for_description)
    await callback.answer()


@router.message(ProductStates.waiting_for_description)
async def process_product_description(message: Message, state: FSMContext):
    description = None if message.text == "/skip" else message.text
    await state.update_data(description=description)
    
    await message.answer(f"✅ Tavsif: <b>{description or 'Otkazib yuborildi'}</b>\n\nNihoyat, mahsulot rasmini yuboring (yoki o'tkazib yuborish uchun /skip yuboring):")
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
    no_desc = "Tavsif yo'q"
    text = (
        f"✅ <b>Mahsulot muvaffaqiyatli qo'shildi!</b>\n\n"
        f"📦 Nomi: {product.name}\n"
        f"💰 Narxi: {product.price} so'm\n"
        f"🏷 Turi: {product.type}\n"
        f"📝 Tavsif: {product.description or no_desc}"
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
    no_desc = "Tavsif yo'q"
    await message.answer(
        f"✅ <b>Mahsulot muvaffaqiyatli qo'shildi!</b>\n\n"
        f"📦 Nomi: {product.name}\n"
        f"💰 Narxi: {product.price} so'm\n"
        f"🏷 Turi: {product.type}\n"
        f"📝 Tavsif: {product.description or no_desc}",
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
            "📦 Tahrirlash uchun mahsulotlar mavjud emas.\n"
            "Avval mahsulotlar qo'shing!",
            reply_markup=get_admin_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "✏️ <b>Mahsulotni tahrirlash</b>\n\n"
            "Tahrirlash uchun mahsulotni tanlang:",
            reply_markup=get_product_edit_keyboard(products)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("product_edit_"))
async def edit_product_menu(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    
    await state.update_data(product_id=product_id)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Nomini tahrirlash", callback_data=f"edit_name_{product_id}")],
            [InlineKeyboardButton(text="💰 Narxini tahrirlash", callback_data=f"edit_price_{product_id}")],
            [InlineKeyboardButton(text="🏷 Turini tahrirlash", callback_data=f"edit_type_{product_id}")],
            [InlineKeyboardButton(text="📄 Tavsifni tahrirlash", callback_data=f"edit_desc_{product_id}")],
            [InlineKeyboardButton(text="🖼 Rasmni tahrirlash", callback_data=f"edit_image_{product_id}")],
            [InlineKeyboardButton(text="🔙 Ortga", callback_data="admin_edit_product")]
        ]
    )
    
    no_desc = "Tavsif yo'q"
    no_img = "Rasm yo'q"
    has_img = "Ha"
    
    text = (
        f"✏️ <b>Tahrirlanmoqda: {product.name}</b>\n\n"
        f"Joriy narx: {product.price} so'm\n"
        f"Joriy tur: {product.type}\n"
        f"Joriy tavsif: {product.description or no_desc}\n"
        f"Joriy rasm: {has_img if product.product_image else no_img}\n\n"
        "Nimani tahrirlashni xohlaysiz?"
    )
    
    # Check if current message has photo (no text to edit)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=keyboard)
    else:
        await callback.message.edit_text(text, reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(F.data.startswith("edit_name_"))
async def edit_name_start(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(
        "✏️ <b>Mahsulot nomini tahrirlash</b>\n\n"
        "Iltimos, yangi mahsulot nomini kiriting:",
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
        f"✅ <b>Mahsulot nomi yangilandi!</b>\n\n"
        f"Yangi nom: {product.name}",
        reply_markup=get_admin_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_price_"))
async def edit_price_start(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(
        "✏️ <b>Mahsulot narxini tahrirlash</b>\n\n"
        "Iltimos, yangi narxni kiriting (masalan, 10.99):",
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
            f"✅ <b>Mahsulot narxi yangilandi!</b>\n\n"
            f"Yangi narx: {product.price} so'm",
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
        "✏️ <b>Mahsulot tavsifini tahrirlash</b>\n\n"
        "Iltimos, yangi tavsifni kiriting:",
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
            [InlineKeyboardButton(text="🔻 Vazn yo'qotish", callback_data=f"edittype_weight_loss_{product_id}")],
            [InlineKeyboardButton(text="🔺 Vazn orttirish", callback_data=f"edittype_weight_gain_{product_id}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")]
        ]
    )
    
    await callback.message.edit_text(
        "✏️ <b>Mahsulot turini tahrirlash</b>\n\n"
        "Iltimos, yangi mahsulot turini tanlang:",
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
        f"✅ <b>Mahsulot turi yangilandi!</b>\n\n"
        f"Yangi tur: {product.type}",
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
        f"✅ <b>Mahsulot tavsifi yangilandi!</b>\n\n"
        f"Yangi tavsif: {product.description}",
        reply_markup=get_admin_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_image_"))
async def edit_image_start(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(product_id=product_id)
    await callback.message.edit_text(
        "✏️ <b>Mahsulot rasmini tahrirlash</b>\n\n"
        "Iltimos, yangi mahsulot rasmini yuboring (yoki rasmni o'chirish uchun /skip yuboring):",
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
        caption=f"✅ <b>Mahsulot rasmi yangilandi!</b>\n\n"
                f"Mahsulot: {product.name}",
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
        f"✅ <b>Mahsulot rasmi o'chirildi!</b>\n\n"
        f"Mahsulot: {product.name}",
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
            "📦 O'chirish uchun mahsulotlar mavjud emas.",
            reply_markup=get_admin_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "🗑 <b>Mahsulotni o'chirish</b>\n\n"
            "⚠️ O'chirish uchun mahsulotni tanlang:",
            reply_markup=get_product_delete_keyboard(products)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("product_delete_"))
async def confirm_delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        product = await get_product_by_id(session, product_id)
    
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    
    text = (
        f"⚠️ <b>O'chirishni tasdiqlash</b>\n\n"
        f"Ushbu mahsulotni o'chirishni xohlaysizmi?\n\n"
        f"📦 Nomi: {product.name}\n"
        f"💰 Narxi: {product.price} so'm"
    )
    
    # Check if current message has photo (no text to edit)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=get_confirm_delete_keyboard(product_id))
    else:
        await callback.message.edit_text(text, reply_markup=get_confirm_delete_keyboard(product_id))
    
    await callback.answer()


@router.callback_query(F.data.startswith("product_confirm_delete_"))
async def process_delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[3])
    
    async with async_session_maker() as session:
        success = await delete_product(session, product_id)
    
    if success:
        await callback.message.edit_text(
            "✅ <b>Mahsulot muvaffaqiyatli o'chirildi!</b>",
            reply_markup=get_admin_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ <b>Mahsulotni o'chirishda xatolik yuz berdi.</b>",
            reply_markup=get_admin_panel_keyboard()
        )
    await callback.answer()
