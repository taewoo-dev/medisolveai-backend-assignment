"""Appointment Status Update Request DTO"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.constants.appointment_status import AppointmentStatus
from app.dtos.frozen_config import FROZEN_CONFIG


class AppointmentStatusUpdateRequest(BaseModel):
    """예약 상태 변경 요청 DTO"""

    model_config = FROZEN_CONFIG

    status: AppointmentStatus = Field(..., description="변경할 예약 상태")
