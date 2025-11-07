"""Treatment Update Request DTO"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.dtos.frozen_config import FROZEN_CONFIG


class TreatmentUpdateRequest(BaseModel):
    """진료 항목 수정 요청 DTO"""

    model_config = FROZEN_CONFIG

    name: str | None = Field(default=None, min_length=1, max_length=100, description="진료 항목명")
    duration_minutes: int | None = Field(default=None, ge=1, description="소요 시간 (분)")
    price: Decimal | None = Field(default=None, ge=0, description="가격")
    description: str | None = Field(default=None, description="설명")

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration_minutes(cls, value: int | None) -> int | None:
        if value is not None and value % 30 != 0:
            raise ValueError("소요 시간은 30분 단위여야 합니다.")
        return value
