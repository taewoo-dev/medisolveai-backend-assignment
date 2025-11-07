"""진료과 상수"""

from __future__ import annotations

from enum import StrEnum


class Department(StrEnum):
    """진료과"""

    DERMATOLOGY = "피부과"
    ORTHOPEDICS = "정형외과"
    INTERNAL_MEDICINE = "내과"
    SURGERY = "외과"
    PEDIATRICS = "소아과"
