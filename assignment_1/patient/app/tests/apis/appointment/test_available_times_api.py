"""
예약 가능 시간 조회 API 테스트
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, time
from decimal import Decimal

from app.core.constants import Department, ErrorMessages
from app.tests.mothers import DoctorMother, HospitalSlotMother, TreatmentMother
from app.tests.test_client import MediSolveAiPatientClient


async def test_get_available_times_success(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """예약 가능 시간 조회 성공 테스트"""
    # Given: 의사, 진료 항목(30분, 60분), HospitalSlot 생성 (병렬 처리)
    doctor, treatment_30min, treatment_60min, _ = await asyncio.gather(
        DoctorMother.create(name="김의사", department=Department.DERMATOLOGY),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
        TreatmentMother.create(name="복합 치료", duration_minutes=60, price=Decimal("100000.00")),
        HospitalSlotMother.create(
            start_time=time(10, 0),
            end_time=time(10, 30),
            max_capacity=3,
        ),
    )

    # 조회할 날짜 설정 (운영일)
    appointment_date = date(2024, 12, 2)  # 월요일

    # When: 예약 가능 시간 조회 (30분 진료, 60분 진료 병렬 처리)
    response_30min, response_60min = await asyncio.gather(
        medisolveai_patient_client.get_available_times(
            doctor_id=doctor.id,
            treatment_id=treatment_30min.id,
            date=appointment_date.isoformat(),
        ),
        medisolveai_patient_client.get_available_times(
            doctor_id=doctor.id,
            treatment_id=treatment_60min.id,
            date=appointment_date.isoformat(),
        ),
    )
    result_30min = response_30min.json()
    result_60min = response_60min.json()

    # Then: 30분 진료 응답 검증
    assert response_30min.status_code == 200
    assert result_30min["doctor_id"] == doctor.id
    assert result_30min["date"] == appointment_date.isoformat()
    assert isinstance(result_30min["available_times"], list)
    # 운영 시간 내 시간대가 포함되어야 함 (점심시간 제외)
    assert "09:00" in result_30min["available_times"]
    assert "09:15" in result_30min["available_times"]
    # 11:30은 가능해야 함 (11:30~12:00, 점심시간과 겹치지 않음)
    assert "11:30" in result_30min["available_times"]
    # 11:45는 제외되어야 함 (11:45~12:15, 점심시간과 겹침)
    assert "11:45" not in result_30min["available_times"]
    # 점심시간은 제외되어야 함
    assert "12:00" not in result_30min["available_times"]
    assert "12:15" not in result_30min["available_times"]
    assert "12:30" not in result_30min["available_times"]
    assert "12:45" not in result_30min["available_times"]
    # 점심시간 이후 시간대 포함
    assert "13:00" in result_30min["available_times"]
    # 17:30은 가능해야 함 (17:30~18:00, 퇴근시간과 겹치지 않음)
    assert "17:30" in result_30min["available_times"]
    # 17:45는 제외되어야 함 (17:45~18:15, 퇴근시간을 넘어감)
    assert "17:45" not in result_30min["available_times"]

    # Then: 60분 진료 응답 검증
    assert response_60min.status_code == 200
    assert result_60min["doctor_id"] == doctor.id
    assert result_60min["date"] == appointment_date.isoformat()
    assert isinstance(result_60min["available_times"], list)
    # 11:00은 가능해야 함 (11:00~12:00, 점심시간과 겹치지 않음)
    assert "11:00" in result_60min["available_times"]
    # 11:15는 제외되어야 함 (11:15~12:15, 점심시간과 겹침)
    assert "11:15" not in result_60min["available_times"]
    # 11:30은 제외되어야 함 (11:30~12:30, 점심시간과 겹침)
    assert "11:30" not in result_60min["available_times"]
    # 17:00은 가능해야 함 (17:00~18:00, 퇴근시간과 겹치지 않음)
    assert "17:00" in result_60min["available_times"]
    # 17:15는 제외되어야 함 (17:15~18:15, 퇴근시간을 넘어감)
    assert "17:15" not in result_60min["available_times"]


async def test_get_available_times_closed_day(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """휴무일 예약 가능 시간 조회 테스트"""
    # Given: 의사와 진료 항목 생성
    doctor, treatment = await asyncio.gather(
        DoctorMother.create(name="김의사", department=Department.DERMATOLOGY),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
    )

    # 조회할 날짜 설정 (일요일 - 휴무일)
    appointment_date = date(2024, 12, 1)  # 일요일

    # When: 예약 가능 시간 조회
    response = await medisolveai_patient_client.get_available_times(
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        date=appointment_date.isoformat(),
    )
    result = response.json()

    # Then: 응답 검증 (빈 리스트)
    assert response.status_code == 200
    assert result["doctor_id"] == doctor.id
    assert result["date"] == appointment_date.isoformat()
    assert result["available_times"] == []


async def test_get_available_times_doctor_not_found(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """의사가 존재하지 않을 때 예약 가능 시간 조회 실패 테스트"""
    # Given: 진료 항목 생성
    treatment = await TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00"))

    # 조회할 날짜 설정
    appointment_date = date(2024, 12, 2)

    # When: 존재하지 않는 의사 ID로 예약 가능 시간 조회
    response = await medisolveai_patient_client.get_available_times(
        doctor_id=99999,
        treatment_id=treatment.id,
        date=appointment_date.isoformat(),
    )

    # Then: 에러 응답 확인
    assert response.status_code == 400
    assert response.json()["message"] == ErrorMessages.DOCTOR_NOT_FOUND


async def test_get_available_times_with_existing_appointments(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """기존 예약이 있는 경우 예약 가능 시간 조회 테스트"""
    # Given: 의사, 진료 항목, HospitalSlot 생성 (병렬 처리)
    doctor, treatment, _ = await asyncio.gather(
        DoctorMother.create(name="김의사", department=Department.DERMATOLOGY),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
        HospitalSlotMother.create(
            start_time=time(10, 0),
            end_time=time(10, 30),
            max_capacity=3,
        ),
    )

    # 조회할 날짜 설정
    appointment_date = date(2024, 12, 2)

    # Given: 기존 예약 생성 (10:00~10:30)
    appointment_datetime = datetime.combine(appointment_date, time(10, 0))
    await medisolveai_patient_client.create_appointment(
        patient_name="홍길동",
        patient_phone="010-1234-5678",
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        appointment_datetime=appointment_datetime.isoformat(),
    )

    # When: 예약 가능 시간 조회
    response = await medisolveai_patient_client.get_available_times(
        doctor_id=doctor.id,
        treatment_id=treatment.id,
        date=appointment_date.isoformat(),
    )
    result = response.json()

    # Then: 응답 검증
    assert response.status_code == 200
    # 10:00은 이미 예약되어 있으므로 제외되어야 함
    assert "10:00" not in result["available_times"]
    # 10:15는 10:00~10:30 예약과 겹치므로 제외되어야 함
    assert "10:15" not in result["available_times"]
    # 10:30은 가능해야 함 (10:00~10:30 예약과 겹치지 않음)
    assert "10:30" in result["available_times"]


async def test_get_available_times_capacity_exceeded(
    medisolveai_patient_client: MediSolveAiPatientClient,
) -> None:
    """수용 인원 초과로 인한 예약 불가 시간 조회 테스트"""
    # Given: 의사 4명, 진료 항목, HospitalSlot 생성 (병렬 처리)
    doctors, treatment, _ = await asyncio.gather(
        DoctorMother.create_bulk(count=4, department=Department.DERMATOLOGY),
        TreatmentMother.create(name="기본 진료", duration_minutes=30, price=Decimal("50000.00")),
        HospitalSlotMother.create(
            start_time=time(10, 0),
            end_time=time(10, 30),
            max_capacity=3,
        ),
    )

    # 조회할 날짜 설정
    appointment_date = date(2024, 12, 2)
    appointment_datetime = datetime.combine(appointment_date, time(10, 0))

    # Given: 같은 시간대에 3개의 예약 생성 (최대 인원수 3명)
    responses = await asyncio.gather(
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
    for response in responses:
        assert response.status_code == 201

    # When: 예약 가능 시간 조회 (4번째 의사)
    response = await medisolveai_patient_client.get_available_times(
        doctor_id=doctors[3].id,
        treatment_id=treatment.id,
        date=appointment_date.isoformat(),
    )
    result = response.json()

    # Then: 응답 검증
    assert response.status_code == 200
    # 10:00은 수용 인원 초과로 제외되어야 함
    assert "10:00" not in result["available_times"]
    # 10:15는 10:00~10:30 슬롯과 겹치므로 제외되어야 함
    assert "10:15" not in result["available_times"]
    # 10:30은 가능해야 함 (다른 슬롯)
    assert "10:30" in result["available_times"]
