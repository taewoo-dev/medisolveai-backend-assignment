"""
Admin App - Appointment 모델

관리자가 예약 정보를 관리할 때 사용하는 모델
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants.appointment_status import AppointmentStatus
from app.core.constants.visit_type import VisitType
from app.core.database.orm import BaseModel, TimestampMixin
from app.dtos.appointment import (
    AppointmentDailyCountItem,
    AppointmentStatusCountItem,
    AppointmentSummaryData,
    AppointmentTimeslotCountItem,
    AppointmentVisitTypeCountItem,
)

if TYPE_CHECKING:
    from app.models.doctor import Doctor
    from app.models.patient import Patient
    from app.models.treatment import Treatment


class Appointment(BaseModel, TimestampMixin):
    """예약 정보 모델 (관리자용)"""

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

    @property
    def duration_minutes(self) -> int:
        """예약 소요 시간 (분)"""
        return self.treatment.duration_minutes

    def can_transition_to(self, new_status: AppointmentStatus) -> bool:
        """상태 전환 가능 여부 확인"""
        # 상태 전환 규칙: PENDING → CONFIRMED → COMPLETED 또는 CANCELLED
        valid_transitions = {
            AppointmentStatus.PENDING: [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED],
            AppointmentStatus.CONFIRMED: [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED],
            AppointmentStatus.COMPLETED: [],  # 완료된 예약은 상태 변경 불가
            AppointmentStatus.CANCELLED: [],  # 취소된 예약은 상태 변경 불가
        }

        return new_status in valid_transitions.get(self.status, [])

    @classmethod
    async def get_by_id(cls, session: AsyncSession, appointment_id: int) -> Appointment | None:
        return await session.get(cls, appointment_id)

    @classmethod
    async def update_status(
        cls,
        session: AsyncSession,
        appointment_id: int,
        *,
        status: AppointmentStatus,
    ) -> None:
        query = update(cls).where(cls.id == appointment_id).values(status=status)
        await session.execute(query)

    @classmethod
    async def get_filtered(
        cls,
        session: AsyncSession,
        *,
        page: int,
        page_size: int,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        doctor_id: int | None = None,
        treatment_id: int | None = None,
        status: AppointmentStatus | None = None,
    ) -> tuple[list[AppointmentSummaryData], int]:
        from app.models.doctor import Doctor
        from app.models.patient import Patient
        from app.models.treatment import Treatment

        conditions = cls._build_conditions(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )

        data_query = (
            select(
                cls.id.label("appointment_id"),
                cls.appointment_datetime,
                cls.status,
                cls.visit_type,
                cls.memo,
                Doctor.id.label("doctor_id"),
                Doctor.name.label("doctor_name"),
                Treatment.id.label("treatment_id"),
                Treatment.name.label("treatment_name"),
                Treatment.duration_minutes.label("treatment_duration_minutes"),
                Patient.id.label("patient_id"),
                Patient.name.label("patient_name"),
                Patient.phone.label("patient_phone"),
            )
            .join(Doctor, cls.doctor_id == Doctor.id)
            .join(Treatment, cls.treatment_id == Treatment.id)
            .join(Patient, cls.patient_id == Patient.id)
        )

        if conditions:
            data_query = data_query.where(*conditions)

        data_query = data_query.order_by(cls.appointment_datetime.desc())
        data_query = data_query.offset((page - 1) * page_size).limit(page_size)

        count_query = (
            select(func.count(cls.id))
            .select_from(cls)
            .join(Doctor, cls.doctor_id == Doctor.id)
            .join(Treatment, cls.treatment_id == Treatment.id)
            .join(Patient, cls.patient_id == Patient.id)
        )

        if conditions:
            count_query = count_query.where(*conditions)

        total_result = await session.execute(count_query)
        total_count = total_result.scalar_one()

        rows = await session.execute(data_query)
        summaries = [
            AppointmentSummaryData(
                id=row.appointment_id,
                appointment_datetime=row.appointment_datetime,
                status=row.status,
                visit_type=row.visit_type,
                memo=row.memo,
                doctor_id=row.doctor_id,
                doctor_name=row.doctor_name,
                treatment_id=row.treatment_id,
                treatment_name=row.treatment_name,
                treatment_duration_minutes=row.treatment_duration_minutes,
                patient_id=row.patient_id,
                patient_name=row.patient_name,
                patient_phone=row.patient_phone,
            )
            for row in rows.all()
        ]

        return summaries, total_count

    @classmethod
    async def get_status_counts(
        cls,
        session: AsyncSession,
        *,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        doctor_id: int | None = None,
        treatment_id: int | None = None,
        status: AppointmentStatus | None = None,
    ) -> list[AppointmentStatusCountItem]:
        conditions = cls._build_conditions(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )

        query = select(cls.status, func.count(cls.id).label("count")).group_by(cls.status)

        if conditions:
            query = query.where(*conditions)
        query = query.order_by(cls.status.asc())

        result = await session.execute(query)
        return [AppointmentStatusCountItem(status=row[0], count=row[1]) for row in result.all()]

    @classmethod
    async def get_daily_counts(
        cls,
        session: AsyncSession,
        *,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        doctor_id: int | None = None,
        treatment_id: int | None = None,
        status: AppointmentStatus | None = None,
    ) -> list[AppointmentDailyCountItem]:
        conditions = cls._build_conditions(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )

        query = select(func.date(cls.appointment_datetime).label("day"), func.count(cls.id).label("count")).group_by(
            "day"
        )
        if conditions:
            query = query.where(*conditions)
        query = query.order_by("day")

        result = await session.execute(query)
        return [AppointmentDailyCountItem(day=row[0], count=row[1]) for row in result.all()]

    @classmethod
    async def get_hourly_counts(
        cls,
        session: AsyncSession,
        *,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        doctor_id: int | None = None,
        treatment_id: int | None = None,
        status: AppointmentStatus | None = None,
    ) -> list[AppointmentTimeslotCountItem]:
        conditions = cls._build_conditions(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )

        hour_col = func.hour(cls.appointment_datetime)
        query = select(hour_col.label("hour"), func.count(cls.id).label("count")).group_by("hour")
        if conditions:
            query = query.where(*conditions)
        query = query.order_by("hour")

        result = await session.execute(query)
        return [AppointmentTimeslotCountItem(hour=int(row[0]), count=row[1]) for row in result.all()]

    @classmethod
    async def get_visit_type_counts(
        cls,
        session: AsyncSession,
        *,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        doctor_id: int | None = None,
        treatment_id: int | None = None,
        status: AppointmentStatus | None = None,
    ) -> list[AppointmentVisitTypeCountItem]:
        conditions = cls._build_conditions(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            doctor_id=doctor_id,
            treatment_id=treatment_id,
            status=status,
        )

        query = select(cls.visit_type, func.count(cls.id).label("count")).group_by(cls.visit_type)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(cls.visit_type.asc())

        result = await session.execute(query)
        return [AppointmentVisitTypeCountItem(visit_type=row[0], count=row[1]) for row in result.all()]

    @classmethod
    def _build_conditions(
        cls,
        *,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        doctor_id: int | None = None,
        treatment_id: int | None = None,
        status: AppointmentStatus | None = None,
    ) -> list[Any]:
        conditions: list[Any] = []

        if start_datetime is not None:
            conditions.append(cls.appointment_datetime >= start_datetime)
        if end_datetime is not None:
            conditions.append(cls.appointment_datetime <= end_datetime)
        if doctor_id is not None:
            conditions.append(cls.doctor_id == doctor_id)
        if treatment_id is not None:
            conditions.append(cls.treatment_id == treatment_id)
        if status is not None:
            conditions.append(cls.status == status)

        return conditions
