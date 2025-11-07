-- ============================================================================
-- 피부과 예약 관리 시스템 데이터베이스 초기화 스크립트
-- ============================================================================

-- ============================================================================
-- 0. 데이터베이스 기본 설정
-- ============================================================================

-- 문자셋 및 콜레이션 설정
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results = utf8mb4;
SET character_set_server = utf8mb4;
SET collation_server = utf8mb4_unicode_ci;
SET collation_connection = utf8mb4_unicode_ci;

-- 외래키 체크 임시 비활성화 (테이블 생성 순서 문제 해결)
SET FOREIGN_KEY_CHECKS = 0;

-- SQL 모드 설정 (엄격한 모드)
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- ============================================================================
-- 1. 테이블 생성
-- ============================================================================

-- 의사 정보 테이블
CREATE TABLE doctors (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '의사 이름',
    department VARCHAR(50) NOT NULL COMMENT '진료과 (피부과, 성형외과 등)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE COMMENT '활성 상태 (퇴사시 FALSE)',
    
    INDEX idx_doctors_active (is_active),
    INDEX idx_doctors_department_active (department, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='의사 정보';

-- 진료항목 테이블
CREATE TABLE treatments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '진료항목명 (기본상담, 레이저시술 등)',
    duration_minutes INT NOT NULL COMMENT '소요시간 (30분 단위)',
    price DECIMAL(10,2) NOT NULL COMMENT '가격',
    description TEXT COMMENT '진료항목 설명',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE COMMENT '활성 상태',
    
    CONSTRAINT chk_duration_30min CHECK (duration_minutes % 30 = 0),
    CONSTRAINT chk_duration_positive CHECK (duration_minutes > 0),
    CONSTRAINT chk_price_positive CHECK (price >= 0),
    
    INDEX idx_treatments_active (is_active),
    INDEX idx_treatments_active_duration (is_active, duration_minutes)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='진료항목 정보';

-- 환자 정보 테이블
CREATE TABLE patients (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '환자 이름',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT '연락처 (인증 및 조회용)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='환자 정보';

-- 병원 시간대별 수용 인원 설정 테이블
CREATE TABLE hospital_slots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    start_time TIME NOT NULL COMMENT '시간대 시작 (30분 단위)',
    end_time TIME NOT NULL COMMENT '시간대 종료 (30분 단위)', 
    max_capacity INT NOT NULL DEFAULT 3 COMMENT '해당 시간대 최대 수용 인원',
    day_of_week ENUM('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY') 
        DEFAULT NULL COMMENT '요일별 설정 (NULL이면 모든 요일 적용)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE COMMENT '활성 상태',
    
    CONSTRAINT chk_capacity_positive CHECK (max_capacity > 0),
    CONSTRAINT chk_time_order CHECK (start_time < end_time),
    
    UNIQUE KEY unique_slot_time (start_time, end_time, day_of_week),
    INDEX idx_day_of_week (day_of_week),
    INDEX idx_hospital_slots_active_time (is_active, start_time, end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='병원 시간대별 수용 인원 설정';

-- 예약 정보 테이블 (핵심 테이블)
CREATE TABLE appointments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doctor_id BIGINT NOT NULL COMMENT '담당 의사',
    patient_id BIGINT NOT NULL COMMENT '환자',
    treatment_id BIGINT NOT NULL COMMENT '진료항목',
    appointment_datetime DATETIME NOT NULL COMMENT '예약 시작 일시 (15분 단위)',
    status ENUM('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED') 
        NOT NULL DEFAULT 'PENDING' COMMENT '예약 상태',
    visit_type ENUM('FIRST_VISIT', 'RETURN_VISIT') 
        NOT NULL COMMENT '초진/재진 (예약 생성시 자동 판단)',
    memo TEXT COMMENT '예약 메모',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 외래키 제약조건
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT, 
    FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE RESTRICT,
    
    -- 성능 최적화 인덱스
    INDEX idx_appointments_doctor_datetime_status (doctor_id, appointment_datetime, status),
    INDEX idx_appointments_treatment_datetime_status (treatment_id, appointment_datetime, status),
    INDEX idx_appointments_patient_status_datetime (patient_id, status, appointment_datetime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='예약 정보';

-- ============================================================================
-- 2. 스키마 생성 완료
-- ============================================================================
-- 


-- 외래키 체크 재활성화
SET FOREIGN_KEY_CHECKS = 1;

-- 스키마 생성 완료 메시지
SELECT '데이터베이스 스키마 생성이 완료되었습니다.' as message;
