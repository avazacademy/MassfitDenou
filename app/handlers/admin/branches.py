from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.engine import async_session_maker
from app.database.branch_requests import (
    get_all_branches,
    get_branch_by_id,
    create_branch,
    update_branch,
    delete_branch
)
from app.keyboards.inline import (
    get_branches_panel_keyboard,
    get_branch_list_keyboard,
    get_branch_edit_keyboard,
    get_branch_delete_keyboard,
    get_branch_detail_keyboard,
    get_confirm_delete_branch_keyboard,
    get_cancel_keyboard
)

router = Router()


class BranchStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_location = State()
    waiting_for_description = State()
    waiting_for_image = State()
    editing_name = State()
    editing_location = State()
    editing_description = State()
    editing_image = State()


@router.callback_query(F.data == "admin_branches")
async def branches_panel(callback: CallbackQuery):
    text = (
        "🏢 <b>Filiallarni boshqarish</b>\n\n"
        "Bu yerda filiallaringizni boshqaring.\n"
        "Quyidagi variantlardan birini tanlang:"
    )
    
    # Check if current message has photo (no text to edit)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=get_branches_panel_keyboard())
    else:
        await callback.message.edit_text(text, reply_markup=get_branches_panel_keyboard())
    
    await callback.answer()


@router.callback_query(F.data == "admin_view_branches")
async def view_all_branches(callback: CallbackQuery):
    async with async_session_maker() as session:
        branches = await get_all_branches(session)
    
    if not branches:
        text = (
            "🏢 <b>Filiallar ro'yxati</b>\n\n"
            "Filiallar topilmadi. Birinchi filialingizni qo'shing!"
        )
        markup = get_branches_panel_keyboard()
    else:
        text = (
            f"🏢 <b>Filiallar ro'yxati</b>\n\n"
            f"Jami filiallar: {len(branches)}\n"
            "Batafsil ma'lumot olish uchun filialni tanlang:"
        )
        markup = get_branch_list_keyboard(branches)
    
    # Check if current message has photo (no text to edit)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=markup)
    else:
        await callback.message.edit_text(text, reply_markup=markup)
    
    await callback.answer()


@router.callback_query(F.data.startswith("branch_view_"))
async def view_branch_detail(callback: CallbackQuery):
    branch_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        branch = await get_branch_by_id(session, branch_id)
    
    if not branch:
        await callback.answer("Filial topilmadi!", show_alert=True)
        return
    
    no_desc = "Tavsif yo'q"
    no_img = "Rasm yo'q"
    has_img = "Ha"
    
    text = (
        f"🏢 <b>{branch.name}</b>\n\n"
        f"📝 Tavsif: {branch.description or no_desc}\n"
        f"📍 Joylashuv: {branch.location}\n"
        f"🖼 Rasm: {has_img if branch.image else no_img}\n\n"
        f"📅 Yaratilgan: {branch.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"🔄 Yangilangan: {branch.updated_at.strftime('%Y-%m-%d %H:%M')}"
    )
    
    if branch.image:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=branch.image,
            caption=text,
            reply_markup=get_branch_detail_keyboard(branch_id)
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_branch_detail_keyboard(branch_id)
        )
    await callback.answer()


# ADD BRANCH
@router.callback_query(F.data == "admin_add_branch")
async def start_add_branch(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "➕ <b>Yangi filial qo'shish</b>\n\n"
        "Iltimos, filial nomini kiriting:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(BranchStates.waiting_for_name)
    await callback.answer()


@router.message(BranchStates.waiting_for_name)
async def process_branch_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        f"✅ Filial nomi: <b>{message.text}</b>\n\n"
        "Endi joylashuvni kiriting (Google Maps havolasi yoki manzil):"
    )
    await state.set_state(BranchStates.waiting_for_location)


@router.message(BranchStates.waiting_for_location)
async def process_branch_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer(
        f"✅ Joylashuv saqlandi\n\n"
        "Endi filial tavsifini kiriting (yoki o'tkazib yuborish uchun /skip yuboring):"
    )
    await state.set_state(BranchStates.waiting_for_description)


@router.message(BranchStates.waiting_for_description)
async def process_branch_description(message: Message, state: FSMContext):
    description = None if message.text == "/skip" else message.text
    await state.update_data(description=description)
    
    await message.answer(
        f"✅ Tavsif: <b>{description or 'Otkazib yuborildi'}</b>\n\n"
        "Nihoyat, filial rasmini yuboring (yoki o'tkazib yuborish uchun /skip yuboring):"
    )
    await state.set_state(BranchStates.waiting_for_image)


