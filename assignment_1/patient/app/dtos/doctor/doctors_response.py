"""
Doctor DTO

의사 정보 응답 DTO
"""

from __future__ import annotations

from pydantic import BaseModel

from app.dtos.frozen_config import FROZEN_CONFIG


class DoctorResponse(BaseModel):
    """의사 정보 응답 DTO"""

    model_config = FROZEN_CONFIG

    id: int
    name: str
    department: str
    is_active: bool
