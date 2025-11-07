"""Hospital Slot Update Request DTO"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.dtos.frozen_config import FROZEN_CONFIG


class HospitalSlotUpdateRequest(BaseModel):
    """병원 시간대 수정 요청 DTO"""

    model_config = FROZEN_CONFIG

    max_capacity: int = Field(..., ge=0, description="최대 수용 인원")
