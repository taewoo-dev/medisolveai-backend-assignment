"""
예약 조회 API 테스트
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal

from app.core.constants import AppointmentStatus, VisitType
from app.tests.mothers import DoctorMother, TreatmentMother
from app.tests.test_client import MediSolveAiPatientClient


async def test_get_appointments_success(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 목록 조회 성공 테스트"""
    # Given: 의사, 진료 항목 생성 (병렬 처리)
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    patient_phone = "010-1234-5678"
    patient_name = "홍길동"

    # 예약 3개 생성 (시간 순서대로)
    appointment_datetime_1 = datetime(2024, 12, 1, 10, 0)
    appointment_datetime_2 = datetime(2024, 12, 2, 14, 0)
    appointment_datetime_3 = datetime(2024, 12, 3, 16, 0)

    # When: 예약 생성 (순차 처리 - 같은 환자이므로)
    await medisolveai_patient_client.create_appointment(
        patient_name=patient_name,
        patient_phone=patient_phone,
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime_1.isoformat(),
    )
    await medisolveai_patient_client.create_appointment(
        patient_name=patient_name,
        patient_phone=patient_phone,
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime_2.isoformat(),
    )
    await medisolveai_patient_client.create_appointment(
        patient_name=patient_name,
        patient_phone=patient_phone,
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime_3.isoformat(),
    )

    # When: 예약 목록 조회
    response = await medisolveai_patient_client.get_appointments(patient_phone=patient_phone)
    appointments = response.json()

    # Then: 응답 검증
    assert response.status_code == 200
    assert len(appointments) == 3

    # 최신순으로 정렬되어 있는지 확인 (가장 최근 예약이 첫 번째)
    assert appointments[0]["appointment_datetime"] == appointment_datetime_3.isoformat()
    assert appointments[1]["appointment_datetime"] == appointment_datetime_2.isoformat()
    assert appointments[2]["appointment_datetime"] == appointment_datetime_1.isoformat()

    # 각 예약 정보 검증
    for appointment in appointments:
        assert appointment["patient_name"] == patient_name
        assert appointment["patient_phone"] == patient_phone
        assert appointment["doctor_id"] == doctor.id
        assert appointment["doctor_name"] == "김의사"
        assert appointment["treatment_id"] == treatment.id
        assert appointment["treatment_name"] == "기본 진료"
        assert appointment["status"] == AppointmentStatus.PENDING.value
        assert appointment["visit_type"] in [VisitType.FIRST_VISIT.value, VisitType.RETURN_VISIT.value]


async def test_get_appointments_empty(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 목록 조회 - 예약이 없는 경우"""
    # Given: 예약이 없는 환자 전화번호
    patient_phone = "010-9999-9999"

    # When: 예약 목록 조회
    response = await medisolveai_patient_client.get_appointments(patient_phone=patient_phone)
    appointments = response.json()

    # Then: 빈 리스트 반환
    assert response.status_code == 200
    assert appointments == []


async def test_get_appointments_only_own(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 목록 조회 - 본인 예약만 조회되는지 확인"""
    # Given: 의사, 진료 항목 생성 (병렬 처리)
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    patient_phone_1 = "010-1111-1111"
    patient_phone_2 = "010-2222-2222"
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # When: 서로 다른 환자가 예약 생성 (병렬 처리)
    await asyncio.gather(
        medisolveai_patient_client.create_appointment(
            patient_name="홍길동",
            patient_phone=patient_phone_1,
            doctor_id=doctor.id,
            treatment_id=treatment.id,
            appointment_datetime=appointment_datetime.isoformat(),
        ),
        medisolveai_patient_client.create_appointment(
            patient_name="김철수",
            patient_phone=patient_phone_2,
            doctor_id=doctor.id,
            treatment_id=treatment.id,
            appointment_datetime=appointment_datetime.isoformat(),
        ),
    )

    # When: 각 환자의 예약 목록 조회 (병렬 처리)
    response_1, response_2 = await asyncio.gather(
        medisolveai_patient_client.get_appointments(patient_phone=patient_phone_1),
        medisolveai_patient_client.get_appointments(patient_phone=patient_phone_2),
    )
    appointments_1 = response_1.json()
    appointments_2 = response_2.json()

    # Then: 각 환자는 본인의 예약만 조회됨
    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert len(appointments_1) == 1
    assert len(appointments_2) == 1
    assert appointments_1[0]["patient_phone"] == patient_phone_1
    assert appointments_2[0]["patient_phone"] == patient_phone_2
