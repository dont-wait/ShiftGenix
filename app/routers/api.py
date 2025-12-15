from fastapi import APIRouter
from app.schemas.schedule import ScheduleRequest, ScheduleResponse
from app.engine.ga_scheduler import generate_schedule
from app.utils.data_loader import load_staff_from_csv, load_positions_from_csv

router = APIRouter(tags=["Scheduler"])

@router.post("/schedule/generate", response_model=ScheduleResponse)
def generate_shift_schedule(payload: ScheduleRequest):
    result = generate_schedule(payload)
    return result

@router.get("/staff")
def get_staff_list():
    """Lấy danh sách nhân viên từ CSV"""
    staff_list = load_staff_from_csv()
    # Tương thích với cả Pydantic v1 và v2
    data = []
    for staff in staff_list:
        if hasattr(staff, 'model_dump'):
            data.append(staff.model_dump())
        else:
            data.append(staff.dict())
    return {"data": data}

@router.get("/positions")
def get_positions_list():
    """Lấy danh sách vị trí từ CSV"""
    positions_list = load_positions_from_csv()
    # Tương thích với cả Pydantic v1 và v2
    data = []
    for position in positions_list:
        if hasattr(position, 'model_dump'):
            data.append(position.model_dump())
        else:
            data.append(position.dict())
    return {"data": data}

@router.get("/department-staff")
def get_department_staff():
    """Lấy danh sách nhân viên theo từng phòng ban (eligible_positions)"""
    staff_list = load_staff_from_csv()
    department_map = {}
    for staff in staff_list:
        for dept in staff.eligible_positions:
            if dept not in department_map:
                department_map[dept] = []
            if hasattr(staff, 'model_dump'):
                department_map[dept].append(staff.model_dump())
            else:
                department_map[dept].append(staff.dict())
    return department_map
