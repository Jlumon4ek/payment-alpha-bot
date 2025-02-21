from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, BigInteger, ForeignKey, TIMESTAMP
from .base import BaseModel

class Payment(BaseModel):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey('users.telegram_id', ondelete='SET NULL'), 
        nullable=False
    )
    store_name: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )
    receipt_id: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )
    payment_date: Mapped[datetime] = mapped_column(
        TIMESTAMP, 
        nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )
    passport_id: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )
    price: Mapped[float] = mapped_column(
        Float, 
        nullable=False
    )