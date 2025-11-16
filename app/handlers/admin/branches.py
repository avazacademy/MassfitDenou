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
    await callback.message.edit_text(
        "🏢 <b>Branches Management</b>\n\n"
        "Manage your branches here.\n"
        "Choose an option below:",
        reply_markup=get_branches_panel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_view_branches")
async def view_all_branches(callback: CallbackQuery):
    async with async_session_maker() as session:
        branches = await get_all_branches(session)
    
    if not branches:
        await callback.message.edit_text(
            "🏢 <b>Branches List</b>\n\n"
            "No branches found. Add your first branch!",
            reply_markup=get_branches_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            f"🏢 <b>Branches List</b>\n\n"
            f"Total branches: {len(branches)}\n"
            "Select a branch to view details:",
            reply_markup=get_branch_list_keyboard(branches)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("branch_view_"))
async def view_branch_detail(callback: CallbackQuery):
    branch_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        branch = await get_branch_by_id(session, branch_id)
    
    if not branch:
        await callback.answer("Branch not found!", show_alert=True)
        return
    
    text = (
        f"🏢 <b>{branch.name}</b>\n\n"
        f"📝 Description: {branch.description or 'No description'}\n"
        f"📍 Location: {branch.location}\n"
        f"🖼 Image: {'Yes' if branch.image else 'No image'}\n\n"
        f"📅 Created: {branch.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"🔄 Updated: {branch.updated_at.strftime('%Y-%m-%d %H:%M')}"
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
        "➕ <b>Add New Branch</b>\n\n"
        "Please enter the branch name:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(BranchStates.waiting_for_name)
    await callback.answer()


@router.message(BranchStates.waiting_for_name)
async def process_branch_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        f"✅ Branch name: <b>{message.text}</b>\n\n"
        "Now enter the location (Google Maps link or address):"
    )
    await state.set_state(BranchStates.waiting_for_location)


@router.message(BranchStates.waiting_for_location)
async def process_branch_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer(
        f"✅ Location saved\n\n"
        "Now enter the branch description (or send /skip to skip):"
    )
    await state.set_state(BranchStates.waiting_for_description)


@router.message(BranchStates.waiting_for_description)
async def process_branch_description(message: Message, state: FSMContext):
    description = None if message.text == "/skip" else message.text
    await state.update_data(description=description)
    
    await message.answer(
        f"✅ Description: <b>{description or 'Skipped'}</b>\n\n"
        "Finally, send the branch image (or send /skip to skip):"
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
    
    text = (
        f"✅ <b>Branch Added Successfully!</b>\n\n"
        f"🏢 Name: {branch.name}\n"
        f"📍 Location: {branch.location}\n"
        f"📝 Description: {branch.description or 'No description'}"
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
    await message.answer(
        f"✅ <b>Branch Added Successfully!</b>\n\n"
        f"🏢 Name: {branch.name}\n"
        f"📍 Location: {branch.location}\n"
        f"📝 Description: {branch.description or 'No description'}",
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
            "🏢 No branches available to edit.\n"
            "Add some branches first!",
            reply_markup=get_branches_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "✏️ <b>Edit Branch</b>\n\n"
            "Select a branch to edit:",
            reply_markup=get_branch_edit_keyboard(branches)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("branch_edit_"))
async def edit_branch_menu(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        branch = await get_branch_by_id(session, branch_id)
    
    if not branch:
        await callback.answer("Branch not found!", show_alert=True)
        return
    
    await state.update_data(branch_id=branch_id)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Edit Name", callback_data=f"edit_branch_name_{branch_id}")],
            [InlineKeyboardButton(text="📍 Edit Location", callback_data=f"edit_branch_location_{branch_id}")],
            [InlineKeyboardButton(text="📄 Edit Description", callback_data=f"edit_branch_desc_{branch_id}")],
            [InlineKeyboardButton(text="🖼 Edit Image", callback_data=f"edit_branch_image_{branch_id}")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="admin_edit_branch")]
        ]
    )
    
    await callback.message.edit_text(
        f"✏️ <b>Editing: {branch.name}</b>\n\n"
        f"Current Location: {branch.location}\n"
        f"Current Description: {branch.description or 'No description'}\n"
        f"Current Image: {'Yes' if branch.image else 'No image'}\n\n"
        "What would you like to edit?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_branch_name_"))
async def edit_branch_name_start(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[3])
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text(
        "✏️ <b>Edit Branch Name</b>\n\n"
        "Please enter the new branch name:",
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
        f"✅ <b>Branch name updated!</b>\n\n"
        f"New name: {branch.name}",
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_branch_location_"))
async def edit_branch_location_start(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[3])
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text(
        "✏️ <b>Edit Branch Location</b>\n\n"
        "Please enter the new location:",
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
        f"✅ <b>Branch location updated!</b>\n\n"
        f"New location: {branch.location}",
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_branch_desc_"))
async def edit_branch_description_start(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[3])
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text(
        "✏️ <b>Edit Branch Description</b>\n\n"
        "Please enter the new description:",
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
        f"✅ <b>Branch description updated!</b>\n\n"
        f"New description: {branch.description}",
        reply_markup=get_branches_panel_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("edit_branch_image_"))
async def edit_branch_image_start(callback: CallbackQuery, state: FSMContext):
    branch_id = int(callback.data.split("_")[3])
    await state.update_data(branch_id=branch_id)
    await callback.message.edit_text(
        "✏️ <b>Edit Branch Image</b>\n\n"
        "Please send the new branch image (or send /skip to remove image):",
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
        caption=f"✅ <b>Branch image updated!</b>\n\n"
                f"Branch: {branch.name}",
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
        f"✅ <b>Branch image removed!</b>\n\n"
        f"Branch: {branch.name}",
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
            "🏢 No branches available to delete.",
            reply_markup=get_branches_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "🗑 <b>Delete Branch</b>\n\n"
            "⚠️ Select a branch to delete:",
            reply_markup=get_branch_delete_keyboard(branches)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("branch_delete_"))
async def confirm_delete_branch(callback: CallbackQuery):
    branch_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        branch = await get_branch_by_id(session, branch_id)
    
    if not branch:
        await callback.answer("Branch not found!", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"⚠️ <b>Confirm Deletion</b>\n\n"
        f"Are you sure you want to delete this branch?\n\n"
        f"🏢 Name: {branch.name}\n"
        f"📍 Location: {branch.location}",
        reply_markup=get_confirm_delete_branch_keyboard(branch_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("branch_confirm_delete_"))
async def process_delete_branch(callback: CallbackQuery):
    branch_id = int(callback.data.split("_")[3])
    
    async with async_session_maker() as session:
        success = await delete_branch(session, branch_id)
    
    if success:
        await callback.message.edit_text(
            "✅ <b>Branch deleted successfully!</b>",
            reply_markup=get_branches_panel_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ <b>Failed to delete branch.</b>",
            reply_markup=get_branches_panel_keyboard()
        )
    await callback.answer()
