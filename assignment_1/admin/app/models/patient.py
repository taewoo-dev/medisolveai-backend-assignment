"""
Admin App - Patient 모델

관리자가 환자 정보를 조회할 때 사용하는 모델
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.orm import BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.appointment import Appointment


class Patient(BaseModel, TimestampMixin):
    """환자 정보 모델 (관리자용)"""

    __tablename__ = "patients"

    # 기본 정보
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="환자 이름")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, comment="연락처")

    # 관계 설정 (Admin App에서는 예약과의 관계 필요)
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        lazy="select",
        order_by="Appointment.appointment_datetime.desc()",  # 최신 예약 순으로 정렬
    )
