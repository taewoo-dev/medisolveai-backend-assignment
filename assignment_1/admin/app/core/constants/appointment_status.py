"""예약 상태 상수"""

from __future__ import annotations

from enum import Enum


class AppointmentStatus(str, Enum):
    """예약 상태"""

    PENDING = "예약대기"  # 예약 요청 후 확정 대기 중
    CONFIRMED = "확정"  # 예약 확정됨
    COMPLETED = "완료"  # 진료 완료
    CANCELLED = "취소"  # 예약 취소

    @classmethod
    def get_active_statuses(cls) -> list[AppointmentStatus]:
        """활성 상태 목록 (취소/미방문 제외)"""
        return [cls.PENDING, cls.CONFIRMED, cls.COMPLETED]

    @classmethod
    def get_bookable_statuses(cls) -> list[AppointmentStatus]:
        """예약 가능한 상태 (대기/확정)"""
        return [cls.PENDING, cls.CONFIRMED]

    def is_active(self) -> bool:
        """활성 상태 여부"""
        return self in self.get_active_statuses()

    def is_bookable(self) -> bool:
        """예약 중인 상태 여부 (시간대 점유)"""
        return self in self.get_bookable_statuses()

    def is_completed(self) -> bool:
        """완료된 상태 여부"""
        return self == self.COMPLETED

    def is_cancelled(self) -> bool:
        """취소된 상태 여부"""
        return self == self.CANCELLED
