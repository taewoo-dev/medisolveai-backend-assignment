"""
Admin App - Treatment 모델

관리자가 진료 항목 정보를 관리할 때 사용하는 모델
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Numeric, String, Text, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.orm import BaseModel, TimestampMixin
from app.dtos.treatment import TreatmentSummaryData

if TYPE_CHECKING:
    from app.models.appointment import Appointment


class Treatment(BaseModel, TimestampMixin):
    """진료 항목 모델 (관리자용)"""

    __tablename__ = "treatments"

    # 기본 정보
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="진료항목명")
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, comment="소요시간 (30분 단위)")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="가격")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="진료항목 설명")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="활성 상태")

    # 관계 설정 (Admin App에서는 예약과의 관계 필요)
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="treatment", lazy="select")

    @classmethod
    async def create_one(
        cls,
        session: AsyncSession,
        *,
        name: str,
        duration_minutes: int,
        price: Decimal,
        description: str | None = None,
        is_active: bool = True,
    ) -> Treatment:
        treatment = cls(
            name=name,
            duration_minutes=duration_minutes,
            price=price,
            description=description,
            is_active=is_active,
        )
        session.add(treatment)
        await session.flush()
        await session.refresh(treatment)
        return treatment

    @classmethod
    async def get_by_id(cls, session: AsyncSession, treatment_id: int) -> Treatment | None:
        return await session.get(cls, treatment_id)

    @classmethod
    async def get_filtered(
        cls,
        session: AsyncSession,
        *,
        is_active: bool | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[TreatmentSummaryData]:
        query = select(
            cls.id,
            cls.name,
            cls.duration_minutes,
            cls.price,
            cls.is_active,
        )

        if is_active is not None:
            query = query.where(cls.is_active == is_active)

        query = query.order_by(cls.id.asc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        result = await session.execute(query)
        rows = result.all()
        return [
            TreatmentSummaryData(
                id=row.id,
                name=row.name,
                duration_minutes=row.duration_minutes,
                price=row.price,
                is_active=row.is_active,
            )
            for row in rows
        ]

    @classmethod
    async def update_fields(
        cls,
        session: AsyncSession,
        treatment_id: int,
        *,
        name: str | None = None,
        duration_minutes: int | None = None,
        price: Decimal | None = None,
        description: str | None = None,
    ) -> None:
        values = {
            key: value
            for key, value in {
                "name": name,
                "duration_minutes": duration_minutes,
                "price": price,
                "description": description,
            }.items()
            if value is not None
        }

        if not values:
            return

        query = update(cls).where(cls.id == treatment_id).values(**values)
        await session.execute(query)

    @classmethod
    async def set_active(
        cls,
        session: AsyncSession,
        treatment_id: int,
        *,
        is_active: bool,
    ) -> None:
        query = update(cls).where(cls.id == treatment_id).values(is_active=is_active)
        await session.execute(query)
