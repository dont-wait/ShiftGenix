"""
Định nghĩa Cá thể (Individual) đơn giản
Một phương án lịch trực hoàn chỉnh
"""
import random
from typing import List, Dict
from datetime import datetime, timedelta
from app.schemas.schedule import Staff, Department, Shift

class Individual:
    """
    Cá thể = Vector 30 chiều (30 ngày)
    Mỗi ngày chứa thông tin phân công cho 3 ca
    """
    
    def __init__(self, staff: List[Staff], departments: List[Department], 
                 shifts: List[Shift], days: int = 30):
        self.staff = staff
        self.departments = departments
        self.shifts = shifts
        self.days = days
        
        # Lịch trực: List[Dict]
        self.schedule: List[Dict] = []
        
        # Metadata
        self.fitness_score: float = 0.0
        self.hard_violations: int = 0
        self.soft_violations: int = 0
        self.is_valid: bool = False
        
        # Thống kê
        self.stats = {
            "total_shifts": 0,
            "hours_per_staff": {},
            "shifts_per_staff": {}
        }
    
    def initialize_random(self):
        """Khởi tạo lịch trực ngẫu nhiên"""
        start_date = datetime(2025, 12, 1)
        
        for day_idx in range(self.days):
            current_date = start_date + timedelta(days=day_idx)
            day_of_week = current_date.strftime("%A")
            is_weekend = day_of_week in ["Saturday", "Sunday"]
            
            day_schedule = {
                "date": current_date.strftime("%Y-%m-%d"),
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "shifts": {}
            }
            
            # Khởi tạo 3 ca
            for shift in self.shifts:
                shift_assignments = {}
                
                # Phân công cho từng khoa
                for department in self.departments:
                    # Lọc nhân viên thuộc khoa này
                    eligible_staff = [
                        s for s in self.staff
                        if s.department == department.name
                    ]
                    
                    if not eligible_staff:
                        shift_assignments[department.name] = []
                        continue
                    
                    # Chọn ngẫu nhiên số lượng nhân viên cần thiết
                    num_needed = department.required_staff_per_shift
                    selected = random.sample(
                        eligible_staff,
                        min(num_needed, len(eligible_staff))
                    )
                    
                    shift_assignments[department.name] = [s.staff_id for s in selected]
                
                day_schedule["shifts"][shift.name] = shift_assignments
            
            self.schedule.append(day_schedule)
    
    def get_staff_by_id(self, staff_id: str) -> Staff:
        """Lấy thông tin nhân viên theo ID"""
        for s in self.staff:
            if s.staff_id == staff_id:
                return s
        return None
    
    def get_staff_schedule(self, staff_id: str) -> List[Dict]:
        """Lấy tất cả ca trực của 1 nhân viên"""
        result = []
        
        for day_idx, day in enumerate(self.schedule):
            for shift_name, departments_dict in day["shifts"].items():
                for department_name, staff_list in departments_dict.items():
                    if staff_id in staff_list:
                        result.append({
                            "day": day_idx + 1,
                            "date": day["date"],
                            "shift": shift_name,
                            "department": department_name
                        })
        
        return result
    
    def count_shifts(self, staff_id: str) -> int:
        """Đếm tổng số ca trực của nhân viên"""
        return len(self.get_staff_schedule(staff_id))
    
    def calculate_hours(self, staff_id: str) -> int:
        """Tính tổng số giờ làm việc của nhân viên"""
        schedule = self.get_staff_schedule(staff_id)
        staff_obj = self.get_staff_by_id(staff_id)
        
        if not staff_obj:
            return 0
        
        total_hours = len(schedule) * staff_obj.shift_duration_hours
        return total_hours
    
    def is_working_on(self, staff_id: str, day_idx: int, shift_name: str = None) -> bool:
        """Kiểm tra nhân viên có làm việc vào ngày/ca cụ thể không"""
        if day_idx >= len(self.schedule):
            return False
        
        day = self.schedule[day_idx]
        
        if shift_name:
            # Kiểm tra ca cụ thể
            departments_dict = day["shifts"].get(shift_name, {})
            for department_name, staff_list in departments_dict.items():
                if staff_id in staff_list:
                    return True
        else:
            # Kiểm tra cả ngày
            for shift_name, departments_dict in day["shifts"].items():
                for department_name, staff_list in departments_dict.items():
                    if staff_id in staff_list:
                        return True
        
        return False
    
    def calculate_statistics(self):
        """Tính toán thống kê"""
        total_shifts = 0
        hours_per_staff = {}
        shifts_per_staff = {}
        
        for staff_member in self.staff:
            staff_id = staff_member.staff_id
            shifts_per_staff[staff_id] = self.count_shifts(staff_id)
            hours_per_staff[staff_id] = self.calculate_hours(staff_id)
            total_shifts += shifts_per_staff[staff_id]
        
        self.stats = {
            "total_shifts": total_shifts,
            "hours_per_staff": hours_per_staff,
            "shifts_per_staff": shifts_per_staff
        }
    
    def copy(self):
        """Tạo bản sao của cá thể"""
        new_individual = Individual(self.staff, self.departments, self.shifts, self.days)
        
        import copy
        new_individual.schedule = copy.deepcopy(self.schedule)
        new_individual.fitness_score = self.fitness_score
        new_individual.hard_violations = self.hard_violations
        new_individual.soft_violations = self.soft_violations
        new_individual.is_valid = self.is_valid
        new_individual.stats = copy.deepcopy(self.stats)
        
        return new_individual
    
    def __repr__(self):
        return (f"Individual(fitness={self.fitness_score:.2f}, "
                f"violations={self.hard_violations})")