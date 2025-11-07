"""
Frozen Config for DTOs

DTO에서 사용하는 불변 객체 설정
"""

from pydantic import ConfigDict

FROZEN_CONFIG = ConfigDict(frozen=True)
