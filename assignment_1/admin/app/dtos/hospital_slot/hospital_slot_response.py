"""Hospital Slot Response DTO"""

from __future__ import annotations

from datetime import time

from pydantic import BaseModel, Field

from app.dtos.frozen_config import FROZEN_CONFIG


class HospitalSlotResponse(BaseModel):
    """병원 시간대 응답 DTO"""

    model_config = FROZEN_CONFIG

    id: int = Field(..., description="슬롯 ID")
    start_time: time = Field(..., description="시간대 시작")
    end_time: time = Field(..., description="시간대 종료")
    max_capacity: int = Field(..., description="최대 수용 인원")
    is_active: bool = Field(..., description="활성 여부")
