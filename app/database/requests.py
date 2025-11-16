from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User


async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, tg_id: int, username: str = None, 
                     first_name: str = None, last_name: str = None, 
                     full_name: str = None, phone_number: str = None) -> User:
    user = User(
        tg_id=tg_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        phone_number=phone_number
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_phone(session: AsyncSession, tg_id: int, phone_number: str) -> User:
    user = await get_user_by_tg_id(session, tg_id)
    if user:
        user.phone_number = phone_number
        await session.commit()
        await session.refresh(user)
    return user
