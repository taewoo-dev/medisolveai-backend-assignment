"""
Patient App - Appointment 모델

환자의 예약 정보를 관리하는 모델
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Text, cast, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants.appointment_status import AppointmentStatus
from app.core.constants.visit_type import VisitType
from app.core.database.orm import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.dtos.appointment import AppointmentWithTreatmentData

    from .doctor import Doctor
    from .patient import Patient
    from .treatment import Treatment


class Appointment(BaseModel, TimestampMixin):
    """예약 정보 모델"""

    __tablename__ = "appointments"

    # 외래키
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False, comment="담당 의사")
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False, comment="환자")
    treatment_id: Mapped[int] = mapped_column(ForeignKey("treatments.id"), nullable=False, comment="진료항목")

    # 예약 정보
    appointment_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="예약 시작 일시")
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.PENDING, comment="예약 상태"
    )
    visit_type: Mapped[VisitType] = mapped_column(Enum(VisitType), nullable=False, comment="초진/재진")
    memo: Mapped[str | None] = mapped_column(Text, nullable=True, comment="예약 메모")

    # 관계 설정
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments", lazy="joined")
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments", lazy="joined")
    treatment: Mapped["Treatment"] = relationship("Treatment", back_populates="appointments", lazy="joined")

    @property
    def appointment_end_datetime(self) -> datetime:
        """예약 종료 시간 계산 (시작 시간 + 진료 소요 시간)"""
        from datetime import timedelta

        return self.appointment_datetime + timedelta(minutes=self.treatment.duration_minutes)

    @property
    def is_completed(self) -> bool:
        """완료된 예약인지 확인"""
        return self.status == AppointmentStatus.COMPLETED

    @property
    def is_active(self) -> bool:
        """활성 예약인지 확인 (취소되지 않은 예약)"""
        return self.status != AppointmentStatus.CANCELLED

    @classmethod
    async def create_one(
        cls,
        session: AsyncSession,
        patient_id: int,
        doctor_id: int,
        treatment_id: int,
        appointment_datetime: datetime,
        visit_type: VisitType,
        memo: str | None = None,
    ) -> Appointment:
        """예약 생성"""
        appointment = cls(
            patient_id=patient_id,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            appointment_datetime=appointment_datetime,
            visit_type=visit_type,
            memo=memo,
            status=AppointmentStatus.PENDING,
        )
        session.add(appointment)
        await session.flush()
        await session.refresh(appointment)
        return appointment

    @classmethod
    async def get_active_by_doctor_with_treatment(
        cls,
        session: AsyncSession,
        doctor_id: int,
        appointment_date: date | None = None,
    ) -> list[AppointmentWithTreatmentData]:
        """의사의 취소되지 않은 예약과 진료 항목 조회"""
        from app.dtos.appointment import AppointmentWithTreatmentData
        from app.models.treatment import Treatment

        query = (
            select(cls, Treatment)
            .join(Treatment, cls.treatment_id == Treatment.id)
            .where(
                cls.doctor_id == doctor_id,
                cls.status != AppointmentStatus.CANCELLED,
            )
        )

        # 날짜 필터링 추가
        if appointment_date is not None:
            query = query.where(cast(cls.appointment_datetime, Date) == appointment_date)

        result = await session.execute(query)
        rows = result.all()
        return [
            AppointmentWithTreatmentData(
                appointment_id=appointment.id,
                doctor_id=appointment.doctor_id,
                appointment_datetime=appointment.appointment_datetime,
                treatment_duration_minutes=treatment.duration_minutes,
            )
            for appointment, treatment in rows
        ]

    @classmethod
    async def get_active_with_treatment(
        cls,
        session: AsyncSession,
        appointment_date: date | None = None,
    ) -> list[AppointmentWithTreatmentData]:
        """취소되지 않은 예약과 진료 항목 조회"""
        from app.dtos.appointment import AppointmentWithTreatmentData
        from app.models.treatment import Treatment

        query = (
            select(cls, Treatment)
            .join(Treatment, cls.treatment_id == Treatment.id)
            .where(cls.status != AppointmentStatus.CANCELLED)
        )

        # 날짜 필터링 추가
        if appointment_date is not None:
            query = query.where(cast(cls.appointment_datetime, Date) == appointment_date)

        result = await session.execute(query)
        rows = result.all()
        return [
            AppointmentWithTreatmentData(
                appointment_id=appointment.id,
                doctor_id=appointment.doctor_id,
                appointment_datetime=appointment.appointment_datetime,
                treatment_duration_minutes=treatment.duration_minutes,
            )
            for appointment, treatment in rows
        ]

    @classmethod
    async def get_by_patient_phone(
        cls,
        session: AsyncSession,
        patient_phone: str,
    ) -> list[Appointment]:
        """환자 전화번호로 예약 목록 조회 (최신순)"""
        from app.models.patient import Patient

        query = (
            select(cls)
            .join(Patient, cls.patient_id == Patient.id)
            .where(Patient.phone == patient_phone)
            .order_by(cls.appointment_datetime.desc())
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def get_by_id_and_patient_phone(
        cls,
        session: AsyncSession,
        appointment_id: int,
        patient_phone: str,
    ) -> "Appointment | None":
        """예약 ID와 환자 전화번호로 예약 조회 (본인 확인용)"""
        from app.models.patient import Patient

        query = (
            select(cls)
            .join(Patient, cls.patient_id == Patient.id)
            .where(cls.id == appointment_id, Patient.phone == patient_phone)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def cancel(self, session: AsyncSession) -> None:
        """예약 취소 (소프트 삭제)"""
        if self.status == AppointmentStatus.CANCELLED:
            from app.core.constants.error_messages import ErrorMessages
            from app.core.exceptions import MediSolveAiException

            raise MediSolveAiException(ErrorMessages.APPOINTMENT_ALREADY_CANCELLED)

        self.status = AppointmentStatus.CANCELLED
        await session.flush()
