"""
Appointment DTOs
"""

from .appointment_response import AppointmentResponse
from .appointment_with_treatment_data import AppointmentWithTreatmentData
from .available_time_response import AvailableTimeResponse
from .create_appointment_request import CreateAppointmentRequest

__all__ = [
    "CreateAppointmentRequest",
    "AppointmentResponse",
    "AppointmentWithTreatmentData",
    "AvailableTimeResponse",
]
