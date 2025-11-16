from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Product


async def get_all_products(session: AsyncSession):
    result = await session.execute(select(Product).order_by(Product.created_at.desc()))
    return result.scalars().all()


async def get_products_by_type(session: AsyncSession, product_type: str):
    result = await session.execute(
        select(Product).where(Product.type == product_type).order_by(Product.created_at.desc())
    )
    return result.scalars().all()


async def get_product_by_id(session: AsyncSession, product_id: int) -> Product | None:
    result = await session.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def create_product(session: AsyncSession, name: str, price: float, product_type: str, description: str = None, product_image: str = None) -> Product:
    product = Product(
        name=name,
        price=price,
        type=product_type,
        description=description,
        product_image=product_image
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def update_product(session: AsyncSession, product_id: int, name: str = None, 
                        price: float = None, description: str = None, product_type: str = None, product_image: str = None) -> Product:
    product = await get_product_by_id(session, product_id)
    if product:
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if description is not None:
            product.description = description
        if product_type is not None:
            product.type = product_type
        if product_image is not None:
            product.product_image = product_image
        await session.commit()
        await session.refresh(product)
    return product


async def delete_product(session: AsyncSession, product_id: int) -> bool:
    result = await session.execute(delete(Product).where(Product.id == product_id))
    await session.commit()
    return result.rowcount > 0
