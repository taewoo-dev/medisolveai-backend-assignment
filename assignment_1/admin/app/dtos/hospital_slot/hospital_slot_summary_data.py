"""Hospital Slot Summary Data"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class HospitalSlotSummaryData:
    """병원 시간대 목록 조회용 요약 데이터"""

    id: int
    start_time: time
    end_time: time
    max_capacity: int
    is_active: bool
