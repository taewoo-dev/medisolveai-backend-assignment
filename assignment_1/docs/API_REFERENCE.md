# MediSolve AI Backend API Reference

이 문서는 `assignment_1/docker-compose.yml`을 기반으로 전체 스택을 실행한 뒤, Gateway(포트 8000)를 통해 모든 Patient/Admin API를 호출하기 위한 참고 자료입니다. 각 엔드포인트는 `docker compose up -d` 후 바로 사용 가능한 기본 테스트 데이터(`database/test_data.sql`)를 기준으로 작성되었습니다.

> **실행 준비**
> ```bash
> cd assignment_1
> docker compose up -d
> ```
>**종료 시**
> ```bash
> docker compose down -v
> ```

- Gateway Base URL: `http://localhost:8000`
- Gateway를 통한 프록시 경로: `http://localhost:8000/api/v1/patient/...`, `http://localhost:8000/api/v1/admin/...`

---

## 1. Gateway 헬스체크

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/` | Gateway 상태 정보 |
| GET | `/health` | 헬스 체크 |
| GET | `/docs` | FastAPI Swagger UI |

예시:
```bash
curl -s http://localhost:8000/
```

---

## 2. Patient API

### 2.1 의사 목록 조회
- **Gateway 경로**: `GET /api/v1/patient/doctors`
- **쿼리 파라미터**
  - `department` (옵션): 진료과 필터 (예: `department=피부과`)
- **설명**: 활성화된 의사 목록을 이름순으로 반환

예시:
```bash
curl -sG "http://localhost:8000/api/v1/patient/doctors" \
  --data-urlencode "department=피부과"
```

### 2.2 예약 가능 시간 조회
- **Gateway 경로**: `GET /api/v1/patient/appointments/available-times`
- **쿼리 파라미터**
  - `doctor_id` (필수)
  - `treatment_id` (필수)
  - `date` (필수, `YYYY-MM-DD`)
- **설명**: 병원 운영 정책(영업시간, 점심시간, 슬롯 용량)을 고려한 예약 가능 시작 시간(15분 단위) 목록을 반환

예시:
```bash
curl -sG "http://localhost:8000/api/v1/patient/appointments/available-times" \
  --data-urlencode "doctor_id=1" \
  --data-urlencode "treatment_id=1" \
  --data-urlencode "date=2024-11-11"
```

### 2.3 예약 생성
- **Gateway 경로**: `POST /api/v1/patient/appointments`
- **본문(JSON)**
  - `doctor_id`, `patient_phone`, `treatment_id`, `appointment_datetime`, `memo`
- **설명**: 중복 예약/슬롯 용량 검사, 초진/재진 자동 판별 포함

예시:
```bash
curl -s -X POST "http://localhost:8000/api/v1/patient/appointments" \
  -H "Content-Type: application/json" \
  -d '{
        "patient_name": "김테스트",
        "patient_phone": "010-1000-0006",
        "doctor_id": 1,
        "treatment_id": 1,
        "appointment_datetime": "2024-11-18T10:15:00",
        "memo": "추가 상담 요청"
      }'
```

### 2.4 환자 예약 목록 조회
- **Gateway 경로**: `GET /api/v1/patient/appointments`
- **쿼리 파라미터**
  - `patient_phone` (필수)
- **설명**: 해당 환자의 예약 내역(최신순) 반환

예시:
```bash
curl -sG "http://localhost:8000/api/v1/patient/appointments" \
  --data-urlencode "patient_phone=010-1000-0001"
```

### 2.5 예약 취소
- **Gateway 경로**: `PATCH /api/v1/patient/appointments/{appointment_id}/cancel`
- **쿼리 파라미터**
  - `patient_phone` (필수)
- **설명**: 환자 본인의 예약을 취소 상태로 변경 (소프트 취소)

예시:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/patient/appointments/6/cancel?patient_phone=010-1000-0004"
```

---

## 3. Admin API

