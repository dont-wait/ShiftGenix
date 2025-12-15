"""
Fitness Function - Đánh giá chất lượng cá thể
Dựa trên ràng buộc cứng và ràng buộc mềm từ tài liệu
"""
from typing import Dict
from app.engine.individual import Individual
import statistics

class FitnessEvaluator:
    """Đánh giá fitness cho cá thể"""
    
    # Trọng số mặc định (có thể điều chỉnh)
    DEFAULT_WEIGHTS = {
        "fair_distribution": 0.30,      # Phân bổ đều ca khó
        "workload_balance": 0.25,        # Cân bằng khối lượng
        "respect_preferences": 0.20,     # Ưu tiên nguyện vọng
        "experience_mix": 0.15,          # Kết hợp kinh nghiệm
        "minimize_overtime": 0.10        # Giảm làm thêm
    }
    
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.penalty_hard = -1000  # Phạt vi phạm ràng buộc cứng
    
    def evaluate(self, individual: Individual) -> float:
        """
        Đánh giá fitness tổng thể
        Returns: điểm fitness (càng cao càng tốt)
        """
        # Tính thống kê trước
        individual.calculate_statistics()
        
        # Bước 1: Kiểm tra ràng buộc cứng
        hard_violations = self.check_hard_constraints(individual)
        individual.hard_violations = hard_violations
        
        # Nếu vi phạm ràng buộc cứng → fitness rất thấp
        if hard_violations > 0:
            individual.is_valid = False
            individual.fitness_score = self.penalty_hard * hard_violations
            return individual.fitness_score
        
        # Bước 2: Tính điểm ràng buộc mềm (0-1000)
        individual.is_valid = True
        soft_score = self.calculate_soft_score(individual)
        individual.fitness_score = soft_score
        
        return individual.fitness_score
    
    def check_hard_constraints(self, individual: Individual) -> int:
        """
        Kiểm tra tất cả ràng buộc cứng
        Returns: số lượng vi phạm
        """
        violations = 0
        
        # HC1: Không trực 2 ca trong 1 ngày
        violations += self.check_no_double_shift(individual)
        
        # HC2: Nghỉ tối thiểu 12 giờ giữa các ca
        violations += self.check_minimum_rest(individual)
        
        # HC3: Tối đa 3 ca đêm liên tiếp
        violations += self.check_consecutive_nights(individual)
        
        # HC4: Không trực khi nghỉ phép
        violations += self.check_leave_dates(individual)
        
        # HC5: Mỗi vị trí phải đủ nhân viên
        violations += self.check_minimum_coverage(individual)
        
        # HC6: Tối đa 40 giờ/tuần (check mỗi tuần)
        violations += self.check_max_hours_per_week(individual)
        
        return violations
    
    def check_no_double_shift(self, individual: Individual) -> int:
        """HC1: Không trực 2 ca trong 1 ngày"""
        violations = 0
        
        for staff_member in individual.staff:
            name = staff_member.name
            for day_idx in range(individual.days):
                shifts_today = 0
                day = individual.schedule[day_idx]
                
                for shift_name in ["morning", "afternoon", "night"]:
                    positions_dict = day["shifts"].get(shift_name, {})
                    for position_name, staff_list in positions_dict.items():
                        if name in staff_list:
                            shifts_today += 1
                
                if shifts_today > 1:
                    violations += 1
        
        return violations
    
    def check_minimum_rest(self, individual: Individual) -> int:
        """HC2: Nghỉ ít nhất 12 giờ giữa các ca"""
        violations = 0
        
        for staff_member in individual.staff:
            name = staff_member.name
            
            for day_idx in range(individual.days - 1):
                # Kiểm tra ca đêm hôm nay (kết thúc 7h sáng mai)
                # và ca sáng ngày mai (bắt đầu 7h)
                worked_night = individual.is_working_on(name, day_idx, "night")
                worked_morning_next = individual.is_working_on(name, day_idx + 1, "morning")
                
                if worked_night and worked_morning_next:
                    # Vi phạm: ca đêm kết thúc 7h, ca sáng bắt đầu 7h
                    # → Không có thời gian nghỉ
                    violations += 1
                
                # Kiểm tra ca chiều → ca đêm (nghỉ 8 giờ < 12 giờ)
                worked_afternoon = individual.is_working_on(name, day_idx, "afternoon")
                worked_night_same = individual.is_working_on(name, day_idx, "night")
                
                if worked_afternoon and worked_night_same:
                    # Ca chiều: 15h-23h
                    # Ca đêm: 23h-7h
                    # Nghỉ 0 giờ → Vi phạm
                    violations += 1
        
        return violations
    
    def check_consecutive_nights(self, individual: Individual) -> int:
        """HC3: Tối đa 3 ca đêm liên tiếp"""
        violations = 0
        
        for staff_member in individual.staff:
            name = staff_member.name
            consecutive_nights = 0
            max_consecutive = 0
            
            for day_idx in range(individual.days):
                if individual.is_working_on(name, day_idx, "night"):
                    consecutive_nights += 1
                    max_consecutive = max(max_consecutive, consecutive_nights)
                else:
                    consecutive_nights = 0
            
            if max_consecutive > staff_member.max_consecutive_night_shifts:
                violations += 1
        
        return violations
    
    def check_leave_dates(self, individual: Individual) -> int:
        """HC4: Không xếp trực khi nghỉ phép"""
        violations = 0
        
        for staff_member in individual.staff:
            name = staff_member.name
            
            for leave_date in staff_member.leave_dates:
                # Tìm ngày trong schedule
                for day_idx, day in enumerate(individual.schedule):
                    if day["date"] == leave_date:
                        if individual.is_working_on(name, day_idx):
                            violations += 1
                        break
        
        return violations
    
    def check_minimum_coverage(self, individual: Individual) -> int:
        """HC5: Mỗi vị trí phải đủ nhân viên (1 BS + 1 ĐD)"""
        violations = 0
        
        for day in individual.schedule:
            for shift_name in ["morning", "afternoon", "night"]:
                positions_dict = day["shifts"].get(shift_name, {})
                
                for position in individual.positions:
                    staff_list = positions_dict.get(position.name, [])
                    
                    # Đếm bác sĩ và điều dưỡng
                    doctors = sum(1 for s_name in staff_list 
                                 if individual.get_staff_by_name(s_name).role == "BacSi")
                    nurses = sum(1 for s_name in staff_list 
                                if individual.get_staff_by_name(s_name).role == "DieuDuong")
                    
                    if doctors < position.required_doctors:
                        violations += 1
                    if nurses < position.required_nurses:
                        violations += 1
        
        return violations
    
    def check_max_hours_per_week(self, individual: Individual) -> int:
        """HC6: Tối đa 40 giờ/tuần"""
        violations = 0
        
        # Giả định mỗi ca = 8 giờ
        hours_per_shift = 8
        
        for staff_member in individual.staff:
            name = staff_member.name
            
            # Kiểm tra 4 tuần (30 ngày ≈ 4 tuần)
            for week in range(4):
                start_day = week * 7
                end_day = min(start_day + 7, individual.days)
                
                hours_this_week = 0
                for day_idx in range(start_day, end_day):
                    if individual.is_working_on(name, day_idx):
                        # Đếm số ca trong ngày
                        day = individual.schedule[day_idx]
                        for shift_name in ["morning", "afternoon", "night"]:
                            positions_dict = day["shifts"].get(shift_name, {})
                            for position_name, staff_list in positions_dict.items():
                                if name in staff_list:
                                    hours_this_week += hours_per_shift
                
                if hours_this_week > staff_member.max_hours_per_week:
                    violations += 1
        
        return violations
    
    def calculate_soft_score(self, individual: Individual) -> float:
        """Tính điểm ràng buộc mềm (0-1000)"""
        score = 0.0
        
        # SC1: Công bằng phân bổ ca khó (đêm, cuối tuần)
        score += self.score_fair_distribution(individual) * self.weights["fair_distribution"]
        
        # SC2: Cân bằng khối lượng công việc
        score += self.score_workload_balance(individual) * self.weights["workload_balance"]
        
        # SC3: Ưu tiên nguyện vọng cá nhân
        score += self.score_preferences(individual) * self.weights["respect_preferences"]
        
        # SC4: Kết hợp kinh nghiệm
        score += self.score_experience_mix(individual) * self.weights["experience_mix"]
        
        # SC5: Giảm làm thêm giờ
        score += self.score_minimize_overtime(individual) * self.weights["minimize_overtime"]
        
        return score * 1000  # Scale to 0-1000
    
    def score_fair_distribution(self, individual: Individual) -> float:
        """SC1: Phân bổ đều ca đêm và ca cuối tuần (0-1)"""
        night_counts = []
        weekend_counts = []
        
        for staff_member in individual.staff:
            name = staff_member.name
            night_counts.append(individual.stats["night_shifts_per_staff"][name])
            weekend_counts.append(individual.stats["weekend_shifts_per_staff"][name])
        
        # Tính độ lệch chuẩn (càng nhỏ càng công bằng)
        if len(night_counts) > 1:
            night_std = statistics.stdev(night_counts)
        else:
            night_std = 0
        
        if len(weekend_counts) > 1:
            weekend_std = statistics.stdev(weekend_counts)
        else:
            weekend_std = 0
        
        # Score: 1.0 khi std = 0 (hoàn toàn công bằng)
        # Giảm dần khi std tăng
        score = 1.0 - min(1.0, (night_std * 0.1 + weekend_std * 0.1))
        return max(0.0, score)
    
    def score_workload_balance(self, individual: Individual) -> float:
        """SC2: Cân bằng tổng số ca trực (0-1)"""
        shift_counts = list(individual.stats["shift_per_staff"].values())
        
        if len(shift_counts) > 1:
            std_dev = statistics.stdev(shift_counts)
            # Mục tiêu: std < 2 ca
            score = 1.0 - min(1.0, std_dev / 10.0)
        else:
            score = 1.0
        
        return max(0.0, score)
    
    def score_preferences(self, individual: Individual) -> float:
        """SC3: Ưu tiên nguyện vọng ca làm việc (0-1)"""
        total_shifts = 0
        matched_shifts = 0
        
        for staff_member in individual.staff:
            if not staff_member.preferred_shifts:
                continue
            
            name = staff_member.name
            schedule = individual.get_staff_schedule(name)
            
            for shift_info in schedule:
                total_shifts += 1
                if shift_info["shift"] in staff_member.preferred_shifts:
                    matched_shifts += 1
        
        if total_shifts == 0:
            return 1.0
        
        return matched_shifts / total_shifts
    
    def score_experience_mix(self, individual: Individual) -> float:
        """SC4: Kết hợp nhân viên có kinh nghiệm và mới (0-1)"""
        well_mixed = 0
        total_shifts = 0
        
        for day in individual.schedule:
            for shift_name in ["morning", "afternoon", "night"]:
                positions_dict = day["shifts"].get(shift_name, {})
                
                for position_name, staff_list in positions_dict.items():
                    if len(staff_list) < 2:
                        continue
                    
                    total_shifts += 1
                    
                    # Kiểm tra có sự kết hợp kinh nghiệm không
                    experience_levels = set()
                    for s_name in staff_list:
                        staff_obj = individual.get_staff_by_name(s_name)
                        if staff_obj:
                            experience_levels.add(staff_obj.experience_level)
                    
                    # Có ít nhất 2 mức kinh nghiệm khác nhau
                    if len(experience_levels) >= 2:
                        well_mixed += 1
        
        if total_shifts == 0:
            return 1.0
        
        return well_mixed / total_shifts
    
    def score_minimize_overtime(self, individual: Individual) -> float:
        """SC5: Giảm làm thêm giờ (0-1)"""
        total_overtime_hours = 0
        
        hours_per_shift = 8
        
        for staff_member in individual.staff:
            name = staff_member.name
            
            for week in range(4):
                start_day = week * 7
                end_day = min(start_day + 7, individual.days)
                
                hours_this_week = 0
                for day_idx in range(start_day, end_day):
                    if individual.is_working_on(name, day_idx):
                        day = individual.schedule[day_idx]
                        for shift_name in ["morning", "afternoon", "night"]:
                            positions_dict = day["shifts"].get(shift_name, {})
                            for position_name, staff_list in positions_dict.items():
                                if name in staff_list:
                                    hours_this_week += hours_per_shift
                
                if hours_this_week > staff_member.max_hours_per_week:
                    total_overtime_hours += (hours_this_week - staff_member.max_hours_per_week)
        
        # Score giảm theo số giờ làm thêm
        # Mục tiêu: 0 giờ làm thêm
        score = 1.0 - min(1.0, total_overtime_hours / 100.0)
        return max(0.0, score)