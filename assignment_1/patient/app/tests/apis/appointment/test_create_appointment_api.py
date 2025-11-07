"""
예약 생성 API 테스트
"""

from __future__ import annotations

import asyncio
from datetime import datetime, time
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.constants import AppointmentStatus, ErrorMessages, VisitType
from app.models.appointment import Appointment
from app.tests.mothers import DoctorMother, HospitalSlotMother, TreatmentMother
from app.tests.test_client import MediSolveAiPatientClient


async def test_create_appointment_success_first_visit(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 생성 성공 테스트 (초진)"""
    # Given: 의사와 진료 항목 생성 (병렬 처리)
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    # 예약 시간 설정
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # When: 예약 생성
    response = await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone="010-1234-5678",
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
        memo="테스트 예약",
    )
    appointment = response.json()

    # Then: 응답 검증
    assert response.status_code == 201
    assert appointment["patient_name"] == "홍길동"
    assert appointment["patient_phone"] == "010-1234-5678"
    assert appointment["doctor_id"] == doctor.id
    assert appointment["doctor_name"] == "김의사"
    assert appointment["treatment_id"] == treatment.id
    assert appointment["treatment_name"] == "기본 진료"
    assert appointment["visit_type"] == VisitType.FIRST_VISIT
    assert appointment["memo"] == "테스트 예약"


async def test_create_appointment_success_return_visit(
    medisolveai_patient_client: MediSolveAiPatientClient,
    session_maker_medisolveai: async_sessionmaker[AsyncSession],
) -> None:
    """예약 생성 성공 테스트 (재진)"""
    # Given: 의사와 진료 항목 생성 (병렬 처리)
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    # 예약 시간 설정
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # Given: 첫 번째 예약 생성 및 완료 처리
    first_response = await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone="010-1234-5678",
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )
    first_appointment_id = first_response.json()["id"]

    # 첫 번째 예약을 완료 상태로 변경
    async with session_maker_medisolveai() as session:
        from sqlalchemy import update

        update_query = (
            update(Appointment)
            .where(Appointment.id == first_appointment_id)
            .values(status=AppointmentStatus.COMPLETED.value)
        )
        await session.execute(update_query)
        await session.commit()

    # 두 번째 예약 시간 설정
    second_appointment_datetime = datetime(2024, 12, 2, 10, 0)

    # When: 두 번째 예약 생성
    response = await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone="010-1234-5678",
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=second_appointment_datetime.isoformat(),
    )
    appointment = response.json()

    # Then: 재진으로 생성되었는지 확인
    assert response.status_code == 201
    assert appointment["visit_type"] == VisitType.RETURN_VISIT


async def test_create_appointment_doctor_not_found(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """의사가 존재하지 않을 때 예약 생성 실패 테스트"""
    # Given: 진료 항목만 생성
    treatment = await TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00"))

    # 예약 시간 설정
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # When: 존재하지 않는 의사 ID로 예약 생성
    response = await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone="010-1234-5678",
        doctor_id=99999,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )

    # Then: 에러 응답 확인
    assert response.status_code == 400
    assert response.json()["message"] == ErrorMessages.DOCTOR_NOT_FOUND


async def test_create_appointment_treatment_not_found(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """진료 항목이 존재하지 않을 때 예약 생성 실패 테스트"""
    # Given: 의사만 생성
    doctor = await DoctorMother.create(name="김의사", department="피부과")

    # 예약 시간 설정
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # When: 존재하지 않는 진료 항목 ID로 예약 생성
    response = await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone="010-1234-5678",
        doctor_id=doctor.id,
        treatment_id=99999,
        appointment_datetime=appointment_datetime.isoformat(),
    )

    # Then: 에러 응답 확인
    assert response.status_code == 400
    assert response.json()["message"] == ErrorMessages.TREATMENT_NOT_FOUND


async def test_create_appointment_duplicate_time(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """중복 예약 방지 테스트"""
    # Given: 의사와 진료 항목 생성 (병렬 처리)
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    # 예약 시간 설정
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # Given: 첫 번째 예약 생성
    first_response = await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone="010-1234-5678",
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )
    assert first_response.status_code == 201

    # When: 동일한 시간에 두 번째 예약 생성 시도
    response = await medisolveai_patient_client.create_appointment(
        patient_name="김철수",
        patient_phone="010-9876-5432",
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )

    # Then: 중복 예약 에러 확인
    assert response.status_code == 400
    assert response.json()["message"] == ErrorMessages.APPOINTMENT_ALREADY_EXISTS


async def test_create_appointment_invalid_time_interval(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 시간이 15분 간격이 아닐 때 실패 테스트"""
    # Given: 의사와 진료 항목 생성 (병렬 처리)
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    # 예약 시간 설정 (15분 간격이 아님)
    appointment_datetime = datetime(2024, 12, 1, 10, 17)

    # When: 15분 간격이 아닌 시간으로 예약 생성 시도
    response = await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone="010-1234-5678",
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )

    # Then: 에러 응답 확인
    assert response.status_code == 400
    assert response.json()["message"] == ErrorMessages.APPOINTMENT_TIME_INVALID


async def test_create_appointment_slot_capacity_exceeded(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """시간대별 최대 인원수 제한 초과 테스트"""
    # Given: HospitalSlot 생성 (10:00~10:30, 최대 인원수 3명)
    await HospitalSlotMother.create(
        start_time=time(10, 0),
        end_time=time(10, 30),
        max_capacity=3,
    )

    # Given: 의사 4명과 진료 항목 생성 (병렬 처리)
    doctors, treatment = await asyncio.gather(
        DoctorMother.create_bulk(count=4, department="피부과"),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    # 예약 시간 설정 (같은 시간대)
    appointment_datetime = datetime(2024, 12, 1, 10, 0)

    # Given: 같은 시간대에 3개의 예약 생성 (최대 인원수 3명, 병렬 처리)
    await asyncio.gather(
        *[
            medisolveai_patient_client.create_appointment(
                patient_name=f"환자{i+1}",
                patient_phone=f"010-1111-{1000+i:04d}",
                doctor_id=doctors[i].id,
                treatment_id=treatment.id,
                appointment_datetime=appointment_datetime.isoformat(),
            )
            for i in range(3)
        ]
    )

    # When: 4번째 예약 생성 시도 (수용 인원 초과)
    response = await medisolveai_patient_client.create_appointment(
        patient_name="환자4",
        patient_phone="010-1111-1003",
        doctor_id=doctors[3].id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )

    # Then: 수용 인원 초과 에러 확인
    assert response.status_code == 400
    assert response.json()["message"] == ErrorMessages.APPOINTMENT_CAPACITY_FULL
