"""
Appointment with Treatment Data

예약과 진료 항목을 함께 담는 데이터 타입
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AppointmentWithTreatmentData:
    """예약과 진료 항목 데이터"""

    appointment_id: int
    doctor_id: int
    appointment_datetime: datetime
    treatment_duration_minutes: int
