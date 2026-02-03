from sqlalchemy import String, CHAR
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from .base import Base
from sqlalchemy.orm import DeclarativeBase
import uuid
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        primary_key=True,
        comment="用户UUID",
        default=uuid.uuid4,
        index=True
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="用户名（如：嵌入式协会）"
    )
    account_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        comment="账户名"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希值（bcrypt加密）"
    )

    def __repr__(self):
        return f"User(user_id={self.user_id}, username={self.username}, account_name={self.account_name})"