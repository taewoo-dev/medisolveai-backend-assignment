"""
예약 가능 시간 응답 DTO
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.dtos.frozen_config import FROZEN_CONFIG


class AvailableTimeResponse(BaseModel):
    """예약 가능 시간 응답 DTO"""

    model_config = FROZEN_CONFIG

    doctor_id: int = Field(..., description="의사 ID")
    date: str = Field(..., description="조회한 날짜 (YYYY-MM-DD)")
    available_times: list[str] = Field(..., description="예약 가능한 시간대 리스트 (HH:MM 형식)")
