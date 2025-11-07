# MediSolve AI Backend Assignment

## 프로젝트 설명
- 피부과 예약 관리 시스템의 Gateway, Patient API, Admin API로 구성된 마이크로서비스 백엔드입니다.
- 예약 가능 시간 계산, 환자/의사/진료 항목 관리, 관리자 통계 등을 FastAPI와 SQLAlchemy(Async) 기반으로 제공합니다.
- 공통 MySQL 데이터베이스를 사용하며 `asyncio` 기반 비동기 처리와 Object Mother 테스트 패턴을 적용했습니다.

## 환경 설정 방법
- Python 3.12, `uv` 패키지 매니저를 사용합니다.
- 각 서비스 디렉터리에 `.env` 파일을 생성해 `ENVIRONMENT=local` (또는 `test`) 등 필요한 값을 직접 지정합니다.
- 로컬 개발 시 혹은 테스트 시 의존성 설치:
  ```bash
  cd patient && uv sync
  cd ../admin && uv sync
  cd ../gateway && uv sync
  ```
- 데이터베이스는 Docker MySQL 8.0을 사용합니다(`docker-compose.yml` 참고).

## 실행 방법
- Docker Compose 실행 (루트에서 실행):
  ```bash
  docker compose up --build
  ```
- 서비스 포트 및 라우팅:
  - Gateway: `http://localhost:8000`
  - Patient API: `http://localhost:8001`
  - Admin API: `http://localhost:8002`
- 개별 서비스 수동 실행 시에는 각 디렉터리에서 `uv run uvicorn app:app --host 0.0.0.0 --port <포트>`를 사용할 수 있습니다.

## 테스트 실행 방법
1. 테스트 전용 DB 컨테이너 실행 (`assignment_1/` 기준):
   ```bash
   docker build -f Dockerfile.test-db -t hospital-test-db .
   docker run --rm -d --name hospital_test_db -p 3309:3306 hospital-test-db
   ```

2. Admin 앱 테스트
   - 직접 명령:
     ```bash
     cd admin
     ENVIRONMENT=test uv run pytest
     ```
   - 스크립트 활용 (권한이 없다면 먼저 `chmod +x test.sh`):
     ```bash
     cd admin
     chmod +x test.sh
     ./test.sh
     ```

3. Patient 앱 테스트
   - 직접 명령:
     ```bash
     cd patient
     ENVIRONMENT=test uv run pytest
     ```
   - 스크립트 활용 (권한이 없다면 먼저 `chmod +x test.sh`):
     ```bash
     cd patient
     chmod +x test.sh
     ./test.sh
     ```

4. 테스트 종료 후 컨테이너 정리:
   ```bash
   docker stop hospital_test_db
   ```

## API 접근 방법
- Gateway (프록시): `http://localhost:8000`
  - Patient API
    - `GET http://localhost:8000/api/v1/patient/doctors`
    - `GET http://localhost:8000/api/v1/patient/appointments`
    - `POST http://localhost:8000/api/v1/patient/appointments`
    - `PATCH http://localhost:8000/api/v1/patient/appointments/{appointment_id}/cancel`
  - Admin API
    - `GET http://localhost:8000/api/v1/admin/doctors`
    - `PATCH http://localhost:8000/api/v1/admin/appointments/{appointment_id}/status`
    - `GET http://localhost:8000/api/v1/admin/appointments/statistics`
- 상세 엔드포인트/예시: [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)

## AI 활용 방식
- 요구사항 분석 및 리팩토링 아이디어 정리에 AI 도구를 사용해 검토 시간을 단축했습니다.
- 중복 코드 탐색, 테스트 시나리오 보강, 병렬 처리 최적화 등에 대해 AI와 질의하며 구조 개선 방향을 수립했습니다.
- 생성형 AI가 제안한 코드는 참고만 하고 직접 검증해 반영함으로써 일관된 코드 스타일과 도메인 규칙을 유지했습니다.

