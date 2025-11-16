from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.keyboards.inline import get_admin_panel_keyboard
from app.config import ADMIN_ID

router = Router()


@router.message(Command('admin'))
async def cmd_admin(message: Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        await message.answer("⛔️ You don't have permission to access the admin panel.")
        return
    
    await message.answer(
        "🔐 <b>Welcome to the Admin Panel</b>\n\n"
        "Here you can manage products and view statistics.\n"
        "Choose an option below:",
        reply_markup=get_admin_panel_keyboard()
    )


@router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🔐 <b>Welcome to the Admin Panel</b>\n\n"
        "Here you can manage products and view statistics.\n"
        "Choose an option below:",
        reply_markup=get_admin_panel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_back_main")
async def admin_back_to_main(callback: CallbackQuery):
    from app.handlers.start import show_main_menu
    await callback.message.delete()
    await show_main_menu(callback.message)
    await callback.answer()
