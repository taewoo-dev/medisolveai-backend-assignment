"""
Admin App Models

관리자 앱에서 사용하는 SQLAlchemy 모델들
"""

from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.hospital_slot import HospitalSlot
from app.models.patient import Patient
from app.models.treatment import Treatment

__all__ = [
    "Appointment",
    "Doctor",
    "HospitalSlot",
    "Patient",
    "Treatment",
]
