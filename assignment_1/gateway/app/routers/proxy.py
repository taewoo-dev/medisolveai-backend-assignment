"""API Gateway 프록시 라우터"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Request, Response

from app.core import settings

router = APIRouter()

# HTTP 클라이언트 설정
client = httpx.AsyncClient(timeout=30.0)

# 서비스 URL 및 내부 기본 경로 매핑
SERVICE_URLS = {
    "patient": {
        "base_url": f"http://{settings.patient_api_host}:{settings.patient_api_port}",
        "base_path": "/api/v1/patient",
        "special_paths": {"health": "/health"},
    },
    "admin": {
        "base_url": f"http://{settings.admin_api_host}:{settings.admin_api_port}",
        "base_path": "/api/v1/admin",
        "special_paths": {"health": "/health"},
    },
}


def _build_target_path(
    base_path: str,
    suffix: str | None,
    *,
    special_paths: dict[str, str] | None = None,
) -> str:
    """내부 서비스로 전달할 최종 경로를 구성합니다."""

    normalized_suffix = (suffix or "").strip("/")

    if special_paths and normalized_suffix in special_paths:
        return special_paths[normalized_suffix]

    if not normalized_suffix:
        return base_path
    return f"{base_path}/{normalized_suffix}"


async def proxy_request(
    service_url: str,
    path: str,
    request: Request,
) -> Response:
    """요청을 해당 서비스로 프록시"""

    # 타겟 URL 구성
    target_url = f"{service_url}{path}"

    # 쿼리 파라미터 포함
    if request.url.query:
        target_url += f"?{request.url.query}"

    try:
        # 원본 요청의 헤더와 바디를 그대로 전달
        headers = dict(request.headers)
        # Host 헤더 제거 (프록시에서 자동 설정)
        headers.pop("host", None)

        # 요청 바디 읽기
        body = await request.body()

        # 타겟 서비스로 요청 전달
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
        )

        # 응답 헤더에서 불필요한 것들 제거
        excluded_headers = {
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        }

        response_headers = {
            key: value for key, value in response.headers.items() if key.lower() not in excluded_headers
        }

        # 응답 반환
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type"),
        )

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Service error: {str(e)}")


@router.api_route(
    "/v1/patient",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy_to_patient_api_root(request: Request) -> Response:
    """Patient API v1 루트로 프록시"""
    mapping = SERVICE_URLS["patient"]
    return await proxy_request(mapping["base_url"], mapping["base_path"], request)


@router.api_route(
    "/v1/patient/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy_to_patient_api_v1(path: str, request: Request) -> Response:
    """Patient API v1 경로 프록시"""
    mapping = SERVICE_URLS["patient"]
    target_path = _build_target_path(
        mapping["base_path"],
        path,
        special_paths=mapping.get("special_paths"),
    )
    return await proxy_request(mapping["base_url"], target_path, request)


@router.api_route(
    "/v1/admin",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy_to_admin_api_root(request: Request) -> Response:
    """Admin API v1 루트로 프록시"""
    mapping = SERVICE_URLS["admin"]
    return await proxy_request(mapping["base_url"], mapping["base_path"], request)


@router.api_route(
    "/v1/admin/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy_to_admin_api_v1(path: str, request: Request) -> Response:
    """Admin API v1 경로 프록시"""
    mapping = SERVICE_URLS["admin"]
    target_path = _build_target_path(
        mapping["base_path"],
        path,
        special_paths=mapping.get("special_paths"),
    )
    return await proxy_request(mapping["base_url"], target_path, request)
