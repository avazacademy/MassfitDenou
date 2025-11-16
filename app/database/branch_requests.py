from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Branch


async def get_all_branches(session: AsyncSession):
    result = await session.execute(select(Branch).order_by(Branch.created_at.desc()))
    return result.scalars().all()


async def get_branch_by_id(session: AsyncSession, branch_id: int) -> Branch | None:
    result = await session.execute(select(Branch).where(Branch.id == branch_id))
    return result.scalar_one_or_none()


async def create_branch(session: AsyncSession, name: str, location: str, description: str = None, image: str = None) -> Branch:
    branch = Branch(
        name=name,
        location=location,
        description=description,
        image=image
    )
    session.add(branch)
    await session.commit()
    await session.refresh(branch)
    return branch


async def update_branch(session: AsyncSession, branch_id: int, name: str = None, 
                       location: str = None, description: str = None, image: str = None) -> Branch:
    branch = await get_branch_by_id(session, branch_id)
    if branch:
        if name is not None:
            branch.name = name
        if location is not None:
            branch.location = location
        if description is not None:
            branch.description = description
        if image is not None:
            branch.image = image
        await session.commit()
        await session.refresh(branch)
    return branch


async def delete_branch(session: AsyncSession, branch_id: int) -> bool:
    result = await session.execute(delete(Branch).where(Branch.id == branch_id))
    await session.commit()
    return result.rowcount > 0
