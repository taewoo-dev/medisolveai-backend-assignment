"""
예약 취소 API 테스트
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal

from app.core.constants import AppointmentStatus, ErrorMessages
from app.tests.mothers import DoctorMother, TreatmentMother
from app.tests.test_client import MediSolveAiPatientClient


async def test_cancel_appointment_success(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 취소 성공 테스트"""
    # Given: 의사, 진료 항목 생성 (병렬 처리)
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    patient_phone = "010-1234-5678"
    patient_name = "홍길동"
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # 예약 생성
    create_response = await medisolveai_patient_client.create_appointment(
        patient_name=patient_name,
        patient_phone=patient_phone,
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )
    appointment = create_response.json()
    appointment_id = appointment["id"]

    # When: 예약 취소
    cancel_response = await medisolveai_patient_client.cancel_appointment(
        appointment_id=appointment_id, patient_phone=patient_phone
    )
    cancelled = cancel_response.json()

    # Then: 응답 검증 (200 OK)
    assert cancel_response.status_code == 200
    assert cancelled["id"] == appointment_id
    assert cancelled["status"] == AppointmentStatus.CANCELLED.value

    # 취소된 예약이 조회 목록에 포함되는지 확인 (취소된 예약도 조회됨)
    get_response = await medisolveai_patient_client.get_appointments(patient_phone=patient_phone)
    appointments = get_response.json()
    assert len(appointments) == 1
    assert appointments[0]["id"] == appointment_id
    assert appointments[0]["status"] == AppointmentStatus.CANCELLED.value


async def test_cancel_appointment_not_found(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 취소 - 존재하지 않는 예약"""
    # Given: 존재하지 않는 예약 ID
    appointment_id = 99999
    patient_phone = "010-1234-5678"

    # When: 예약 취소 시도
    response = await medisolveai_patient_client.cancel_appointment(
        appointment_id=appointment_id, patient_phone=patient_phone
    )

    # Then: 에러 응답
    assert response.status_code == 400
    result = response.json()
    assert result["message"] == ErrorMessages.APPOINTMENT_NOT_FOUND


async def test_cancel_appointment_not_owned(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 취소 - 본인 예약이 아닌 경우"""
    # Given: 의사, 진료 항목 생성 (병렬 처리)
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    patient_phone_1 = "010-1111-1111"
    patient_phone_2 = "010-2222-2222"
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # 환자1이 예약 생성
    create_response = await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone=patient_phone_1,
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )
    appointment = create_response.json()
    appointment_id = appointment["id"]

    # When: 환자2가 환자1의 예약 취소 시도
    response = await medisolveai_patient_client.cancel_appointment(
        appointment_id=appointment_id, patient_phone=patient_phone_2
    )

    # Then: 에러 응답 (예약을 찾을 수 없음 - 본인 예약이 아니므로)
    assert response.status_code == 400
    result = response.json()
    assert result["message"] == ErrorMessages.APPOINTMENT_NOT_FOUND


async def test_cancel_appointment_already_cancelled(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 취소 - 이미 취소된 예약"""
    # Given: 의사, 진료 항목 생성 (병렬 처리)
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    patient_phone = "010-1234-5678"
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # 예약 생성
    create_response = await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone=patient_phone,
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )
    appointment = create_response.json()
    appointment_id = appointment["id"]

    # 첫 번째 취소
    await medisolveai_patient_client.cancel_appointment(appointment_id=appointment_id, patient_phone=patient_phone)

    # When: 두 번째 취소 시도
    response = await medisolveai_patient_client.cancel_appointment(
        appointment_id=appointment_id, patient_phone=patient_phone
    )

    # Then: 에러 응답
    assert response.status_code == 400
    result = response.json()
    assert result["message"] == ErrorMessages.APPOINTMENT_ALREADY_CANCELLED
