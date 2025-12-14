from fastapi import APIRouter
from app.schemas.schedule import ScheduleRequest, ScheduleResponse
from app.engine.ga_scheduler import generate_schedule

router = APIRouter(tags=["Scheduler"])

@router.post("/schedule/generate", response_model=ScheduleResponse)
def generate_shift_schedule(payload: ScheduleRequest):
    result = generate_schedule(payload)
    return result
