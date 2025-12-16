"""
Fitness Function đơn giản
Chỉ kiểm tra các ràng buộc cơ bản
"""
from typing import Dict
from app.engine.individual import Individual
import statistics

class FitnessEvaluator:
    """Đánh giá fitness đơn giản"""
    
    DEFAULT_WEIGHTS = {
        "workload_balance": 0.40,        # Cân bằng khối lượng
        "satisfaction": 0.30,            # Tối ưu sự hài lòng
        "experience_distribution": 0.20, # Phân bổ kinh nghiệm
        "minimize_overtime": 0.10        # Giảm làm thêm
    }
    
    def __init__(self, weights: Dict[str, float] = None, 
                 min_hours_per_month: int = 160,
                 max_consecutive_shifts: int = 2):
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.penalty_hard = -1000
        self.min_hours_per_month = min_hours_per_month
        self.max_consecutive_shifts = max_consecutive_shifts
    
    def evaluate(self, individual: Individual) -> float:
        """Đánh giá fitness"""
        individual.calculate_statistics()
        
        # Kiểm tra ràng buộc cứng
        hard_violations = self.check_hard_constraints(individual)
        individual.hard_violations = hard_violations
        
        if hard_violations > 0:
            individual.is_valid = False
            individual.fitness_score = self.penalty_hard * hard_violations
            return individual.fitness_score
        
        # Tính điểm ràng buộc mềm
        individual.is_valid = True
        soft_score = self.calculate_soft_score(individual)
        individual.fitness_score = soft_score
        
        return individual.fitness_score
    
    def check_hard_constraints(self, individual: Individual) -> int:
        """
        Kiểm tra ràng buộc cứng:
        1. Số giờ làm tối thiểu/tháng
        2. Không làm 2 ca liên tiếp
        3. Đủ nhân viên mỗi ca
        """
        violations = 0
        
        # HC1: Số giờ làm tối thiểu
        violations += self.check_minimum_hours(individual)
        
        # HC2: Không làm quá N ca liên tiếp
        violations += self.check_consecutive_shifts(individual)
        
        # HC3: Đủ nhân viên mỗi ca
        violations += self.check_minimum_coverage(individual)
        
        return violations
    
    def check_minimum_hours(self, individual: Individual) -> int:
        """HC1: Kiểm tra số giờ làm tối thiểu/tháng"""
        violations = 0
        
        for staff_member in individual.staff:
            staff_id = staff_member.staff_id
            total_hours = individual.calculate_hours(staff_id)
            
            if total_hours < self.min_hours_per_month:
                violations += 1
        
        return violations
    
    def check_consecutive_shifts(self, individual: Individual) -> int:
        """HC2: Không làm quá max_consecutive_shifts ca liên tiếp"""
        violations = 0
        
        for staff_member in individual.staff:
            staff_id = staff_member.staff_id
            consecutive_count = 0
            max_consecutive = 0
            
            for day_idx in range(individual.days):
                if individual.is_working_on(staff_id, day_idx):
                    consecutive_count += 1
                    max_consecutive = max(max_consecutive, consecutive_count)
                else:
                    consecutive_count = 0
            
            if max_consecutive > self.max_consecutive_shifts:
                violations += 1
        
        return violations
    
    def check_minimum_coverage(self, individual: Individual) -> int:
        """HC3: Đủ nhân viên mỗi ca"""
        violations = 0
        
        for day in individual.schedule:
            for shift_name in ["morning", "afternoon", "night"]:
                departments_dict = day["shifts"].get(shift_name, {})
                
                for department in individual.departments:
                    staff_list = departments_dict.get(department.name, [])
                    
                    if len(staff_list) < department.required_staff_per_shift:
                        violations += 1
        
        return violations
    
    def calculate_soft_score(self, individual: Individual) -> float:
        """Tính điểm ràng buộc mềm (0-1000)"""
        score = 0.0
        
        # SC1: Cân bằng khối lượng công việc
        score += self.score_workload_balance(individual) * self.weights["workload_balance"]
        
        # SC2: Tối ưu sự hài lòng
        score += self.score_satisfaction(individual) * self.weights["satisfaction"]
        
        # SC3: Phân bổ kinh nghiệm
        score += self.score_experience_distribution(individual) * self.weights["experience_distribution"]
        
        # SC4: Giảm làm thêm
        score += self.score_minimize_overtime(individual) * self.weights["minimize_overtime"]
        
        return score * 1000
    
    def score_workload_balance(self, individual: Individual) -> float:
        """SC1: Cân bằng số giờ làm việc (0-1)"""
        hours_list = list(individual.stats["hours_per_staff"].values())
        
        if len(hours_list) <= 1:
            return 1.0
        
        std_dev = statistics.stdev(hours_list)
        # Càng đều thì std_dev càng nhỏ
        score = 1.0 - min(1.0, std_dev / 100.0)
        return max(0.0, score)
    
    def score_satisfaction(self, individual: Individual) -> float:
        """SC2: Tối ưu sự hài lòng dựa trên khối lượng công việc (0-1)"""
        total_score = 0.0
        count = 0
        
        for staff_member in individual.staff:
            staff_id = staff_member.staff_id
            actual_hours = individual.stats["hours_per_staff"][staff_id]
            expected_hours = staff_member.workdays_per_month * staff_member.shift_duration_hours
            
            # Nếu làm đúng số giờ mong muốn → satisfaction cao
            if expected_hours > 0:
                ratio = actual_hours / expected_hours
                # Tốt nhất khi ratio gần 1.0
                satisfaction = 1.0 - abs(1.0 - ratio)
                total_score += max(0.0, satisfaction)
                count += 1
        
        return total_score / count if count > 0 else 0.0
    
    def score_experience_distribution(self, individual: Individual) -> float:
        """SC3: Phân bổ đều các mức kinh nghiệm trong mỗi ca (0-1)"""
        well_distributed = 0
        total_shifts = 0
        
        for day in individual.schedule:
            for shift_name in ["morning", "afternoon", "night"]:
                departments_dict = day["shifts"].get(shift_name, {})
                
                for department_name, staff_list in departments_dict.items():
                    if len(staff_list) < 2:
                        continue
                    
                    total_shifts += 1
                    
                    # Lấy mức kinh nghiệm
                    experience_levels = []
                    for staff_id in staff_list:
                        staff_obj = individual.get_staff_by_id(staff_id)
                        if staff_obj:
                            experience_levels.append(staff_obj.years_of_experience)
                    
                    # Có sự đa dạng về kinh nghiệm (có cả mới và cũ)
                    if len(experience_levels) >= 2:
                        exp_range = max(experience_levels) - min(experience_levels)
                        if exp_range >= 5:  # Chênh lệch ít nhất 5 năm
                            well_distributed += 1
        
        if total_shifts == 0:
            return 1.0
        
        return well_distributed / total_shifts
    
    def score_minimize_overtime(self, individual: Individual) -> float:
        """SC4: Giảm số giờ làm thêm (0-1)"""
        total_overtime = 0
        
        for staff_member in individual.staff:
            staff_id = staff_member.staff_id
            actual_hours = individual.stats["hours_per_staff"][staff_id]
            expected_hours = staff_member.workdays_per_month * staff_member.shift_duration_hours
            
            if actual_hours > expected_hours:
                total_overtime += (actual_hours - expected_hours)
        
        # Phạt theo tổng giờ làm thêm
        score = 1.0 - min(1.0, total_overtime / 500.0)
        return max(0.0, score)