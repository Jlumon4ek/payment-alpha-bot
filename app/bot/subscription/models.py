from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, BigInteger, Column, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.sql import func
import datetime
from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Subscription(AsyncAttrs, Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    subscription_type: Mapped[str] = mapped_column(String, nullable=False)
    subscription_start: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, default=func.now())
    subscription_end: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False)
    subscription_price: Mapped[float] = mapped_column(Float, nullable=False)
    isActive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    @validates('subscription_type')
    def validate_subscription_type(self, key, subscription_type):
        if subscription_type not in ['day', 'month']:
            raise ValueError('Invalid subscription type')
        return subscription_type


class Payments(AsyncAttrs, Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete='SET NULL'), nullable=False)
    store_name: Mapped[str] = mapped_column(String, nullable=False)
    receipt_id: Mapped[str] = mapped_column(String, nullable=False)
    payment_date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    passport_id: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
