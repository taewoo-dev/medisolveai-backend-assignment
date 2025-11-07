"""방문 유형 상수"""

from __future__ import annotations

from enum import Enum


class VisitType(str, Enum):
    """방문 유형 (초진/재진)"""

    FIRST_VISIT = "초진"  # 첫 방문 (해당 환자의 첫 진료)
    RETURN_VISIT = "재진"  # 재방문 (이전에 진료 받은 적 있음)

    @classmethod
    def determine_visit_type(cls, has_previous_completed_visit: bool) -> VisitType:
        """이전 완료된 진료 기록을 바탕으로 방문 유형 결정"""
        if has_previous_completed_visit:
            return cls.RETURN_VISIT
        else:
            return cls.FIRST_VISIT

    def is_first_visit(self) -> bool:
        """초진 여부"""
        return self == self.FIRST_VISIT

    def is_return_visit(self) -> bool:
        """재진 여부"""
        return self == self.RETURN_VISIT

    def get_description(self) -> str:
        """방문 유형 설명"""
        descriptions = {
            self.FIRST_VISIT: "첫 방문 - 기본 상담 및 진단",
            self.RETURN_VISIT: "재방문 - 경과 관찰 및 추가 치료",
        }
        return descriptions.get(self, "알 수 없는 방문 유형")
