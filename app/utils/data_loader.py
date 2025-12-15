import csv
from pathlib import Path
from typing import List
from app.schemas.schedule import Staff, Position

def load_staff_from_csv(filepath: str = "app/data/staff.csv") -> List[Staff]:
    """Đọc danh sách nhân viên từ file CSV"""
    staff_list = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse preferred_shifts
                preferred_shifts = []
                if row['preferred_shifts']:
                    preferred_shifts = row['preferred_shifts'].split('|')
                
                # Parse leave_dates
                leave_dates = []
                if row['leave_dates']:
                    leave_dates = row['leave_dates'].split('|')
                
                # Parse eligible_positions based on specialty
                specialty = row['specialty']
                eligible_positions = []
                if specialty == "Nội khoa":
                    eligible_positions = ["PK_NOI_001"]
                elif specialty == "Ngoại khoa":
                    eligible_positions = ["PK_NGOAI_001"]
                elif specialty == "Sản khoa":
                    eligible_positions = ["PK_SAN_001"]
                elif specialty == "Nhi khoa":
                    eligible_positions = ["PK_NHI_001"]
                
                staff = Staff(
                    id=int(row['id'].replace('BS', '').replace('DD', '')),
                    name=row['name'],
                    role=row['role'],
                    specialty=specialty,
                    experience_level=row['experience_level'],
                    max_hours_per_week=int(row['max_hours_per_week']),
                    min_rest_hours=int(row['min_rest_hours']),
                    max_consecutive_night_shifts=int(row['max_consecutive_night_shifts']),
                    is_pregnant=row['is_pregnant'] == 'True',
                    has_young_children=row['has_young_children'] == 'True',
                    preferred_shifts=preferred_shifts,
                    leave_dates=leave_dates,
                    eligible_positions=eligible_positions
                )
                staff_list.append(staff)
                
    except FileNotFoundError:
        print(f"File {filepath} không tồn tại")
        return []
    except Exception as e:
        print(f"Lỗi khi đọc file CSV: {e}")
        return []
    
    return staff_list


def load_positions_from_csv(filepath: str = "app/data/positions.csv") -> List[Position]:
    """Đọc danh sách vị trí từ file CSV"""
    positions_list = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                position = Position(
                    id=int(row['id'].split('_')[-1]),
                    name=row['name'],
                    specialty_required=row['specialty_required'],
                    required_doctors=int(row['required_doctors']),
                    required_nurses=int(row['required_nurses'])
                )
                positions_list.append(position)
                
    except FileNotFoundError:
        print(f"File {filepath} không tồn tại")
        return []
    except Exception as e:
        print(f"Lỗi khi đọc file CSV: {e}")
        return []
    
    return positions_list


def save_staff_to_csv(staff_list: List[Staff], filepath: str = "data/staff.csv"):
    """Lưu danh sách nhân viên vào file CSV"""
    try:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'id', 'name', 'role', 'specialty', 'experience_level',
                'max_hours_per_week', 'min_rest_hours', 'max_consecutive_night_shifts',
                'is_pregnant', 'has_young_children', 'preferred_shifts', 'leave_dates'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for staff in staff_list:
                writer.writerow({
                    'id': f"{staff.role[:2].upper()}{staff.id:03d}",
                    'name': staff.name,
                    'role': staff.role,
                    'specialty': staff.specialty,
                    'experience_level': staff.experience_level,
                    'max_hours_per_week': staff.max_hours_per_week,
                    'min_rest_hours': staff.min_rest_hours,
                    'max_consecutive_night_shifts': staff.max_consecutive_night_shifts,
                    'is_pregnant': staff.is_pregnant,
                    'has_young_children': staff.has_young_children,
                    'preferred_shifts': '|'.join(staff.preferred_shifts),
                    'leave_dates': '|'.join(staff.leave_dates)
                })
                
        print(f"Đã lưu {len(staff_list)} nhân viên vào {filepath}")
        
    except Exception as e:
        print(f"Lỗi khi lưu file CSV: {e}")


# Test function
if __name__ == "__main__":
    staff = load_staff_from_csv()
    print(f"Đã load {len(staff)} nhân viên")
    for s in staff[:3]:
        print(f"- {s.name} ({s.role}, {s.specialty})")
    
    positions = load_positions_from_csv()
    print(f"\nĐã load {len(positions)} vị trí")
    for p in positions:
        print(f"- {p.name} ({p.specialty_required})")