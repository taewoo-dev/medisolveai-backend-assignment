"""Appointment list response DTO"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.dtos.appointment.appointment_list_item_response import AppointmentListItemResponse
from app.dtos.frozen_config import FROZEN_CONFIG


class AppointmentListResponse(BaseModel):
    """예약 목록 응답 DTO (페이지네이션 포함)"""

    model_config = FROZEN_CONFIG

    items: list[AppointmentListItemResponse] = Field(default_factory=list, description="예약 목록")
    page: int = Field(..., ge=1, description="현재 페이지")
    page_size: int = Field(..., ge=1, description="페이지 크기")
    total_count: int = Field(..., ge=0, description="총 예약 수")
    total_pages: int = Field(..., ge=0, description="총 페이지 수")
