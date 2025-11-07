"""Appointment Statistics Response DTOs"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.core.constants.appointment_status import AppointmentStatus
from app.core.constants.visit_type import VisitType
from app.dtos.frozen_config import FROZEN_CONFIG


class AppointmentStatusCountItem(BaseModel):
    """상태별 예약 건수"""

    model_config = FROZEN_CONFIG

    status: AppointmentStatus = Field(..., description="예약 상태")
    count: int = Field(..., ge=0, description="건수")


class AppointmentDailyCountItem(BaseModel):
    """일별 예약 현황"""

    model_config = FROZEN_CONFIG

    day: date = Field(..., description="날짜")
    count: int = Field(..., ge=0, description="건수")


class AppointmentTimeslotCountItem(BaseModel):
    """시간대별 예약 현황 (시간 단위)"""

    model_config = FROZEN_CONFIG

    hour: int = Field(..., ge=0, le=23, description="시간 (0-23)")
    count: int = Field(..., ge=0, description="건수")


class AppointmentVisitTypeCountItem(BaseModel):
    """초진/재진 예약 건수"""

    model_config = FROZEN_CONFIG

    visit_type: VisitType = Field(..., description="방문 유형")
    count: int = Field(..., ge=0, description="건수")


class AppointmentStatisticsResponse(BaseModel):
    """예약 통계 응답 DTO"""

    model_config = FROZEN_CONFIG

    status_counts: list[AppointmentStatusCountItem] = Field(default_factory=list, description="상태별 건수")
    daily_counts: list[AppointmentDailyCountItem] = Field(default_factory=list, description="일별 건수")
    timeslot_counts: list[AppointmentTimeslotCountItem] = Field(default_factory=list, description="시간대별 건수")
    visit_type_counts: list[AppointmentVisitTypeCountItem] = Field(default_factory=list, description="방문 유형별 건수")
