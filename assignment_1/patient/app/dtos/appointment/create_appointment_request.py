"""
예약 생성 요청 DTO
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.dtos.frozen_config import FROZEN_CONFIG


class CreateAppointmentRequest(BaseModel):
    """예약 생성 요청 DTO"""

    model_config = FROZEN_CONFIG

    patient_name: str = Field(..., description="환자 이름")
    patient_phone: str = Field(..., description="환자 연락처")
    doctor_id: int = Field(..., description="의사 ID")
    treatment_id: int = Field(..., description="진료 항목 ID")
    appointment_datetime: datetime = Field(..., description="예약 시작 일시")
    memo: str | None = Field(None, description="예약 메모")
