"""
Patient App - Treatment 모델

환자가 진료 항목 정보를 조회할 때 사용하는 모델
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.orm import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from .appointment import Appointment


class Treatment(BaseModel, TimestampMixin):
    """병원에서 제공하는 진료/시술 메뉴"""

    __tablename__ = "treatments"

    # 기본 정보
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="진료항목명")
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, comment="소요시간 (30분 단위)")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="가격")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="진료항목 설명")
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="활성 상태 (예약 생성 시 비활성 진료 항목은 사용 불가)"
    )

    # 관계 설정 (Patient App에서는 예약과의 관계만 필요)
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="treatment", lazy="select")

    @classmethod
    async def get_by_id(cls, session: AsyncSession, treatment_id: int) -> Treatment | None:
        """ID로 진료 항목 조회"""
        from sqlalchemy import select

        query = select(cls).where(cls.id == treatment_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
