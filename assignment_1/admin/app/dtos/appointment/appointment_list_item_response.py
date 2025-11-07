"""Appointment list item response DTO"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants.appointment_status import AppointmentStatus
from app.core.constants.visit_type import VisitType
from app.dtos.frozen_config import FROZEN_CONFIG


class AppointmentListItemResponse(BaseModel):
    """예약 목록 아이템 응답 DTO"""

    model_config = FROZEN_CONFIG

    id: int = Field(..., description="예약 ID")
    appointment_datetime: datetime = Field(..., description="예약 일시")
    status: AppointmentStatus = Field(..., description="예약 상태")
    visit_type: VisitType = Field(..., description="방문 유형")
    memo: str | None = Field(default=None, description="예약 메모")
    doctor_id: int = Field(..., description="의사 ID")
    doctor_name: str = Field(..., description="의사 이름")
    treatment_id: int = Field(..., description="진료 항목 ID")
    treatment_name: str = Field(..., description="진료 항목 이름")
    treatment_duration_minutes: int = Field(..., description="진료 소요 시간(분)")
    patient_id: int = Field(..., description="환자 ID")
    patient_name: str = Field(..., description="환자 이름")
    patient_phone: str = Field(..., description="환자 연락처")
