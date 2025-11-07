"""
HospitalSlot Mother

병원 시간대별 수용 인원 설정 테스트 데이터 생성용 클래스
"""

from __future__ import annotations

from datetime import time

from app.core.constants.day_of_week import DayOfWeek
from app.core.database.connection_async import get_async_session
from app.models.hospital_slot import HospitalSlot


class HospitalSlotMother:
    """병원 시간대별 수용 인원 설정 테스트 데이터 생성 클래스"""

    @staticmethod
    async def create(
        start_time: time = time(10, 0),
        end_time: time = time(10, 30),
        max_capacity: int = 3,
        day_of_week: DayOfWeek | None = None,
        is_active: bool = True,
    ) -> HospitalSlot:
        """
        병원 시간대별 수용 인원 설정 생성
        Args:
            start_time: 시간대 시작 (기본값: 10:00)
            end_time: 시간대 종료 (기본값: 10:30)
            max_capacity: 최대 수용 인원 (기본값: 3)
            day_of_week: 요일별 설정 (기본값: None, 모든 요일)
            is_active: 활성 상태 (기본값: True)

        Returns:
            생성된 병원 시간대별 수용 인원 설정 객체
        """
        async with get_async_session() as session:
            hospital_slot = HospitalSlot(
                start_time=start_time,
                end_time=end_time,
                max_capacity=max_capacity,
                day_of_week=day_of_week,
                is_active=is_active,
            )
            session.add(hospital_slot)
            await session.flush()
            await session.refresh(hospital_slot)
            await session.commit()
            return hospital_slot
