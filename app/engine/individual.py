"""
Định nghĩa Cá thể (Individual) - Một phương án lịch trực hoàn chỉnh
"""
import random
from typing import List, Dict, Set
from datetime import datetime, timedelta
from app.schemas.schedule import Staff, Position, Shift

class Individual:
    """
    Cá thể = Vector 30 chiều (30 ngày)
    Mỗi ngày chứa thông tin phân công đầy đủ cho 3 ca
    """
    
    def __init__(self, staff: List[Staff], positions: List[Position], 
                 shifts: List[Shift], days: int = 30):
        self.staff = staff
        self.positions = positions
        self.shifts = shifts
        self.days = days
        
        # Lịch trực: List[Dict] với 30 phần tử
        # Mỗi phần tử là 1 ngày với cấu trúc:
        # {
        #   "date": "2025-12-01",
        #   "day_of_week": "Monday",
        #   "is_weekend": False,
        #   "shifts": {
        #     "morning": {"PK_NOI_001": [staff_ids], ...},
        #     "afternoon": {...},
        #     "night": {...}
        #   }
        # }
        self.schedule: List[Dict] = []
        
        # Metadata
        self.fitness_score: float = 0.0
        self.hard_violations: int = 0
        self.soft_violations: int = 0
        self.is_valid: bool = False
        
        # Thống kê
        self.stats = {
            "total_shifts": 0,
            "shift_per_staff": {},
            "night_shifts_per_staff": {},
            "weekend_shifts_per_staff": {}
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
                "is_holiday": False,
                "shifts": {}
            }
            
            # Khởi tạo 3 ca
            for shift in self.shifts:
                shift_assignments = {}
                
                # Phân công cho từng vị trí
                for position in self.positions:
                    # Lọc nhân viên phù hợp chuyên môn
                    eligible_staff = [
                        s for s in self.staff
                        if (s.specialty == position.specialty_required and
                            current_date.strftime("%Y-%m-%d") not in s.leave_dates)
                    ]
                    
                    if not eligible_staff:
                        shift_assignments[position.name] = []
                        continue
                    
                    # Chọn ngẫu nhiên bác sĩ và điều dưỡng
                    doctors = [s for s in eligible_staff if s.role == "BacSi"]
                    nurses = [s for s in eligible_staff if s.role == "DieuDuong"]
                    
                    assigned = []
                    
                    # Chọn bác sĩ
                    if doctors and position.required_doctors > 0:
                        selected_doctors = random.sample(
                            doctors, 
                            min(position.required_doctors, len(doctors))
                        )
                        assigned.extend([d.name for d in selected_doctors])
                    
                    # Chọn điều dưỡng
                    if nurses and position.required_nurses > 0:
                        selected_nurses = random.sample(
                            nurses,
                            min(position.required_nurses, len(nurses))
                        )
                        assigned.extend([n.name for n in selected_nurses])
                    
                    shift_assignments[position.name] = assigned
                
                day_schedule["shifts"][shift.name] = shift_assignments
            
            self.schedule.append(day_schedule)
    
    def get_staff_by_name(self, name: str) -> Staff:
        """Lấy thông tin nhân viên theo tên"""
        for s in self.staff:
            if s.name == name:
                return s
        return None
    
    def get_staff_schedule(self, staff_name: str) -> List[Dict]:
        """Lấy tất cả ca trực của 1 nhân viên"""
        result = []
        
        for day_idx, day in enumerate(self.schedule):
            for shift_name, positions_dict in day["shifts"].items():
                for position_name, staff_list in positions_dict.items():
                    if staff_name in staff_list:
                        result.append({
                            "day": day_idx + 1,
                            "date": day["date"],
                            "shift": shift_name,
                            "position": position_name
                        })
        
        return result
    
    def count_shifts(self, staff_name: str) -> int:
        """Đếm tổng số ca trực của nhân viên"""
        return len(self.get_staff_schedule(staff_name))
    
    def count_night_shifts(self, staff_name: str) -> int:
        """Đếm số ca đêm của nhân viên"""
        schedule = self.get_staff_schedule(staff_name)
        return sum(1 for s in schedule if s["shift"] == "night")
    
    def count_weekend_shifts(self, staff_name: str) -> int:
        """Đếm số ca cuối tuần của nhân viên"""
        weekend_count = 0
        for day in self.schedule:
            if day["is_weekend"]:
                for shift_name, positions_dict in day["shifts"].items():
                    for position_name, staff_list in positions_dict.items():
                        if staff_name in staff_list:
                            weekend_count += 1
        return weekend_count
    
    def is_working_on(self, staff_name: str, day_idx: int, shift_name: str = None) -> bool:
        """Kiểm tra nhân viên có làm việc vào ngày/ca cụ thể không"""
        if day_idx >= len(self.schedule):
            return False
        
        day = self.schedule[day_idx]
        
        if shift_name:
            # Kiểm tra ca cụ thể
            positions_dict = day["shifts"].get(shift_name, {})
            for position_name, staff_list in positions_dict.items():
                if staff_name in staff_list:
                    return True
        else:
            # Kiểm tra cả ngày
            for shift_name, positions_dict in day["shifts"].items():
                for position_name, staff_list in positions_dict.items():
                    if staff_name in staff_list:
                        return True
        
        return False
    
    def calculate_statistics(self):
        """Tính toán thống kê"""
        total_shifts = 0
        shift_per_staff = {}
        night_shifts_per_staff = {}
        weekend_shifts_per_staff = {}
        
        for staff_member in self.staff:
            name = staff_member.name
            shift_per_staff[name] = self.count_shifts(name)
            night_shifts_per_staff[name] = self.count_night_shifts(name)
            weekend_shifts_per_staff[name] = self.count_weekend_shifts(name)
            total_shifts += shift_per_staff[name]
        
        self.stats = {
            "total_shifts": total_shifts,
            "shift_per_staff": shift_per_staff,
            "night_shifts_per_staff": night_shifts_per_staff,
            "weekend_shifts_per_staff": weekend_shifts_per_staff
        }
    
    def copy(self):
        """Tạo bản sao của cá thể"""
        new_individual = Individual(self.staff, self.positions, self.shifts, self.days)
        
        # Deep copy schedule
        import copy
        new_individual.schedule = copy.deepcopy(self.schedule)
        
        # Copy metadata
        new_individual.fitness_score = self.fitness_score
        new_individual.hard_violations = self.hard_violations
        new_individual.soft_violations = self.soft_violations
        new_individual.is_valid = self.is_valid
        new_individual.stats = copy.deepcopy(self.stats)
        
        return new_individual
    
    def __repr__(self):
        return (f"Individual(fitness={self.fitness_score:.2f}, "
                f"hard_violations={self.hard_violations}, "
                f"soft_violations={self.soft_violations})")