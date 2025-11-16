from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.database.models import BasketItem, Order, OrderItem, User, Product


# BASKET OPERATIONS
async def get_basket_items(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(BasketItem).where(BasketItem.user_id == user_id)
    )
    return result.scalars().all()


async def add_to_basket(session: AsyncSession, user_id: int, product_id: int, quantity: int = 1):
    # Check if item already exists
    result = await session.execute(
        select(BasketItem).where(
            BasketItem.user_id == user_id,
            BasketItem.product_id == product_id
        )
    )
    basket_item = result.scalar_one_or_none()
    
    if basket_item:
        basket_item.quantity = quantity
    else:
        basket_item = BasketItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        session.add(basket_item)
    
    await session.commit()
    await session.refresh(basket_item)
    return basket_item


async def update_basket_quantity(session: AsyncSession, user_id: int, product_id: int, quantity: int):
    if quantity < 1:
        # Remove from basket
        await session.execute(
            delete(BasketItem).where(
                BasketItem.user_id == user_id,
                BasketItem.product_id == product_id
            )
        )
        await session.commit()
        return None
    
    result = await session.execute(
        select(BasketItem).where(
            BasketItem.user_id == user_id,
            BasketItem.product_id == product_id
        )
    )
    basket_item = result.scalar_one_or_none()
    
    if basket_item:
        basket_item.quantity = quantity
        await session.commit()
        await session.refresh(basket_item)
        return basket_item
    return None


async def remove_from_basket(session: AsyncSession, user_id: int, product_id: int):
    await session.execute(
        delete(BasketItem).where(
            BasketItem.user_id == user_id,
            BasketItem.product_id == product_id
        )
    )
    await session.commit()


async def clear_basket(session: AsyncSession, user_id: int):
    await session.execute(delete(BasketItem).where(BasketItem.user_id == user_id))
    await session.commit()


# ORDER OPERATIONS
async def create_order(session: AsyncSession, user_id: int, total_price: float, delivery_type: str = None, 
                      branch_id: int = None, latitude: float = None, longitude: float = None, group_message_id: int = None):
    order = Order(
        user_id=user_id,
        total_price=total_price,
        status='waiting',
        delivery_type=delivery_type,
        branch_id=branch_id,
        delivery_latitude=latitude,
        delivery_longitude=longitude,
        group_message_id=group_message_id
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def create_order_item(session: AsyncSession, order_id: int, product_id: int, 
                           product_name: str, product_price: float, quantity: int):
    order_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        product_name=product_name,
        product_price=product_price,
        quantity=quantity
    )
    session.add(order_item)
    await session.commit()
    await session.refresh(order_item)
    return order_item


async def get_order_by_id(session: AsyncSession, order_id: int):
    result = await session.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def get_user_orders(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    return result.scalars().all()


async def update_order_status(session: AsyncSession, order_id: int, status: str):
    order = await get_order_by_id(session, order_id)
    if order:
        order.status = status
        await session.commit()
        await session.refresh(order)
    return order


async def get_order_items(session: AsyncSession, order_id: int):
    result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    return result.scalars().all()


async def get_user_by_id(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_basket_items_with_products(session, user_id: int):
    result = await session.execute(
        select(BasketItem)
        .options(joinedload(BasketItem.product))
        .where(BasketItem.user_id == user_id)
    )
    return result.scalars().all()
