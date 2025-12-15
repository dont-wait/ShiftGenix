from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import date

class Staff(BaseModel):
    """Nhân viên y tế"""
    id: int
    name: str
    role: str  # "BacSi", "DieuDuong", "HoSinh", "KyThuatY"
    specialty: str  # "Nội khoa", "Ngoại khoa", "Sản khoa", "Nhi khoa"
    experience_level: str = "Có kinh nghiệm"  # "Mới", "Có kinh nghiệm", "Thâm niên"
    
    # Giới hạn thời gian
    max_hours_per_week: int = 40
    min_rest_hours: int = 12
    max_consecutive_night_shifts: int = 3
    
    # Ngày nghỉ phép
    leave_dates: List[str] = []
    
    # Nguyện vọng cá nhân
    preferred_shifts: List[str] = []  # ["morning", "afternoon", "night"]
    avoid_days: List[str] = []  # ["Monday", "Tuesday", ...]
    
    # Đặc điểm cá nhân
    is_pregnant: bool = False
    has_young_children: bool = False
    
    # Vị trí có thể trực
    eligible_positions: List[str] = []

class Shift(BaseModel):
    """Ca làm việc"""
    id: int
    name: str  # "morning", "afternoon", "night"
    start_time: str  # "07:00"
    end_time: str  # "15:00"
    duration_hours: int = 8

class Position(BaseModel):
    """Vị trí công việc (Phòng khám)"""
    id: int
    name: str  # "Phòng_khám_Nội", "Phòng_khám_Ngoại"
    required_doctors: int = 1
    required_nurses: int = 1
    specialty_required: str  # "Nội khoa", "Ngoại khoa"

class DemandPattern(BaseModel):
    """Mẫu nhu cầu bệnh nhân"""
    time_slot: str
    estimated_patients: int

class ScheduleRequest(BaseModel):
    """Request để tạo lịch trực"""
    staff: List[Staff]
    shifts: List[Shift]
    positions: List[Position]
    days: int = 30
    
    # Cấu hình GA
    population_size: int = 100
    max_generations: int = 500
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    
    # Trọng số ràng buộc mềm
    weights: Dict[str, float] = {
        "fair_distribution": 0.30,
        "workload_balance": 0.25,
        "respect_preferences": 0.20,
        "experience_mix": 0.15,
        "minimize_overtime": 0.10
    }

class DaySchedule(BaseModel):
    """Lịch trực của 1 ngày"""
    date: str
    day_of_week: str
    is_weekend: bool
    is_holiday: bool
    shifts: Dict[str, Dict[str, List[str]]]  # {shift_name: {position_name: [staff_ids]}}

class ScheduleResponse(BaseModel):
    """Response trả về lịch trực"""
    schedule: List[DaySchedule]
    fitness_score: float
    hard_violations: int
    soft_violations: int
    statistics: Dict[str, Any]
    generation: int
    computation_time: float