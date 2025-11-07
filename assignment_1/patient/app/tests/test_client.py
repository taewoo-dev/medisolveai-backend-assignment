"""Patient App 전용 테스트 클라이언트"""

from __future__ import annotations

from typing import Any

import httpx


class MediSolveAiPatientClient:
    """Patient App 테스트 클라이언트"""

    def __init__(self, httpx_client: httpx.AsyncClient):
        """
        Patient App 테스트 중 API 호출은 본 클래스를 통합니다.
        """
        self._client = httpx_client

    async def get_status(self) -> dict[str, Any]:
        """Patient App 상태 확인"""
        response = await self._client.get("/")
        return dict(response.json())

    async def get_health(self) -> dict[str, Any]:
        """Patient App 헬스 체크"""
        response = await self._client.get("/health")
        return dict(response.json())

    async def get_doctors(self, department: str | None = None) -> httpx.Response:
        """의사 목록 조회"""
        params = {
            key: value
            for key, value in {
                "department": department,
            }.items()
            if value is not None
        }
        return await self._client.get("/api/v1/patient/doctors", params=params)

    async def get_available_times(self, doctor_id: int, treatment_id: int, date: str) -> httpx.Response:
        """예약 가능 시간 조회"""
        return await self._client.get(
            "/api/v1/patient/appointments/available-times",
            params={"doctor_id": doctor_id, "treatment_id": treatment_id, "date": date},
        )

    async def get_appointments(self, patient_phone: str) -> httpx.Response:
        """예약 목록 조회"""
        return await self._client.get(
            "/api/v1/patient/appointments",
            params={"patient_phone": patient_phone},
        )

    async def create_appointment(
        self,
        patient_name: str,
        patient_phone: str,
        doctor_id: int,
        treatment_id: int,
        appointment_datetime: str,
        memo: str | None = None,
    ) -> httpx.Response:
        """예약 생성"""
        data = {
            "patient_name": patient_name,
            "patient_phone": patient_phone,
            "doctor_id": doctor_id,
            "treatment_id": treatment_id,
            "appointment_datetime": appointment_datetime,
        }
        if memo is not None:
            data["memo"] = memo
        return await self._client.post("/api/v1/patient/appointments", json=data)

    async def cancel_appointment(self, appointment_id: int, patient_phone: str) -> httpx.Response:
        """예약 취소"""
        return await self._client.patch(
            f"/api/v1/patient/appointments/{appointment_id}/cancel",
            params={"patient_phone": patient_phone},
        )
