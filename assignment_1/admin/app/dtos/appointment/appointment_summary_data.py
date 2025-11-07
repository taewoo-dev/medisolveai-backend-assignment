"""Appointment summary data for listings and statistics"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.core.constants.appointment_status import AppointmentStatus
from app.core.constants.visit_type import VisitType


@dataclass(frozen=True)
class AppointmentSummaryData:
    """예약 목록 조회용 요약 데이터"""

    id: int
    appointment_datetime: datetime
    status: AppointmentStatus
    visit_type: VisitType
    memo: str | None
    doctor_id: int
    doctor_name: str
    treatment_id: int
    treatment_name: str
    treatment_duration_minutes: int
    patient_id: int
    patient_name: str
    patient_phone: str


@dataclass(frozen=True)
class AppointmentStatusCountItemData:
    """예약 상태별 건수"""

    status: AppointmentStatus
    count: int


@dataclass(frozen=True)
class AppointmentDailyCountItemData:
    """예약 일별 건수"""

    day: date
    count: int


@dataclass(frozen=True)
class AppointmentTimeslotCountItemData:
    """시간대별 예약 건수"""

    hour: int
    count: int


@dataclass(frozen=True)
class AppointmentVisitTypeCountItemData:
    """방문 유형별 예약 건수"""

    visit_type: VisitType
    count: int
