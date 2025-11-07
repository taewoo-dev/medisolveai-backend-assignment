"""
Base Exception Classes

모든 커스텀 예외의 기본 클래스
"""

from __future__ import annotations

from typing import Any


class MediSolveAiException(Exception):
    """Base exception class for all custom exceptions"""

    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', details={self.details})"
