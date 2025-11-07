from app.apis.v1.appointment_router import router as appointment_router
from app.apis.v1.doctor_router import router as doctor_router
from app.apis.v1.hospital_slot_router import router as hospital_slot_router
from app.apis.v1.treatment_router import router as treatment_router

__all__ = ["doctor_router", "treatment_router", "hospital_slot_router", "appointment_router"]
