"""
Genetic Algorithm for Shift Scheduling
Thuật toán Di truyền để tối ưu hóa lịch trực
"""
import random
import time
from typing import List, Tuple
from app.schemas.schedule import ScheduleRequest, ScheduleResponse, DaySchedule
from app.engine.individual import Individual
from app.engine.fitness import FitnessEvaluator


class GeneticScheduler:
    """Thuật toán Di truyền cho bài toán xếp lịch"""
    
    def __init__(self, config: ScheduleRequest):
        self.config = config
        self.population: List[Individual] = []
        self.best_individual: Individual = None
        self.fitness_evaluator = FitnessEvaluator(
            weights=config.weights,
            min_hours_per_month=config.min_hours_per_month,
            max_consecutive_shifts=config.max_consecutive_shifts
        )
        
        # Lịch sử fitness qua các thế hệ
        self.fitness_history = []
    
    def initialize_population(self):
        """Khởi tạo quần thể ban đầu"""
        print(f"Khởi tạo quần thể với {self.config.population_size} cá thể...")
        
        for i in range(self.config.population_size):
            individual = Individual(
                staff=self.config.staff,
                departments=self.config.departments,
                shifts=self.config.shifts,
                days=self.config.days
            )
            individual.initialize_random()
            self.population.append(individual)
            
            if (i + 1) % 20 == 0:
                print(f"  Đã khởi tạo {i + 1}/{self.config.population_size}")
    
    def evaluate_population(self):
        """Đánh giá fitness cho toàn bộ quần thể"""
        for individual in self.population:
            self.fitness_evaluator.evaluate(individual)
        
        # Sắp xếp theo fitness (cao → thấp)
        self.population.sort(key=lambda x: x.fitness_score, reverse=True)
        
        # Cập nhật best individual
        if not self.best_individual or self.population[0].fitness_score > self.best_individual.fitness_score:
            self.best_individual = self.population[0].copy()
    
    def selection(self) -> List[Individual]:
        """Chọn lọc - Tournament Selection"""
        tournament_size = 5
        selected = []
        
        # Chọn 50% số lượng tốt nhất để làm cha mẹ
        num_parents = self.config.population_size // 2
        
        for _ in range(num_parents):
            # Chọn ngẫu nhiên tournament_size cá thể
            tournament = random.sample(self.population, tournament_size)
            # Chọn cá thể tốt nhất trong tournament
            winner = max(tournament, key=lambda x: x.fitness_score)
            selected.append(winner)
        
        return selected
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Lai ghép - Single Point Crossover theo ngày"""
        if random.random() > self.config.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        # Chọn điểm cắt ngẫu nhiên
        crossover_point = random.randint(1, self.config.days - 1)
        
        # Tạo 2 con
        child1 = Individual(
            staff=self.config.staff,
            departments=self.config.departments,
            shifts=self.config.shifts,
            days=self.config.days
        )
        child2 = Individual(
            staff=self.config.staff,
            departments=self.config.departments,
            shifts=self.config.shifts,
            days=self.config.days
        )
        
        # Child 1: Lấy crossover_point ngày đầu từ parent1, phần còn lại từ parent2
        child1.schedule = parent1.schedule[:crossover_point] + parent2.schedule[crossover_point:]
        
        # Child 2: Ngược lại
        child2.schedule = parent2.schedule[:crossover_point] + parent1.schedule[crossover_point:]
        
        return child1, child2
    
    def mutate(self, individual: Individual):
        """Đột biến - Hoán đổi ngẫu nhiên nhân viên trong 1 ca"""
        if random.random() > self.config.mutation_rate:
            return
        
        # Chọn ngẫu nhiên 1 ngày
        day_idx = random.randint(0, self.config.days - 1)
        day = individual.schedule[day_idx]
        
        # Chọn ngẫu nhiên 1 ca
        shift_name = random.choice(["morning", "afternoon", "night"])
        positions_dict = day["shifts"][shift_name]
        
        # Chọn ngẫu nhiên 1 vị trí
        if not positions_dict:
            return
        
        position_name = random.choice(list(positions_dict.keys()))
        current_staff = positions_dict[position_name]
        
        if not current_staff:
            return
        
        # Tìm vị trí tương ứng
        position = None
        for p in self.config.positions:
            if p.name == position_name:
                position = p
                break
        
        if not position:
            return
        
        # Lọc nhân viên phù hợp chuyên môn và không nghỉ phép
        eligible_staff = [
            s for s in self.config.staff
            if (s.specialty == position.specialty_required and
                day["date"] not in s.leave_dates)
        ]
        
        if not eligible_staff:
            return
        
        # Chọn ngẫu nhiên nhân viên mới
        # Lọc theo role hiện tại đang thiếu
        doctors_needed = position.required_doctors
        nurses_needed = position.required_nurses
        
        current_doctors = [s for s in current_staff 
                          if individual.get_staff_by_name(s).role == "BacSi"]
        current_nurses = [s for s in current_staff 
                         if individual.get_staff_by_name(s).role == "DieuDuong"]
        
        new_staff = []
        
        # Thêm bác sĩ nếu thiếu
        if len(current_doctors) < doctors_needed:
            available_doctors = [s for s in eligible_staff if s.role == "BacSi"]
            if available_doctors:
                new_doctor = random.choice(available_doctors)
                new_staff.append(new_doctor.name)
        
        # Thêm điều dưỡng nếu thiếu
        if len(current_nurses) < nurses_needed:
            available_nurses = [s for s in eligible_staff if s.role == "DieuDuong"]
            if available_nurses:
                new_nurse = random.choice(available_nurses)
                new_staff.append(new_nurse.name)
        
        # Cập nhật
        if new_staff:
            individual.schedule[day_idx]["shifts"][shift_name][position_name] = new_staff
    
    def evolve(self) -> Individual:
        """
        Chạy thuật toán Di truyền
        Returns: Cá thể tốt nhất
        """
        start_time = time.time()
        
        # Bước 1: Khởi tạo quần thể
        self.initialize_population()
        
        # Bước 2: Đánh giá ban đầu
        print("\nĐánh giá quần thể ban đầu...")
        self.evaluate_population()
        self.fitness_history.append(self.best_individual.fitness_score)
        
        print(f"Thế hệ 0: Best Fitness = {self.best_individual.fitness_score:.2f}, "
              f"Violations = {self.best_individual.hard_violations}")
        
        # Bước 3: Tiến hóa qua các thế hệ
        for generation in range(1, self.config.max_generations + 1):
            # 3.1 Chọn lọc
            parents = self.selection()
            
            # 3.2 Lai ghép và tạo thế hệ mới
            new_population = []
            
            # Giữ lại 10% cá thể tốt nhất (Elitism)
            elite_size = self.config.population_size // 10
            new_population.extend([ind.copy() for ind in self.population[:elite_size]])
            
            # Tạo con từ lai ghép
            while len(new_population) < self.config.population_size:
                parent1 = random.choice(parents)
                parent2 = random.choice(parents)
                
                child1, child2 = self.crossover(parent1, parent2)
                
                # 3.3 Đột biến
                self.mutate(child1)
                self.mutate(child2)
                
                new_population.append(child1)
                if len(new_population) < self.config.population_size:
                    new_population.append(child2)
            
            # 3.4 Thay thế quần thể
            self.population = new_population
            
            # 3.5 Đánh giá thế hệ mới
            self.evaluate_population()
            self.fitness_history.append(self.best_individual.fitness_score)
            
            # Log tiến trình
            if generation % 50 == 0 or generation == self.config.max_generations:
                print(f"Thế hệ {generation}: "
                      f"Best Fitness = {self.best_individual.fitness_score:.2f}, "
                      f"Hard Violations = {self.best_individual.hard_violations}, "
                      f"Soft Violations = {self.best_individual.soft_violations}")
            
            # Dừng sớm nếu đã đạt được lịch hoàn hảo
            if self.best_individual.hard_violations == 0 and self.best_individual.fitness_score >= 950:
                print(f"\nĐạt được lịch trực tối ưu tại thế hệ {generation}!")
                break
        
        computation_time = time.time() - start_time
        print(f"\n✓ Hoàn thành trong {computation_time:.2f} giây")
        
        return self.best_individual


def generate_schedule(payload: ScheduleRequest) -> ScheduleResponse:
    """
    API endpoint chính để tạo lịch trực
    """
    print("\n" + "="*60)
    print("BẮT ĐẦU TẠO LỊCH TRỰC")
    print("="*60)
    print(f"Nhân viên: {len(payload.staff)}")
    print(f"Vị trí: {len(payload.positions)}")
    print(f"Số ngày: {payload.days}")
    print(f"Quần thể: {payload.population_size}")
    print(f"Thế hệ: {payload.max_generations}")
    print("="*60 + "\n")
    
    # Tạo scheduler
    scheduler = GeneticScheduler(payload)
    
    # Chạy GA
    best_individual = scheduler.evolve()
    
    # Chuyển đổi sang response format
    schedule_days = []
    for day_data in best_individual.schedule:
        day_schedule = DaySchedule(
            date=day_data["date"],
            day_of_week=day_data["day_of_week"],
            is_weekend=day_data["is_weekend"],
            is_holiday=day_data["is_holiday"],
            shifts=day_data["shifts"]
        )
        schedule_days.append(day_schedule)
    
    # Tạo response
    response = ScheduleResponse(
        schedule=schedule_days,
        fitness_score=best_individual.fitness_score,
        hard_violations=best_individual.hard_violations,
        soft_violations=best_individual.soft_violations,
        statistics=best_individual.stats,
        generation=len(scheduler.fitness_history),
        computation_time=0.0  # Sẽ được cập nhật
    )
    
    return response