"""Treatment Response DTO"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.dtos.frozen_config import FROZEN_CONFIG


class TreatmentResponse(BaseModel):
    """진료 항목 응답 DTO"""

    model_config = FROZEN_CONFIG

    id: int = Field(..., description="진료 항목 ID")
    name: str = Field(..., description="진료 항목명")
    duration_minutes: int = Field(..., description="소요 시간 (분)")
    price: Decimal = Field(..., description="가격")
    description: str | None = Field(None, description="설명")
    is_active: bool = Field(..., description="활성 여부")
