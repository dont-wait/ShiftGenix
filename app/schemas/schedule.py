from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Staff(BaseModel):
    """Nhân viên y tế - Schema đơn giản"""
    staff_id: str  # S00000
    department: str  # Pediatrics, Surgery, etc.
    shift_duration_hours: int  # 8, 10, 12
    patient_load: int  # Số bệnh nhân/ca
    workdays_per_month: int  # Số ngày làm việc/tháng
    satisfaction_score: float  # Điểm hài lòng
    overtime_hours: int  # Giờ làm thêm
    years_of_experience: int  # Số năm kinh nghiệm
    previous_satisfaction_rating: float  # Đánh giá trước
    absenteeism_days: int  # Số ngày vắng mặt
    
    # Thêm thông tin bổ sung nếu cần
    role: str = "Doctor"  # Doctor, Nurse
    eligible_departments: List[str] = []  # Các khoa có thể làm

class Department(BaseModel):
    """Khoa/Phòng ban"""
    id: str
    name: str  # Pediatrics, Surgery, etc.
    required_staff_per_shift: int = 1  # Số nhân viên tối thiểu/ca
    max_patient_load: int = 100  # Tải bệnh nhân tối đa

class Shift(BaseModel):
    """Ca làm việc"""
    id: int
    name: str  # "morning", "afternoon", "night"
    start_time: str  # "07:00"
    end_time: str  # "15:00"
    duration_hours: int = 8

class ScheduleRequest(BaseModel):
    """Request để tạo lịch trực"""
    staff: List[Staff]
    departments: List[Department]
    shifts: List[Shift]
    days: int = 30
    
    # Cấu hình GA
    population_size: int = 100
    max_generations: int = 500
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    
    # Ràng buộc đơn giản
    min_hours_per_month: int = 160  # Tối thiểu 160 giờ/tháng
    max_consecutive_shifts: int = 2  # Không làm quá 2 ca liên tiếp
    
    # Trọng số ràng buộc mềm
    weights: Dict[str, float] = {
        "workload_balance": 0.40,        # Cân bằng khối lượng
        "satisfaction": 0.30,            # Tối ưu sự hài lòng
        "experience_distribution": 0.20, # Phân bổ kinh nghiệm
        "minimize_overtime": 0.10        # Giảm làm thêm
    }

class DaySchedule(BaseModel):
    """Lịch trực của 1 ngày"""
    date: str
    day_of_week: str
    is_weekend: bool
    shifts: Dict[str, Dict[str, List[str]]]  # {shift_name: {department: [staff_ids]}}

class ScheduleResponse(BaseModel):
    """Response trả về lịch trực"""
    schedule: List[DaySchedule]
    fitness_score: float
    hard_violations: int
    soft_violations: int
    statistics: Dict[str, Any]
    generation: int
    computation_time: float