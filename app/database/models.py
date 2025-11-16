from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Numeric, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AbstractBaseModel(Base):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class User(AbstractBaseModel):
    __tablename__ = 'users'
    
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(512), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    
    orders = relationship("Order", back_populates="user", lazy="selectin")
    basket_items = relationship("BasketItem", back_populates="user", cascade="all, delete-orphan", lazy="selectin")


class Product(AbstractBaseModel):
    __tablename__ = 'products'
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    product_image: Mapped[str] = mapped_column(String(255), nullable=True)


class Branch(AbstractBaseModel):
    __tablename__ = 'branches'
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(500), nullable=False)


class BasketItem(AbstractBaseModel):
    __tablename__ = 'basket_items'
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    user = relationship("User", back_populates="basket_items", lazy="selectin")
    product = relationship("Product", lazy="selectin")


class Order(AbstractBaseModel):
    __tablename__ = 'orders'
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='waiting', nullable=False)
    group_message_id: Mapped[int] = mapped_column(Integer, nullable=True)
    delivery_type: Mapped[str] = mapped_column(String(50), nullable=True)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    delivery_latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)
    delivery_longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)
    
    user = relationship("User", back_populates="orders", lazy="selectin")
    branch = relationship("Branch", lazy="selectin")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin")


class OrderItem(AbstractBaseModel):
    __tablename__ = 'order_items'
    
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    order = relationship("Order", back_populates="order_items", lazy="selectin")
    product = relationship("Product", lazy="selectin")
