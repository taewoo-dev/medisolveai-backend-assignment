"""환경 설정 관리"""

from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(StrEnum):
    LOCAL = "local"
    STAGE = "stage"
    PROD = "prod"
    TEST = "test"


class Settings(BaseSettings):
    """애플리케이션 환경 설정"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    # ============================================================================
    # 환경 설정
    # ============================================================================

    environment: Env = Field(default=Env.LOCAL, description="실행 환경")

    # ============================================================================
    # 서버 설정
    # ============================================================================

    # Patient API
    patient_api_host: str = Field(default="0.0.0.0", description="Patient API 호스트")
    patient_api_port: int = Field(default=8001, description="Patient API 포트")

    # Admin API
    admin_api_host: str = Field(default="0.0.0.0", description="Admin API 호스트")
    admin_api_port: int = Field(default=8002, description="Admin API 포트")

    # Gateway
    gateway_host: str = Field(default="0.0.0.0", description="Gateway 호스트")
    gateway_port: int = Field(default=8000, description="Gateway 포트")

    # ============================================================================
    # 데이터베이스 설정
    # ============================================================================

    db_host: str = Field(default="localhost", description="데이터베이스 호스트")
    db_port: int = Field(default=3308, description="데이터베이스 포트")
    db_user: str = Field(default="hospital_user", description="데이터베이스 사용자")
    db_password: str = Field(default="hospital_pass", description="데이터베이스 비밀번호")
    db_name: str = Field(default="hospital_management", description="데이터베이스 이름")

    # ============================================================================
    # 비즈니스 로직 설정
    # ============================================================================

    # 예약 관련 설정
    appointment_slot_minutes: int = Field(default=15, description="예약 시간 간격 (분)")
    treatment_unit_minutes: int = Field(default=30, description="진료 시간 단위 (분)")
    default_capacity_per_slot: int = Field(default=3, description="시간대별 기본 수용 인원")

    # 병원 운영 시간
    hospital_open_time: str = Field(default="09:00", description="병원 오픈 시간")
    hospital_close_time: str = Field(default="18:00", description="병원 마감 시간")
    lunch_start_time: str = Field(default="12:00", description="점심시간 시작")
    lunch_end_time: str = Field(default="13:00", description="점심시간 종료")

    # 예약 제한 설정
    max_advance_booking_days: int = Field(default=30, description="최대 예약 가능 일수")
    min_advance_booking_hours: int = Field(default=2, description="최소 예약 시간 (시간)")

    # ============================================================================
    # 계산된 속성들
    # ============================================================================

    @property
    def database_url(self) -> str:
        """비동기 데이터베이스 URL 생성"""
        if self.is_test:
            return (
                f"mysql+asyncmy://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:3309/hospital_management_test"
                f"?charset=utf8mb4"
            )
        return (
            f"mysql+asyncmy://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset=utf8mb4"
        )

    @property
    def is_local(self) -> bool:
        """로컬 환경 여부"""
        return self.environment == Env.LOCAL

    @property
    def is_stage(self) -> bool:
        """스테이지 환경 여부"""
        return self.environment == Env.STAGE

    @property
    def is_prod(self) -> bool:
        """운영 환경 여부"""
        return self.environment == Env.PROD

    @property
    def is_test(self) -> bool:
        """테스트 환경 여부"""
        return self.environment == Env.TEST


# 전역 설정 인스턴스
settings = Settings()
