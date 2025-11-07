"""상수 모듈"""

from app.core.constants.appointment_status import AppointmentStatus
from app.core.constants.department import Department
from app.core.constants.error_messages import ErrorMessages
from app.core.constants.hospital_constants import HospitalOperationConstants
from app.core.constants.visit_type import VisitType

__all__ = [
    "AppointmentStatus",
    "Department",
    "ErrorMessages",
    "HospitalOperationConstants",
    "VisitType",
]