### 3.1 의사 관리
- **목록 조회**: `GET /api/v1/admin/doctors`
  - 파라미터: `department`, `is_active`, `page`, `page_size`
- **생성**: `POST /api/v1/admin/doctors`
- **수정**: `PATCH /api/v1/admin/doctors/{doctor_id}`
- **비활성화**: `DELETE /api/v1/admin/doctors/{doctor_id}` (소프트 삭제)

목록 조회 예시:
```bash
curl -sG "http://localhost:8000/api/v1/admin/doctors" \
  --data-urlencode "page=1" \
  --data-urlencode "page_size=10"
```

생성 예시:
```bash
curl -s -X POST "http://localhost:8000/api/v1/admin/doctors" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "신규의사",
        "department": "피부과"
      }'
```

### 3.2 진료 항목 관리
- **목록 조회**: `GET /api/v1/admin/treatments`
  - 파라미터: `is_active`, `page`, `page_size`
- **생성**: `POST /api/v1/admin/treatments`
- **수정**: `PATCH /api/v1/admin/treatments/{treatment_id}`
- **비활성화**: `DELETE /api/v1/admin/treatments/{treatment_id}`

생성 예시:
```bash
curl -s -X POST "http://localhost:8000/api/v1/admin/treatments" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "프리미엄 케어",
        "duration_minutes": 60,
        "price": 160000,
        "description": "프리미엄 관리 프로그램"
      }'
```

### 3.3 병원 시간대 관리 (HospitalSlot)
- **목록 조회**: `GET /api/v1/admin/hospital-slots`
  - 파라미터: `is_active`
- **생성**: `POST /api/v1/admin/hospital-slots`
- **수정**: `PATCH /api/v1/admin/hospital-slots/{slot_id}` (max_capacity만 변경 가능)
- **비활성화**: `DELETE /api/v1/admin/hospital-slots/{slot_id}`

생성 예시:
```bash
curl -s -X POST "http://localhost:8000/api/v1/admin/hospital-slots" \
  -H "Content-Type: application/json" \
  -d '{
        "start_time": "18:00",
        "end_time": "18:30",
        "max_capacity": 2,
        "is_active": true
      }'
```

### 3.4 예약 목록 조회 (관리자)
- **경로**: `GET /api/v1/admin/appointments`
- **쿼리 파라미터**
  - `page`, `page_size`, `start_date`, `end_date`, `doctor_id`, `treatment_id`, `status`
- **설명**: 다양한 필터를 적용해 페이지네이션된 예약 목록 반환

예시:
```bash
curl -sG "http://localhost:8000/api/v1/admin/appointments" \
  --data-urlencode "status=확정" \
  --data-urlencode "page=1" \
  --data-urlencode "page_size=10"
```

### 3.5 예약 상태 변경
- **경로**: `PATCH /api/v1/admin/appointments/{appointment_id}/status`
- **본문(JSON)**
  - `status`: `예약대기`, `확정`, `완료`, `취소` (요청 및 응답 모두 `예약대기`, `확정`, `완료`, `취소` 등 한글 상태명을 사용하며, 내부적으로만 영문 코드로 저장됨)
- **설명**: 유효한 상태 전환인지 검사 후 상태 업데이트

예시:
```bash
curl -s -X PATCH "http://localhost:8000/api/v1/admin/appointments/12/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "확정"}'
```

### 3.6 예약 통계 조회
- **경로**: `GET /api/v1/admin/appointments/statistics`
- **쿼리 파라미터**
  - `start_date`, `end_date`, `doctor_id`, `treatment_id`, `status`
- **설명**: 상태별/일별/시간대별/초진·재진 통계를 병렬 계산 후 단일 DTO로 반환

예시:
```bash
curl -sG "http://localhost:8000/api/v1/admin/appointments/statistics" \
  --data-urlencode "start_date=2024-11-10" \
  --data-urlencode "end_date=2024-11-20"
```

---

## 4. 테스트 데이터 참고

`database/test_data.sql`