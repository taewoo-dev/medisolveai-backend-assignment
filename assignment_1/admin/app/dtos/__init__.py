from app.dtos.appointment import (
    AppointmentDailyCountItem,
    AppointmentListItemResponse,
    AppointmentListResponse,
    AppointmentStatisticsResponse,
    AppointmentStatusCountItem,
    AppointmentStatusUpdateRequest,
    AppointmentSummaryData,
    AppointmentTimeslotCountItem,
    AppointmentVisitTypeCountItem,
)
from app.dtos.doctor import (
    DoctorCreateRequest,
    DoctorResponse,
    DoctorSummaryData,
    DoctorUpdateRequest,
)
from app.dtos.hospital_slot import (
    HospitalSlotCreateRequest,
    HospitalSlotResponse,
    HospitalSlotSummaryData,
    HospitalSlotUpdateRequest,
)
from app.dtos.treatment import (
    TreatmentCreateRequest,
    TreatmentResponse,
    TreatmentSummaryData,
    TreatmentUpdateRequest,
)

__all__ = [
    "DoctorCreateRequest",
    "DoctorResponse",
    "DoctorSummaryData",
    "DoctorUpdateRequest",
    "TreatmentCreateRequest",
    "TreatmentResponse",
    "TreatmentSummaryData",
    "TreatmentUpdateRequest",
    "HospitalSlotCreateRequest",
    "HospitalSlotResponse",
    "HospitalSlotSummaryData",
    "HospitalSlotUpdateRequest",
    "AppointmentListItemResponse",
    "AppointmentListResponse",
    "AppointmentStatusUpdateRequest",
    "AppointmentSummaryData",
    "AppointmentStatisticsResponse",
    "AppointmentStatusCountItem",
    "AppointmentDailyCountItem",
    "AppointmentTimeslotCountItem",
    "AppointmentVisitTypeCountItem",
]
