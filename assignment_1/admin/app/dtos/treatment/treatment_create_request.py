"""Treatment Create Request DTO"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.dtos.frozen_config import FROZEN_CONFIG


class TreatmentCreateRequest(BaseModel):
    """진료 항목 생성 요청 DTO"""

    model_config = FROZEN_CONFIG

    name: str = Field(..., min_length=1, max_length=100, description="진료 항목명")
    duration_minutes: int = Field(..., ge=1, description="소요 시간 (분)")
    price: Decimal = Field(..., ge=0, description="가격")
    description: str | None = Field(None, description="설명")
    is_active: bool = Field(default=True, description="활성 여부")

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration_minutes(cls, value: int) -> int:
        if value % 30 != 0:
            raise ValueError("소요 시간은 30분 단위여야 합니다.")
        return value
