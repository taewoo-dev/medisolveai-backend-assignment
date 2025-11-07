"""Treatment Summary Data"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TreatmentSummaryData:
    """진료 항목 목록 조회용 요약 데이터"""

    id: int
    name: str
    duration_minutes: int
    price: Decimal
    is_active: bool
