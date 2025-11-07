"""Admin App 전용 테스트 클라이언트"""

from __future__ import annotations

from typing import Any

import httpx


class MediSolveAiAdminClient:
    """Admin App 테스트 클라이언트"""

    def __init__(self, httpx_client: httpx.AsyncClient):
        """
        Admin App 테스트 중 API 호출은 본 클래스를 통합니다.
        """
        self._client = httpx_client

    async def get_status(self) -> dict[str, Any]:
        """Admin App 상태 확인"""
        response = await self._client.get("/")
        return dict(response.json())

    async def get_health(self) -> dict[str, Any]:
        """Admin App 헬스 체크"""
        response = await self._client.get("/health")
        return dict(response.json())

    async def create_doctor(self, *, name: str, department: str, is_active: bool = True) -> httpx.Response:
        """의사 생성"""

        payload = {"name": name, "department": department, "is_active": is_active}
        return await self._client.post("/api/v1/admin/doctors", json=payload)

    async def create_treatment(
        self,
        *,
        name: str,
        duration_minutes: int,
        price: str | float,
        description: str | None = None,
        is_active: bool = True,
    ) -> httpx.Response:
        """진료 항목 생성"""

        payload = {
            "name": name,
            "duration_minutes": duration_minutes,
            "price": price,
            "is_active": is_active,
        }
        if description is not None:
            payload["description"] = description
        return await self._client.post("/api/v1/admin/treatments", json=payload)

    async def get_treatments(
        self,
        *,
        is_active: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> httpx.Response:
        """진료 항목 목록 조회"""

        params = {
            key: value
            for key, value in {
                "is_active": is_active,
                "page": page,
                "page_size": page_size,
            }.items()
            if value is not None
        }
        return await self._client.get("/api/v1/admin/treatments", params=params)

    async def update_treatment(self, treatment_id: int, **payload: Any) -> httpx.Response:
        """진료 항목 수정"""

        return await self._client.patch(f"/api/v1/admin/treatments/{treatment_id}", json=payload)

    async def delete_treatment(self, treatment_id: int) -> httpx.Response:
        """진료 항목 비활성화"""

        return await self._client.delete(f"/api/v1/admin/treatments/{treatment_id}")

    async def get_doctors(
        self,
        *,
        department: str | None = None,
        is_active: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> httpx.Response:
        """의사 목록 조회"""
        params = {
            key: value
            for key, value in {
                "department": department,
                "is_active": is_active,
                "page": page,
                "page_size": page_size,
            }.items()
            if value is not None
        }
        return await self._client.get("/api/v1/admin/doctors", params=params)

    async def update_doctor(self, doctor_id: int, **payload: Any) -> httpx.Response:
        """의사 정보 수정"""
        return await self._client.patch(f"/api/v1/admin/doctors/{doctor_id}", json=payload)

    async def delete_doctor(self, doctor_id: int) -> httpx.Response:
        """의사 정보 삭제"""
        return await self._client.delete(f"/api/v1/admin/doctors/{doctor_id}")

    async def create_hospital_slot(
        self,
        *,
        start_time: str,
        end_time: str,
        max_capacity: int,
        is_active: bool = True,
    ) -> httpx.Response:
        """병원 시간대 생성"""

        payload = {
            "start_time": start_time,
            "end_time": end_time,
            "max_capacity": max_capacity,
            "is_active": is_active,
        }
        return await self._client.post("/api/v1/admin/hospital-slots", json=payload)

    async def get_hospital_slots(self, *, is_active: bool | None = None) -> httpx.Response:
        """병원 시간대 목록 조회"""

        params = {"is_active": is_active} if is_active is not None else None
        return await self._client.get("/api/v1/admin/hospital-slots", params=params)

    async def update_hospital_slot(self, slot_id: int, **payload: Any) -> httpx.Response:
        """병원 시간대 수정"""

        return await self._client.patch(f"/api/v1/admin/hospital-slots/{slot_id}", json=payload)

    async def delete_hospital_slot(self, slot_id: int) -> httpx.Response:
        """병원 시간대 비활성화"""

        return await self._client.delete(f"/api/v1/admin/hospital-slots/{slot_id}")

    async def get_appointments(self, **params: Any) -> httpx.Response:
        """예약 목록 조회"""

        query_params = {key: value for key, value in params.items() if value is not None}
        return await self._client.get("/api/v1/admin/appointments", params=query_params)

    async def update_appointment_status(self, appointment_id: int, *, status: str) -> httpx.Response:
        """예약 상태 변경"""

        payload = {"status": status}
        return await self._client.patch(f"/api/v1/admin/appointments/{appointment_id}/status", json=payload)

    async def get_appointment_statistics(self, **params: Any) -> httpx.Response:
        """예약 통계 조회"""

        query_params = {key: value for key, value in params.items() if value is not None}
        return await self._client.get("/api/v1/admin/appointments/statistics", params=query_params)
