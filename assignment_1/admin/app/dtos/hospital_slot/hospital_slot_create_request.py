"""Hospital Slot Create Request DTO"""

from __future__ import annotations

from datetime import time

from pydantic import BaseModel, Field

from app.dtos.frozen_config import FROZEN_CONFIG


class HospitalSlotCreateRequest(BaseModel):
    """병원 시간대 생성 요청 DTO"""

    model_config = FROZEN_CONFIG

    start_time: time = Field(..., description="시간대 시작 (HH:MM)")
    end_time: time = Field(..., description="시간대 종료 (HH:MM)")
    max_capacity: int = Field(..., ge=0, description="최대 수용 인원")
    is_active: bool = Field(default=True, description="활성 여부")