@router.message(BranchStates.waiting_for_image, F.photo)
async def process_branch_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(image=file_id)
    
    data = await state.get_data()
    
    async with async_session_maker() as session:
        branch = await create_branch(
            session,
            name=data['name'],
            location=data['location'],
            description=data.get('description'),
            image=file_id
        )
    
    no_desc = "Tavsif yo'q"
    
    text = (
        f"✅ <b>Filial muvaffaqiyatli qo'shildi!</b>\n\n"
        f"🏢 Nomi: {branch.name}\n"
        f"📍 Joylashuv: {branch.location}\n"
        f"📝 Tavsif: {branch.description or no_desc}"
    )
    
    from app.keyboards.inline import get_branches_panel_keyboard
    await message.answer_photo(
        photo=file_id,
        caption=text,
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


@router.message(BranchStates.waiting_for_image, F.text == "/skip")
async def skip_branch_image(message: Message, state: FSMContext):
    data = await state.get_data()
    
    async with async_session_maker() as session:
        branch = await create_branch(
            session,
            name=data['name'],
            location=data['location'],
            description=data.get('description'),
            image=None
        )
    
    from app.keyboards.inline import get_branches_panel_keyboard
    
    no_desc = "Tavsif yo'q"
    
    await message.answer(
        f"✅ <b>Filial muvaffaqiyatli qo'shildi!</b>\n\n"
        f"🏢 Nomi: {branch.name}\n"
        f"📍 Joylashuv: {branch.location}\n"
        f"📝 Tavsif: {branch.description or no_desc}",
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


# EDIT BRANCH
@router.callback_query(F.data == "admin_edit_branch")
async def start_edit_branch(callback: CallbackQuery):
    async with async_session_maker() as session:
        branches = await get_all_branches(session)
    
    if not branches:
        await callback.message.edit_text(
            "🏢 Tahrirlash uchun filiallar mavjud emas.\n"
            "Avval filiallar qo'shing!",
            reply_markup=get_branches_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "✏️ <b>Filialni tahrirlash</b>\n\n"
            "Tahrirlash uchun filialni tanlang:",
            reply_markup=get_branch_edit_keyboard(branches)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("branch_edit_"))
async def edit_branch_menu(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        branch = await get_branch_by_id(session, branch_id)
    
    if not branch:
        await callback.answer("Filial topilmadi!", show_alert=True)
        return
    
    await state.update_data(branch_id=branch_id)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Nomni tahrirlash", callback_data=f"edit_branch_name_{branch_id}")],
            [InlineKeyboardButton(text="📍 Joylashuvni tahrirlash", callback_data=f"edit_branch_location_{branch_id}")],
            [InlineKeyboardButton(text="📄 Tavsifni tahrirlash", callback_data=f"edit_branch_desc_{branch_id}")],
            [InlineKeyboardButton(text="🖼 Rasmni tahrirlash", callback_data=f"edit_branch_image_{branch_id}")],
            [InlineKeyboardButton(text="🔙 Ortga", callback_data="admin_edit_branch")]
        ]
    )
    
    no_desc = "Tavsif yo'q"
    no_img = "Rasm yo'q"
    has_img = "Ha"
    
    text = (
        f"✏️ <b>Tahrirlanmoqda: {branch.name}</b>\n\n"
        f"Joriy joylashuv: {branch.location}\n"
        f"Joriy tavsif: {branch.description or no_desc}\n"
        f"Joriy rasm: {has_img if branch.image else no_img}\n\n"
        "Nimani tahrirlashni xohlaysiz?"
    )
    
    # Check if current message has photo (no text to edit)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=keyboard)
    else:
        await callback.message.edit_text(text, reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(F.data.startswith("edit_branch_name_"))
async def edit_branch_name_start(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[3])
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text(
        "✏️ <b>Filial nomini tahrirlash</b>\n\n"
        "Iltimos, yangi filial nomini kiriting:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(BranchStates.editing_name)
    await callback.answer()


@router.message(BranchStates.editing_name)
async def process_edit_branch_name(message: Message, state: FSMContext):
    data = await state.get_data()
    branch_id = data['branch_id']
    
    async with async_session_maker() as session:
        branch = await update_branch(session, branch_id, name=message.text)
    
    from app.keyboards.inline import get_branches_panel_keyboard
    await message.answer(
        f"✅ <b>Filial nomi yangilandi!</b>\n\n"
        f"Yangi nom: {branch.name}",
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_branch_location_"))
async def edit_branch_location_start(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[3])
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text(
        "✏️ <b>Filial joylashuvini tahrirlash</b>\n\n"
        "Iltimos, yangi joylashuvni kiriting:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(BranchStates.editing_location)
    await callback.answer()


@router.message(BranchStates.editing_location)
async def process_edit_branch_location(message: Message, state: FSMContext):
    data = await state.get_data()
    branch_id = data['branch_id']
    
    async with async_session_maker() as session:
        branch = await update_branch(session, branch_id, location=message.text)
    
    from app.keyboards.inline import get_branches_panel_keyboard
    await message.answer(
        f"✅ <b>Filial joylashuvi yangilandi!</b>\n\n"
        f"Yangi joylashuv: {branch.location}",
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_branch_desc_"))
async def edit_branch_description_start(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[3])
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text(
        "✏️ <b>Filial tavsifini tahrirlash</b>\n\n"
        "Iltimos, yangi tavsifni kiriting:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(BranchStates.editing_description)
    await callback.answer()


@router.message(BranchStates.editing_description)
async def process_edit_branch_description(message: Message, state: FSMContext):
    data = await state.get_data()
    branch_id = data['branch_id']
    
    async with async_session_maker() as session:
        branch = await update_branch(session, branch_id, description=message.text)
    
    from app.keyboards.inline import get_branches_panel_keyboard
    await message.answer(
        f"✅ <b>Filial tavsifi yangilandi!</b>\n\n"
        f"Yangi tavsif: {branch.description}",
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_branch_image_"))
async def edit_branch_image_start(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[3])
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text(
        "✏️ <b>Filial rasmini tahrirlash</b>\n\n"
        "Iltimos, yangi filial rasmini yuboring (yoki rasmni o'chirish uchun /skip yuboring):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(BranchStates.editing_image)
    await callback.answer()


@router.message(BranchStates.editing_image, F.photo)
async def process_edit_branch_image(message: Message, state: FSMContext):
    data = await state.get_data()
    branch_id = data['branch_id']
    
    photo = message.photo[-1]
    file_id = photo.file_id
    
    async with async_session_maker() as session:
        branch = await update_branch(session, branch_id, image=file_id)
    
    from app.keyboards.inline import get_branches_panel_keyboard
    await message.answer_photo(
        photo=file_id,
        caption=f"✅ <b>Filial rasmi yangilandi!</b>\n\n"
                f"Filial: {branch.name}",
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


@router.message(BranchStates.editing_image, F.text == "/skip")
async def remove_branch_image(message: Message, state: FSMContext):
    data = await state.get_data()
    branch_id = data['branch_id']
    
    async with async_session_maker() as session:
        branch = await update_branch(session, branch_id, image=None)
    
    from app.keyboards.inline import get_branches_panel_keyboard
    await message.answer(
        f"✅ <b>Filial rasmi o'chirildi!</b>\n\n"
        f"Filial: {branch.name}",
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


# DELETE BRANCH
@router.callback_query(F.data == "admin_delete_branch")
async def start_delete_branch(callback: CallbackQuery):
    async with async_session_maker() as session:
        branches = await get_all_branches(session)
    
    if not branches:
        await callback.message.edit_text(
            "🏢 O'chirish uchun filiallar mavjud emas.",
            reply_markup=get_branches_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "🗑 <b>Filialni o'chirish</b>\n\n"
            "⚠️ O'chirish uchun filialni tanlang:",
            reply_markup=get_branch_delete_keyboard(branches)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("branch_delete_"))
async def confirm_delete_branch(callback: CallbackQuery):
    branch_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        branch = await get_branch_by_id(session, branch_id)
    
    if not branch:
        await callback.answer("Filial topilmadi!", show_alert=True)
        return
    
    text = (
        f"⚠️ <b>O'chirishni tasdiqlang</b>\n\n"
        f"Ushbu filialni o'chirishni xohlaysizmi?\n\n"
        f"🏢 Nomi: {branch.name}\n"
        f"📍 Joylashuv: {branch.location}"
    )
    
    # Check if current message has photo (no text to edit)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=get_confirm_delete_branch_keyboard(branch_id))
    else:
        await callback.message.edit_text(text, reply_markup=get_confirm_delete_branch_keyboard(branch_id))
    
    await callback.answer()


@router.callback_query(F.data.startswith("branch_confirm_delete_"))
async def process_delete_branch(callback: CallbackQuery):
    branch_id = int(callback.data.split("_")[3])
    
    async with async_session_maker() as session:
        success = await delete_branch(session, branch_id)
    
    if success:
        await callback.message.edit_text(
            "✅ <b>Filial muvaffaqiyatli o'chirildi!</b>",
            reply_markup=get_branches_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ <b>Filialni o'chirish muvaffaqiyatsiz tugadi.</b>",
            reply_markup=get_branches_panel_keyboard()
        )
    await callback.answer()
