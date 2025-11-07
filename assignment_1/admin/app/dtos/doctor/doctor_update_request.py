"""Doctor Update Request DTO"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.dtos.frozen_config import FROZEN_CONFIG


class DoctorUpdateRequest(BaseModel):
    """의사 수정 요청 DTO"""

    model_config = FROZEN_CONFIG

    name: str | None = Field(default=None, min_length=1, max_length=100, description="의사 이름")
    department: str | None = Field(default=None, min_length=1, max_length=50, description="진료과")
