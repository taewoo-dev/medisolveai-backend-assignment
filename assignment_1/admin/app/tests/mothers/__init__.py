"""Admin App Test Mothers"""

from app.tests.mothers.appointment_mother import AppointmentMother
from app.tests.mothers.doctor_mother import DoctorMother
from app.tests.mothers.hospital_slot_mother import HospitalSlotMother
from app.tests.mothers.treatment_mother import TreatmentMother

__all__ = ["DoctorMother", "TreatmentMother", "HospitalSlotMother", "AppointmentMother"]
