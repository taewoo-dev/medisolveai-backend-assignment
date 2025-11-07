"""Department Constants"""

from __future__ import annotations

from enum import StrEnum


class Department(StrEnum):
    """병원 진료과 상수"""

    DERMATOLOGY = "DERMATOLOGY"  # 피부과
    SURGERY = "SURGERY"  # 외과
    INTERNAL_MEDICINE = "INTERNAL_MEDICINE"  # 내과
    PEDIATRICS = "PEDIATRICS"  # 소아과
    OBSTETRICS = "OBSTETRICS"  # 산부인과
    DENTISTRY = "DENTISTRY"  # 치과
    ORTHOPEDICS = "ORTHOPEDICS"  # 정형외과
