from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import String, Integer, Float, BigInteger, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from .base import BaseModel
from .user import User
from sqlalchemy.orm import relationship

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

    notified_24: Mapped[bool] = mapped_column(
        Boolean, 
        default=False
    )
    notified_1: Mapped[bool] = mapped_column(
        Boolean, 
        default=False
    )

    user = relationship("User", foreign_keys=[telegram_id])

    @validates('subscription_type')
    def validate_subscription_type(self, key, subscription_type):
        valid_types = ['day', 'month']
        if subscription_type not in valid_types:
            raise ValueError(f'Invalid subscription type. Must be one of: {valid_types}')
        return subscription_type

    def __repr__(self) -> str:
        return (
            f"<Subscription("
            f"telegram_id={self.telegram_id}, "
            f"isActive={self.isActive}, "
            f")>"
        )