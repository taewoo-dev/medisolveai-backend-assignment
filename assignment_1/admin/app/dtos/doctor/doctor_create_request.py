"""Doctor Create Request DTO"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.dtos.frozen_config import FROZEN_CONFIG


class DoctorCreateRequest(BaseModel):
    """의사 생성 요청 DTO"""

    model_config = FROZEN_CONFIG

    name: str = Field(..., min_length=1, max_length=100, description="의사 이름")
    department: str = Field(..., min_length=1, max_length=50, description="진료과")
    is_active: bool = Field(default=True, description="활성 여부")
