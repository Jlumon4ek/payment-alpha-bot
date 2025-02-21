from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import String, Integer, Float, BigInteger, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from .base import BaseModel

class Subscription(BaseModel):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey('users.telegram_id'), 
        nullable=False
    )
    subscription_type: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )
    subscription_start: Mapped[datetime] = mapped_column(
        TIMESTAMP, 
        nullable=False, 
        default=func.now()
    )
    subscription_end: Mapped[datetime] = mapped_column(
        TIMESTAMP, 
        nullable=False
    )
    subscription_price: Mapped[float] = mapped_column(
        Float, 
        nullable=False
    )
    isActive: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=True
    )

    @validates('subscription_type')
    def validate_subscription_type(self, key, subscription_type):
        valid_types = ['day', 'month']
        if subscription_type not in valid_types:
            raise ValueError(f'Invalid subscription type. Must be one of: {valid_types}')
        return subscription_type