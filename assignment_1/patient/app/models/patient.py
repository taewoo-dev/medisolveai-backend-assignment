"""
Patient App - Patient 모델

환자 정보를 관리하는 모델
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.orm import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from .appointment import Appointment


class Patient(BaseModel, TimestampMixin):
    """예약을 진행하는 환자의 기본 정보"""

    __tablename__ = "patients"

    # 기본 정보
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="환자 이름")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, comment="연락처")

    # 관계 설정 (Patient App에서는 예약과의 관계만 필요)
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        lazy="select",
        order_by="Appointment.appointment_datetime.desc()",  # 최신 예약 순으로 정렬
    )

    @classmethod
    async def get_by_phone(cls, session: AsyncSession, phone: str) -> Patient | None:
        """전화번호로 환자 조회"""
        query = select(cls).where(cls.phone == phone)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_or_create(
        cls,
        session: AsyncSession,
        name: str,
        phone: str,
    ) -> Patient:
        """전화번호로 환자 조회 또는 생성"""
        patient = await cls.get_by_phone(session=session, phone=phone)
        if patient is None:
            patient = cls(name=name, phone=phone)
            session.add(patient)
            await session.flush()
            await session.refresh(patient)
        return patient

    async def has_completed_appointment(self, session: AsyncSession) -> bool:
        """완료된 예약이 있는지 확인"""
        from app.core.constants.appointment_status import AppointmentStatus
        from app.models.appointment import Appointment

        query = select(Appointment).where(
            Appointment.patient_id == self.id,
            Appointment.status == AppointmentStatus.COMPLETED,
        )
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None
