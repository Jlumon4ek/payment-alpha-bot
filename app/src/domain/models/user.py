from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger
from .base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, 
        nullable=False, 
        unique=True
    )
    username: Mapped[str] = mapped_column(
        String, 
        nullable=True
    )
    full_name: Mapped[str] = mapped_column(
        String, 
        nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<User("
            f"telegram_id={self.telegram_id}, "
            f")>"
        )