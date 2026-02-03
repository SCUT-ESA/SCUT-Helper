from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
class Base(DeclarativeBase):
    created_at:Mapped[datetime]= mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
        )
    updated_at:Mapped[datetime]= mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="修改时间"
        )