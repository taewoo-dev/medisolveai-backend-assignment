"""SQLAlchemy ORM 기본 설정"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy Base 클래스"""

    # 타입 어노테이션 맵핑
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }


class TimestampMixin:
    """생성/수정 시간 자동 관리 Mixin"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="생성 시간"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정 시간"
    )


class BaseModel(Base):
    """기본 모델 클래스 (모든 테이블의 부모)"""

    __abstract__ = True

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="기본키")
