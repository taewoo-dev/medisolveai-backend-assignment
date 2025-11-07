"""
Doctor Service

의사 정보 조회 및 생성 서비스
"""

from __future__ import annotations

from app.core.database.connection_async import get_async_session
from app.dtos.doctor import DoctorResponse
from app.models.doctor import Doctor


async def service_create_doctor(name: str, department: str, is_active: bool = True) -> Doctor:
    """의사 생성"""
    async with get_async_session() as session:
        doctor = await Doctor.create_one(session=session, name=name, department=department, is_active=is_active)
        await session.commit()
        return doctor


async def service_get_doctors(department: str | None = None) -> list[DoctorResponse]:
    async with get_async_session() as session:
        doctors = await Doctor.get_active_doctors(session=session, department=department)
        return [DoctorResponse(id=d.id, name=d.name, department=d.department, is_active=d.is_active) for d in doctors]
