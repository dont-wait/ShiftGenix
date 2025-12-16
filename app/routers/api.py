from fastapi import APIRouter
from app.schemas.schedule import ScheduleRequest, ScheduleResponse
from app.engine.ga_scheduler import generate_schedule
from app.utils.data_loader import load_staff_from_csv, load_departments_from_csv

router = APIRouter(tags=["Scheduler"])

@router.post("/schedule/generate", response_model=ScheduleResponse)
def generate_shift_schedule(payload: ScheduleRequest):
    """
    Tạo lịch trực tự động sử dụng Genetic Algorithm
    
    Body mẫu:
    {
      "staff": [...],
      "departments": [...],
      "shifts": [...],
      "days": 30,
      "population_size": 100,
      "max_generations": 200
    }
    """
    result = generate_schedule(payload)
    return result

@router.get("/staff")
def get_staff_list():
    """Lấy danh sách nhân viên từ CSV"""
    staff_list = load_staff_from_csv("data/staff.csv")
    
    # Tương thích với cả Pydantic v1 và v2
    data = []
    for staff in staff_list:
        if hasattr(staff, 'model_dump'):
            data.append(staff.model_dump())
        else:
            data.append(staff.dict())
    
    return {
        "success": True,
        "count": len(data),
        "data": data
    }

@router.get("/departments")
def get_departments_list():
    """Lấy danh sách khoa/phòng ban từ CSV"""
    departments_list = load_departments_from_csv("data/departments.csv")
    
    # Tương thích với cả Pydantic v1 và v2
    data = []
    for department in departments_list:
        if hasattr(department, 'model_dump'):
            data.append(department.model_dump())
        else:
            data.append(department.dict())
    
    return {
        "success": True,
        "count": len(data),
        "data": data
    }

@router.get("/staff-by-department")
def get_staff_by_department():
    """Lấy danh sách nhân viên theo từng khoa"""
    staff_list = load_staff_from_csv("data/staff.csv")
    
    department_map = {}
    for staff in staff_list:
        dept = staff.department
        
        if dept not in department_map:
            department_map[dept] = []
        
        # Serialize staff object
        if hasattr(staff, 'model_dump'):
            department_map[dept].append(staff.model_dump())
        else:
            department_map[dept].append(staff.dict())
    
    return {
        "success": True,
        "departments": list(department_map.keys()),
        "data": department_map
    }

@router.get("/staff/{staff_id}")
def get_staff_by_id(staff_id: str):
    """Lấy thông tin chi tiết 1 nhân viên"""
    staff_list = load_staff_from_csv("data/staff.csv")
    
    for staff in staff_list:
        if staff.staff_id == staff_id:
            if hasattr(staff, 'model_dump'):
                return {"success": True, "data": staff.model_dump()}
            else:
                return {"success": True, "data": staff.dict()}
    
    return {
        "success": False,
        "message": f"Không tìm thấy nhân viên {staff_id}"
    }

@router.get("/statistics")
def get_statistics():
    """Thống kê tổng quan"""
    staff_list = load_staff_from_csv("data/staff.csv")
    departments_list = load_departments_from_csv("data/departments.csv")
    
    # Thống kê theo vai trò
    role_count = {}
    for staff in staff_list:
        role = staff.role
        role_count[role] = role_count.get(role, 0) + 1
    
    # Thống kê theo khoa
    dept_count = {}
    for staff in staff_list:
        dept = staff.department
        dept_count[dept] = dept_count.get(dept, 0) + 1
    
    # Thống kê kinh nghiệm
    total_experience = sum(s.years_of_experience for s in staff_list)
    avg_experience = total_experience / len(staff_list) if staff_list else 0
    
    # Thống kê hài lòng
    total_satisfaction = sum(s.satisfaction_score for s in staff_list)
    avg_satisfaction = total_satisfaction / len(staff_list) if staff_list else 0
    
    return {
        "success": True,
        "total_staff": len(staff_list),
        "total_departments": len(departments_list),
        "by_role": role_count,
        "by_department": dept_count,
        "average_experience": round(avg_experience, 1),
        "average_satisfaction": round(avg_satisfaction, 2)
    }

@router.get("/health")
def health_check():
    """Kiểm tra trạng thái API"""
    return {
        "status": "ok",
        "message": "ShiftGenix API is running",
        "version": "0.2.0-simple"
    }