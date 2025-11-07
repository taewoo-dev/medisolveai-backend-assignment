"""로깅 미들웨어"""

from __future__ import annotations

import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # 요청 시작 시간
        start_time = time.time()

        # 요청 정보 로깅 (로컬 환경에서만)
        if request.app.state.settings.is_local:
            print(f"🔄 {request.method} {request.url.path}")

        # 요청 처리
        response = await call_next(request)

        # 처리 시간 계산
        process_time = time.time() - start_time

        # 응답 정보 로깅 (로컬 환경에서만)
        if request.app.state.settings.is_local:
            print(f"✅ {response.status_code} - {process_time:.3f}s")

        # 응답 헤더에 처리 시간 추가
        response.headers["X-Process-Time"] = str(process_time)

        return response
