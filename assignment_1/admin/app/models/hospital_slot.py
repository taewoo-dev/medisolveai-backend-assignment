"""
Admin App - HospitalSlot 모델

관리자가 병원 시간대별 수용 인원을 관리할 때 사용하는 모델
"""

from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Integer, Time, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants.hospital_constants import DayOfWeek
from app.core.database.orm import BaseModel, TimestampMixin
from app.dtos.hospital_slot import HospitalSlotSummaryData

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
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="활성 상태")

    @classmethod
    async def create_one(
        cls,
        session: AsyncSession,
        *,
        start_time: time,
        end_time: time,
        max_capacity: int,
        is_active: bool = True,
    ) -> HospitalSlot:
        slot = cls(
            start_time=start_time,
            end_time=end_time,
            max_capacity=max_capacity,
            is_active=is_active,
        )
        session.add(slot)
        await session.flush()
        await session.refresh(slot)
        return slot

    @classmethod
    async def get_by_id(cls, session: AsyncSession, slot_id: int) -> HospitalSlot | None:
        return await session.get(cls, slot_id)

    @classmethod
    async def get_by_time(
        cls,
        session: AsyncSession,
        *,
        start_time: time,
        end_time: time,
    ) -> HospitalSlot | None:
        query = select(cls).where(cls.start_time == start_time, cls.end_time == end_time)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_filtered(
        cls,
        session: AsyncSession,
        *,
        is_active: bool | None = None,
    ) -> list[HospitalSlotSummaryData]:
        query = select(
            cls.id,
            cls.start_time,
            cls.end_time,
            cls.max_capacity,
            cls.is_active,
        ).order_by(cls.start_time, cls.end_time)

        if is_active is not None:
            query = query.where(cls.is_active == is_active)

        result = await session.execute(query)
        rows = result.all()
        return [
            HospitalSlotSummaryData(
                id=row.id,
                start_time=row.start_time,
                end_time=row.end_time,
                max_capacity=row.max_capacity,
                is_active=row.is_active,
            )
            for row in rows
        ]

    @classmethod
    async def update_max_capacity(
        cls,
        session: AsyncSession,
        slot_id: int,
        *,
        max_capacity: int,
    ) -> None:
        query = update(cls).where(cls.id == slot_id).values(max_capacity=max_capacity)
        await session.execute(query)

    @classmethod
    async def set_active(
        cls,
        session: AsyncSession,
        slot_id: int,
        *,
        is_active: bool,
    ) -> None:
        query = update(cls).where(cls.id == slot_id).values(is_active=is_active)
        await session.execute(query)
