"""
Patient App - Doctor 모델

환자가 의사 정보를 조회할 때 사용하는 모델
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.orm import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from .appointment import Appointment


class Doctor(BaseModel, TimestampMixin):
    """병원에서 근무하는 의사의 기본 정보"""

    __tablename__ = "doctors"

    # 기본 정보
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="의사 이름")
    department: Mapped[str] = mapped_column(String(50), nullable=False, comment="진료과")
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="활성 상태 (예약 생성 시 비활성 의사는 사용 불가)"
    )

    # 관계 설정 (Patient App에서는 예약과의 관계만 필요)
    appointments: Mapped[list[Appointment]] = relationship("Appointment", back_populates="doctor", lazy="select")

    @classmethod
    async def create_one(
        cls,
        session: AsyncSession,
        name: str,
        department: str,
        is_active: bool = True,
    ) -> Doctor:
        """의사 생성"""
        doctor = cls(name=name, department=department, is_active=is_active)
        session.add(doctor)
        await session.flush()
        await session.refresh(doctor)
        return doctor

    @classmethod
    async def create_bulk(
        cls,
        session: AsyncSession,
        doctors_data: list[dict[str, str | bool]],
    ) -> list[Doctor]:
        """의사 일괄 생성"""
        doctors = [
            cls(name=data["name"], department=data["department"], is_active=data.get("is_active", True))
            for data in doctors_data
        ]
        session.add_all(doctors)
        await session.flush()
        for doctor in doctors:
            await session.refresh(doctor)
        return doctors

    @classmethod
    async def get_by_id(cls, session: AsyncSession, doctor_id: int) -> Doctor | None:
        """ID로 의사 조회"""
        query = select(cls).where(cls.id == doctor_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_active_doctors(cls, session: AsyncSession, department: str | None = None) -> list[Doctor]:
        """활성 의사 목록 조회"""
        query = select(cls).where(cls.is_active)

        if department:
            query = query.where(cls.department == department)

        query = query.order_by(cls.name)

        result = await session.execute(query)
        return list(result.scalars().all())
