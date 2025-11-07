"""Doctor Summary Data"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DoctorSummaryData:
    """의사 목록 조회용 요약 데이터"""

    id: int
    name: str
    department: str
    is_active: bool
