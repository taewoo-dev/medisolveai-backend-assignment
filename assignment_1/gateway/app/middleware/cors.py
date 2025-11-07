"""CORS 미들웨어"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def add_cors_middleware(app: FastAPI) -> None:
    """CORS 미들웨어 추가"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 개발 환경에서는 모든 오리진 허용
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
