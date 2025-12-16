import csv
from pathlib import Path
from typing import List
from app.schemas.schedule import Staff, Department

def load_staff_from_csv(filepath: str = "data/staff.csv") -> List[Staff]:
    """Đọc danh sách nhân viên từ file CSV"""
    staff_list = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse eligible departments (mặc định chỉ làm khoa của mình)
                eligible_departments = [row['department']]
                
                staff = Staff(
                    staff_id=row['staff_id'],
                    department=row['department'],
                    shift_duration_hours=int(row['shift_duration_hours']),
                    patient_load=int(row['patient_load']),
                    workdays_per_month=int(row['workdays_per_month']),
                    satisfaction_score=float(row['satisfaction_score']),
                    overtime_hours=int(row['overtime_hours']),
                    years_of_experience=int(row['years_of_experience']),
                    previous_satisfaction_rating=float(row['previous_satisfaction_rating']),
                    absenteeism_days=int(row['absenteeism_days']),
                    role=row.get('role', 'Doctor'),
                    eligible_departments=eligible_departments
                )
                staff_list.append(staff)
                
    except FileNotFoundError:
        print(f"❌ File {filepath} không tồn tại")
        return []
    except Exception as e:
        print(f"❌ Lỗi khi đọc file CSV: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    return staff_list


def load_departments_from_csv(filepath: str = "data/departments.csv") -> List[Department]:
    """Đọc danh sách khoa/phòng ban từ file CSV"""
    departments_list = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                department = Department(
                    id=row['id'],
                    name=row['name'],
                    required_staff_per_shift=int(row['required_staff_per_shift']),
                    max_patient_load=int(row['max_patient_load'])
                )
                departments_list.append(department)
                
    except FileNotFoundError:
        print(f"❌ File {filepath} không tồn tại")
        return []
    except Exception as e:
        print(f"❌ Lỗi khi đọc file CSV: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    return departments_list


def save_staff_to_csv(staff_list: List[Staff], filepath: str = "data/staff.csv"):
    """Lưu danh sách nhân viên vào file CSV"""
    try:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'staff_id', 'department', 'shift_duration_hours', 'patient_load',
                'workdays_per_month', 'satisfaction_score', 'overtime_hours',
                'years_of_experience', 'previous_satisfaction_rating', 'absenteeism_days', 'role'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for staff in staff_list:
                writer.writerow({
                    'staff_id': staff.staff_id,
                    'department': staff.department,
                    'shift_duration_hours': staff.shift_duration_hours,
                    'patient_load': staff.patient_load,
                    'workdays_per_month': staff.workdays_per_month,
                    'satisfaction_score': staff.satisfaction_score,
                    'overtime_hours': staff.overtime_hours,
                    'years_of_experience': staff.years_of_experience,
                    'previous_satisfaction_rating': staff.previous_satisfaction_rating,
                    'absenteeism_days': staff.absenteeism_days,
                    'role': staff.role
                })
                
        print(f"✓ Đã lưu {len(staff_list)} nhân viên vào {filepath}")
        
    except Exception as e:
        print(f"❌ Lỗi khi lưu file CSV: {e}")


# Test function
if __name__ == "__main__":
    print("="*60)
    print("TEST LOAD DATA")
    print("="*60)
    
    staff = load_staff_from_csv()
    print(f"\n✓ Đã load {len(staff)} nhân viên")
    
    if staff:
        print("\nMẪU 3 NHÂN VIÊN ĐẦU:")
        for i, s in enumerate(staff[:3], 1):
            print(f"\n{i}. {s.staff_id} - {s.role}")
            print(f"   Khoa: {s.department}")
            print(f"   Ca: {s.shift_duration_hours}h, Bệnh nhân: {s.patient_load}")
            print(f"   Ngày làm/tháng: {s.workdays_per_month}")
            print(f"   Kinh nghiệm: {s.years_of_experience} năm")
            print(f"   Hài lòng: {s.satisfaction_score:.2f}")
    
    departments = load_departments_from_csv()
    print(f"\n✓ Đã load {len(departments)} khoa/phòng ban")
    
    if departments:
        print("\nDANH SÁCH KHOA:")
        for d in departments:
            print(f"  - {d.name}: {d.required_staff_per_shift} nhân viên/ca, "
                  f"max {d.max_patient_load} bệnh nhân")