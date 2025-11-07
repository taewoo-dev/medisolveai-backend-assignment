"""
예약 응답 DTO
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.dtos.frozen_config import FROZEN_CONFIG


class AppointmentResponse(BaseModel):
    """예약 응답 DTO"""

    model_config = FROZEN_CONFIG

    id: int = Field(..., description="예약 ID")
    patient_name: str = Field(..., description="환자 이름")
    patient_phone: str = Field(..., description="환자 연락처")
    doctor_id: int = Field(..., description="의사 ID")
    doctor_name: str = Field(..., description="의사 이름")
    treatment_id: int = Field(..., description="진료 항목 ID")
    treatment_name: str = Field(..., description="진료 항목명")
    appointment_datetime: datetime = Field(..., description="예약 시작 일시")
    status: str = Field(..., description="예약 상태")
    visit_type: str = Field(..., description="초진/재진")
    memo: str | None = Field(None, description="예약 메모")
