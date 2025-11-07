"""Frozen Config for DTOs"""

from pydantic import ConfigDict

FROZEN_CONFIG = ConfigDict(frozen=True, extra="forbid")
