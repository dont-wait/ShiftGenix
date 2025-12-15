"""
Script test Genetic Algorithm
Chạy: python test_ga.py
"""
from app.utils.data_loader import load_staff_from_csv, load_positions_from_csv
from app.schemas.schedule import ScheduleRequest, Shift
from app.engine.ga_scheduler import generate_schedule

def test_simple():
    """Test với dữ liệu đơn giản"""
    print("="*60)
    print("TEST 1: Lịch trực 7 ngày với cấu hình nhẹ")
    print("="*60)
    
    # Load data
    staff = load_staff_from_csv("app/data/staff.csv")
    positions = load_positions_from_csv("app/data/positions.csv")
    
    if not staff or not positions:
        print("❌ Không load được dữ liệu từ CSV!")
        print("   Đảm bảo file data/staff.csv và data/positions.csv tồn tại")
        return
    
    print(f"✓ Loaded {len(staff)} nhân viên")
    print(f"✓ Loaded {len(positions)} vị trí")
    
    # Tạo payload
    payload = ScheduleRequest(
        staff=staff[:10],  # Chỉ lấy 10 nhân viên đầu
        positions=positions[:2],  # Chỉ lấy 2 vị trí đầu
        shifts=[
            Shift(id=1, name="morning", start_time="07:00", end_time="15:00", duration_hours=8),
            Shift(id=2, name="afternoon", start_time="15:00", end_time="23:00", duration_hours=8),
            Shift(id=3, name="night", start_time="23:00", end_time="07:00", duration_hours=8)
        ],
        days=7,  # Chỉ 7 ngày để test nhanh
        population_size=30,
        max_generations=50,
        mutation_rate=0.1,
        crossover_rate=0.8
    )
    
    # Chạy GA
    result = generate_schedule(payload)
    
    # In kết quả
    print("\n" + "="*60)
    print("KẾT QUẢ")
    print("="*60)
    print(f"✓ Fitness Score: {result.fitness_score:.2f}/1000")
    print(f"✓ Hard Violations: {result.hard_violations}")
    print(f"✓ Soft Violations: {result.soft_violations}")
    print(f"✓ Số thế hệ: {result.generation}")
    print(f"✓ Thời gian: {result.computation_time:.2f}s")
    
    # Thống kê
    print("\nTHỐNG KÊ:")
    print(f"  - Tổng ca trực: {result.statistics['total_shifts']}")
    print(f"  - Trung bình ca/người: {result.statistics['total_shifts'] / len(staff[:10]):.1f}")
    
    # Hiển thị vài ngày đầu
    print("\nLỊCH TRỰC 3 NGÀY ĐẦU:")
    for i, day in enumerate(result.schedule[:3]):
        print(f"\n{day.date} ({day.day_of_week}):")
        for shift_name in ["morning", "afternoon", "night"]:
            shift_data = day.shifts.get(shift_name, {})
            print(f"  {shift_name}:")
            for position, staff_list in shift_data.items():
                print(f"    {position}: {', '.join(staff_list) if staff_list else 'Chưa xếp'}")
    
    if result.hard_violations == 0:
        print("\n✓ ✓ ✓ THÀNH CÔNG: Lịch trực hợp lệ!")
    else:
        print(f"\n⚠️ Có {result.hard_violations} vi phạm ràng buộc cứng")

def test_full():
    """Test với dữ liệu đầy đủ"""
    print("\n" + "="*60)
    print("TEST 2: Lịch trực 30 ngày đầy đủ")
    print("="*60)
    
    # Load full data
    staff = load_staff_from_csv("data/staff.csv")
    positions = load_positions_from_csv("data/positions.csv")
    
    print(f"✓ Loaded {len(staff)} nhân viên")
    print(f"✓ Loaded {len(positions)} vị trí")
    
    # Full payload
    payload = ScheduleRequest(
        staff=staff,
        positions=positions,
        shifts=[
            Shift(id=1, name="morning", start_time="07:00", end_time="15:00", duration_hours=8),
            Shift(id=2, name="afternoon", start_time="15:00", end_time="23:00", duration_hours=8),
            Shift(id=3, name="night", start_time="23:00", end_time="07:00", duration_hours=8)
        ],
        days=30,
        population_size=100,
        max_generations=200,
        mutation_rate=0.1,
        crossover_rate=0.8
    )
    
    # Chạy GA
    result = generate_schedule(payload)
    
    # In kết quả
    print("\n" + "="*60)
    print("KẾT QUẢ")
    print("="*60)
    print(f"✓ Fitness Score: {result.fitness_score:.2f}/1000")
    print(f"✓ Hard Violations: {result.hard_violations}")
    print(f"✓ Soft Violations: {result.soft_violations}")
    print(f"✓ Số thế hệ: {result.generation}")
    print(f"✓ Thời gian: {result.computation_time:.2f}s")
    
    if result.hard_violations == 0:
        print("\n✓ ✓ ✓ THÀNH CÔNG: Lịch trực 30 ngày hợp lệ!")
        
        # Phân tích chi tiết
        print("\nPHÂN TÍCH CHI TIẾT:")
        shift_counts = list(result.statistics['shift_per_staff'].values())
        print(f"  - Ca trực min: {min(shift_counts)}")
        print(f"  - Ca trực max: {max(shift_counts)}")
        print(f"  - Ca trực trung bình: {sum(shift_counts)/len(shift_counts):.1f}")
        
        night_counts = list(result.statistics['night_shifts_per_staff'].values())
        print(f"  - Ca đêm min: {min(night_counts)}")
        print(f"  - Ca đêm max: {max(night_counts)}")
    else:
        print(f"\n⚠️ Có {result.hard_violations} vi phạm ràng buộc cứng")

if __name__ == "__main__":
    import sys
    
    print("\n🧬 GENETIC ALGORITHM SCHEDULER TEST\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        test_full()
    else:
        test_simple()
        
        print("\n" + "="*60)
        print("Để chạy test đầy đủ 30 ngày:")
        print("  python test_ga.py full")
        print("="*60)