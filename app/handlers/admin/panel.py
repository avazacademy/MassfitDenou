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
        await message.answer("⛔️ Sizda admin panelga kirish huquqi yo'q.")
        return
    
    await message.answer(
        "🔐 <b>Admin Panelga xush kelibsiz</b>\n\n"
        "Bu yerda siz mahsulotlarni boshqarishingiz va statistikani ko'rishingiz mumkin.\n"
        "Quyidagi variantlardan birini tanlang:",
        reply_markup=get_admin_panel_keyboard()
    )


@router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🔐 <b>Admin Panelga xush kelibsiz</b>\n\n"
        "Bu yerda siz mahsulotlarni boshqarishingiz va statistikani ko'rishingiz mumkin.\n"
        "Quyidagi variantlardan birini tanlang:"
    )
    
    # Check if current message has photo (no text to edit)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=get_admin_panel_keyboard())
    else:
        await callback.message.edit_text(text, reply_markup=get_admin_panel_keyboard())
    
    await callback.answer()


@router.callback_query(F.data == "admin_back_main")
async def admin_back_to_main(callback: CallbackQuery):
    from app.handlers.start import show_main_menu
    await callback.message.delete()
    await show_main_menu(callback.message)
    await callback.answer()
