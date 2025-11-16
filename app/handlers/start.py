from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.database.engine import async_session_maker
from app.database.requests import get_user_by_tg_id, create_user, update_user_phone
from app.keyboards.reply import get_phone_keyboard, get_main_menu_keyboard
from app.keyboards.inline import get_admin_panel_keyboard
from app.config import ADMIN_ID

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    # Check if user is admin
    if str(message.from_user.id) == str(ADMIN_ID):
        await message.answer(
            "🔐 <b>Welcome to the Admin Panel</b>\n\n"
            "Here you can manage products and view statistics.\n"
            "Choose an option below:",
            reply_markup=get_admin_panel_keyboard()
        )
        return
    
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, message.from_user.id)
        
        if not user:
            # Create new user
            full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
            await create_user(
                session,
                tg_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                full_name=full_name
            )
            
            await message.answer(
                "Hello! Please enter your phone number. We need it so that we can contact you.",
                reply_markup=get_phone_keyboard()
            )
        elif not user.phone_number:
            # User exists but no phone number
            await message.answer(
                "Hello! Please enter your phone number. We need it so that we can contact you.",
                reply_markup=get_phone_keyboard()
            )
        else:
            # User exists with phone number - show main menu
            await show_main_menu(message)


@router.message(F.contact)
async def process_contact(message: Message):
    phone_number = message.contact.phone_number
    
    async with async_session_maker() as session:
        await update_user_phone(session, message.from_user.id, phone_number)
    
    await show_main_menu(message)


async def show_main_menu(message: Message):
    bot_description = (
        "🥗 <b>Welcome to MassFit - Your Personal Nutrition Assistant!</b>\n\n"
        "We are here to help you achieve your health and fitness goals through proper nutrition. "
        "Our bot provides personalized meal plans and expert recommendations tailored to your needs.\n\n"
        "✨ <b>What we offer:</b>\n"
        "• Custom meal plans for weight loss or muscle gain\n"
        "• Balanced nutrition recommendations\n"
        "• Healthy recipes and meal ideas\n"
        "• Professional dietary guidance\n"
        "• Track your orders and progress\n\n"
        "Choose your goal below to get started! 👇"
    )
    
    await message.answer(
        bot_description,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )
