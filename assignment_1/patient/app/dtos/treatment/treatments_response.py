"""
Treatment DTO

진료 항목 정보 응답 DTO
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from app.dtos.frozen_config import FROZEN_CONFIG


class TreatmentResponse(BaseModel):
    """진료 항목 정보 응답 DTO"""

    model_config = FROZEN_CONFIG

    id: int
    name: str
    duration_minutes: int
    price: Decimal
    description: str | None
    is_active: bool
