"""
Admin App - Doctor 모델

관리자가 의사 정보를 관리할 때 사용하는 모델
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.orm import BaseModel, TimestampMixin
from app.dtos.doctor import DoctorSummaryData

if TYPE_CHECKING:
    from app.models.appointment import Appointment


class Doctor(BaseModel, TimestampMixin):
    """의사 정보 모델 (관리자용)"""

    __tablename__ = "doctors"

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="의사 이름")
    department: Mapped[str] = mapped_column(String(50), nullable=False, comment="진료과")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="활성 상태")

    appointments: Mapped[list[Appointment]] = relationship("Appointment", back_populates="doctor", lazy="select")

    # -------------------------------------------------------------------------
    # ORM 편의 메서드
    # -------------------------------------------------------------------------
    @classmethod
    async def create_one(
        cls,
        session: AsyncSession,
        *,
        name: str,
        department: str,
        is_active: bool = True,
    ) -> Doctor:
        doctor = cls(name=name, department=department, is_active=is_active)
        session.add(doctor)
        await session.flush()
        await session.refresh(doctor)
        return doctor

    @classmethod
    async def get_by_id(cls, session: AsyncSession, doctor_id: int) -> Doctor | None:
        return await session.get(cls, doctor_id)

    @classmethod
    async def get_filtered(
        cls,
        session: AsyncSession,
        *,
        department: str | None = None,
        is_active: bool | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[DoctorSummaryData]:
        query = select(
            cls.id,
            cls.name,
            cls.department,
            cls.is_active,
        )

        if department is not None:
            query = query.where(cls.department == department)
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
            DoctorSummaryData(
                id=row.id,
                name=row.name,
                department=row.department,
                is_active=row.is_active,
            )
            for row in rows
        ]

    @classmethod
    async def update_fields(
        cls,
        session: AsyncSession,
        doctor_id: int,
        *,
        name: str | None = None,
        department: str | None = None,
    ) -> None:
        values = {
            key: value
            for key, value in {
                "name": name,
                "department": department,
            }.items()
            if value is not None
        }

        if not values:
            return

        query = update(cls).where(cls.id == doctor_id).values(**values)
        await session.execute(query)

    @classmethod
    async def set_active(
        cls,
        session: AsyncSession,
        doctor_id: int,
        *,
        is_active: bool,
    ) -> None:
        query = update(cls).where(cls.id == doctor_id).values(is_active=is_active)
        await session.execute(query)

    @classmethod
    async def delete_one(cls, session: AsyncSession, doctor_id: int) -> None:
        query = delete(cls).where(cls.id == doctor_id)
        await session.execute(query)
