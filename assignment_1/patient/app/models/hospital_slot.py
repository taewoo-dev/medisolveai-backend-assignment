"""
Patient App - HospitalSlot 모델

병원 시간대별 수용 인원 설정 모델
"""

from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Integer, Time, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants.day_of_week import DayOfWeek
from app.core.database.orm import BaseModel, TimestampMixin

if TYPE_CHECKING:
    pass  # HospitalSlot은 다른 모델과 관계가 없음


class HospitalSlot(BaseModel, TimestampMixin):
    """병원 시간대별 수용 인원 설정 모델"""

    __tablename__ = "hospital_slots"

    # 시간대 정보
    start_time: Mapped[time] = mapped_column(Time, nullable=False, comment="시간대 시작")
    end_time: Mapped[time] = mapped_column(Time, nullable=False, comment="시간대 종료")
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=3, comment="최대 수용 인원")

    # 요일별 설정 (NULL이면 모든 요일 적용)
    day_of_week: Mapped[DayOfWeek | None] = mapped_column(Enum(DayOfWeek), nullable=True, comment="요일별 설정")

    # 활성 상태
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="활성 상태 (예약 검증 시 무시되고 기본값 3 사용)"
    )

    @property
    def duration_minutes(self) -> int:
        """시간대 지속 시간 (분)"""
        from datetime import datetime, timedelta

        # time 객체를 datetime으로 변환하여 계산
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)

        # 자정을 넘어가는 경우 처리
        if end_dt < start_dt:
            end_dt += timedelta(days=1)

        return int((end_dt - start_dt).total_seconds() / 60)

    @property
    def time_range_str(self) -> str:
        """시간대 문자열 표현"""
        return f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

    def is_time_in_slot(self, check_time: time) -> bool:
        """주어진 시간이 이 슬롯에 포함되는지 확인"""
        if self.start_time <= self.end_time:
            # 일반적인 경우 (자정을 넘지 않음)
            return self.start_time <= check_time < self.end_time
        else:
            # 자정을 넘어가는 경우
            return check_time >= self.start_time or check_time < self.end_time

    @classmethod
    async def get_active_slots(
        cls,
        session: AsyncSession,
        slot_time: time,
        day_of_week: DayOfWeek | None = None,
    ) -> list[HospitalSlot]:
        """특정 시간에 해당하는 활성 슬롯 조회"""
        # 활성 슬롯 모두 조회
        query = select(cls).where(cls.is_active)
        result = await session.execute(query)
        all_slots = list(result.scalars().all())

        # Python 레벨에서 필터링
        matching_slots = []
        for slot in all_slots:
            # 시간이 슬롯에 포함되는지 확인
            if not slot.is_time_in_slot(slot_time):
                continue

            # 요일 필터 (NULL이면 모든 요일, 특정 요일이면 해당 요일만)
            if slot.day_of_week is None or slot.day_of_week == day_of_week:
                matching_slots.append(slot)

        return matching_slots

    @classmethod
    async def get_default_capacity(
        cls,
        session: AsyncSession,
        slot_time: time,
        day_of_week: DayOfWeek | None = None,
    ) -> int:
        """특정 시간대의 기본 수용 인원 조회 (슬롯이 없으면 기본값 3)"""
        slots = await cls.get_active_slots(session=session, slot_time=slot_time, day_of_week=day_of_week)
        if slots:
            # 여러 슬롯이 있으면 첫 번째 슬롯의 max_capacity 사용
            return slots[0].max_capacity
        return 3  # 기본값
