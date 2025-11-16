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
            "🔐 <b>Admin Panelga xush kelibsiz</b>\n\n"
            "Bu yerda siz mahsulotlarni boshqarishingiz va statistikani ko'rishingiz mumkin.\n"
            "Quyidagi variantlardan birini tanlang:",
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
                "Assalomu alaykum! Iltimos, telefon raqamingizni yuboring. Bu siz bilan bog'lanishimiz uchun kerak.",
                reply_markup=get_phone_keyboard()
            )
        elif not user.phone_number:
            # User exists but no phone number
            await message.answer(
                "Assalomu alaykum! Iltimos, telefon raqamingizni yuboring. Bu siz bilan bog'lanishimiz uchun kerak.",
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
        "🥗 <b>MassFit - Shaxsiy ovqatlanish yordamchingizga xush kelibsiz!</b>\n\n"
        "Biz sizga to'g'ri ovqatlanish orqali salomatlik va fitnes maqsadlaringizga erishishda yordam beramiz. "
        "Bizning bot sizning ehtiyojlaringizga moslashtirilgan shaxsiy ovqatlanish rejalari va professional tavsiyalarni taqdim etadi.\n\n"
        "✨ <b>Biz taklif qilamiz:</b>\n"
        "• Vazn yo'qotish yoki mushak massasini oshirish uchun maxsus ovqatlanish rejalari\n"
        "• Muvozanatli ovqatlanish bo'yicha tavsiyalar\n"
        "• Sog'lom retseptlar va ovqatlanish g'oyalari\n"
        "• Professional parhez bo'yicha yo'riqnoma\n"
        "• Buyurtmalaringiz va taraqqiyotingizni kuzatish\n\n"
        "Boshlash uchun maqsadingizni tanlang! 👇"
    )
    
    await message.answer(
        bot_description,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )
