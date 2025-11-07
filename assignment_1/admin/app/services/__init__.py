from app.services.appointment_service import (
    service_get_appointment_daily_counts,
    service_get_appointment_status_counts,
    service_get_appointment_timeslot_counts,
    service_get_appointment_visit_type_counts,
    service_get_appointments,
    service_update_appointment_status,
)
from app.services.doctor_service import (
    service_create_doctor,
    service_delete_doctor,
    service_get_doctors,
    service_update_doctor,
)
from app.services.hospital_slot_service import (
    service_create_hospital_slot,
    service_delete_hospital_slot,
    service_get_hospital_slots,
    service_update_hospital_slot,
)
from app.services.treatment_service import (
    service_create_treatment,
    service_delete_treatment,
    service_get_treatments,
    service_update_treatment,
)

__all__ = [
    "service_create_doctor",
    "service_delete_doctor",
    "service_get_doctors",
    "service_update_doctor",
    "service_create_treatment",
    "service_delete_treatment",
    "service_get_treatments",
    "service_update_treatment",
    "service_create_hospital_slot",
    "service_delete_hospital_slot",
    "service_get_hospital_slots",
    "service_update_hospital_slot",
    "service_get_appointments",
    "service_update_appointment_status",
    "service_get_appointment_status_counts",
    "service_get_appointment_daily_counts",
    "service_get_appointment_timeslot_counts",
    "service_get_appointment_visit_type_counts",
]
