"""Admin Appointment Mother"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.constants.appointment_status import AppointmentStatus
from app.core.constants.visit_type import VisitType
from app.models import Appointment, Patient


class AppointmentMother:
    """예약 테스트 데이터 생성 헬퍼"""

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self._session_maker = session_maker

    async def create(
        self,
        *,
        doctor_id: int,
        treatment_id: int,
        appointment_datetime: datetime,
        status: AppointmentStatus = AppointmentStatus.CONFIRMED,
        visit_type: VisitType = VisitType.FIRST_VISIT,
        memo: str | None = None,
        patient_name: str = "홍길동",
        patient_phone: str = "010-0000-0000",
    ) -> dict[str, Any]:
        async with self._session_maker() as session:
            patient = await self._get_or_create_patient(
                session=session,
                name=patient_name,
                phone=patient_phone,
            )

            appointment = Appointment(
                doctor_id=doctor_id,
                patient_id=patient.id,
                treatment_id=treatment_id,
                appointment_datetime=appointment_datetime,
                status=status,
                visit_type=visit_type,
                memo=memo,
            )
            session.add(appointment)
            await session.commit()
            await session.refresh(appointment)
            await session.refresh(appointment.doctor)
            await session.refresh(appointment.treatment)
            await session.refresh(appointment.patient)

            return self._map_appointment_to_dict(appointment)

    @staticmethod
    def _map_appointment_to_dict(appointment: Appointment) -> dict[str, Any]:
        return {
            "id": appointment.id,
            "appointment_datetime": appointment.appointment_datetime,
            "status": appointment.status,
            "visit_type": appointment.visit_type,
            "memo": appointment.memo,
            "doctor_id": appointment.doctor_id,
            "doctor_name": appointment.doctor.name,
            "treatment_id": appointment.treatment_id,
            "treatment_name": appointment.treatment.name,
            "treatment_duration_minutes": appointment.treatment.duration_minutes,
            "patient_id": appointment.patient_id,
            "patient_name": appointment.patient.name,
            "patient_phone": appointment.patient.phone,
        }

    async def _get_or_create_patient(
        self,
        *,
        session: AsyncSession,
        name: str,
        phone: str,
    ) -> Patient:
        result = await session.execute(select(Patient).where(Patient.phone == phone))
        patient = result.scalar_one_or_none()
        if patient is not None:
            return patient

        patient = Patient(name=name, phone=phone)
        session.add(patient)
        await session.flush()
        await session.refresh(patient)
        return patient
