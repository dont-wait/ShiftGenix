Hệ thống xếp lịch trực sử dụng Thuật toán Di truyền (Genetic Algorithm) dành cho Khoa Khám Ngoại Trú tại bệnh viện.

## 🚀 Tính năng

- ✅ Xếp lịch tự động sử dụng Genetic Algorithm
- ✅ Tuân thủ các ràng buộc cứng về pháp lý (40h/tuần, 12h nghỉ giữa ca, ...)
- ✅ Tối ưu hóa các ràng buộc mềm (công bằng, nguyện vọng, ...)
- ✅ Quản lý nhân viên và vị trí công việc
- ✅ Xuất lịch trực ra Excel
- ✅ Giao diện web thân thiện

## 📋 Yêu cầu hệ thống

- Python 3.11+
- pip hoặc poetry

## 🛠️ Cài đặt

### 1. Clone repository

```bash
git clone 
cd shiftgenix
```

### 2. Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

## 🏃 Chạy ứng dụng

### Development mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Mở trình duyệt và truy cập: `http://localhost:8000`

## 📁 Cấu trúc dự án

```
shiftgenix/
├── app/
│   ├── engine/           # Thuật toán GA
│   │   ├── ga_scheduler.py
│   │   └── fitness.py
│   ├── routers/          # API routes
│   │   ├── web.py        # Web UI routes
│   │   └── api.py        # REST API routes
│   ├── schemas/          # Pydantic models
│   │   └── schedule.py
│   ├── static/           # CSS, JS
│   │   └── style.css
│   ├── templates/        # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── staff.html
│   │   ├── positions.html
│   │   ├── schedule.html
│   │   ├── results.html
│   │   └── about.html
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🎯 Hướng dẫn sử dụng

### Bước 1: Quản lý Nhân viên

1. Truy cập `/staff`
2. Thêm thông tin nhân viên (bác sĩ, điều dưỡng)
3. Cấu hình:
   - Chuyên khoa
   - Kinh nghiệm
   - Giới hạn giờ làm
   - Ngày nghỉ phép
   - Nguyện vọng cá nhân

### Bước 2: Quản lý Vị trí

1. Truy cập `/positions`
2. Thêm các phòng khám/vị trí công việc
3. Cấu hình:
   - Chuyên khoa yêu cầu
   - Số lượng bác sĩ/điều dưỡng tối thiểu
   - Nhu cầu bệnh nhân theo khung giờ

### Bước 3: Tạo lịch trực

1. Truy cập `/schedule`
2. Cấu hình tham số Genetic Algorithm:
   - Kích thước quần thể: 100
   - Số thế hệ: 500
   - Tỷ lệ đột biến: 0.1
   - Tỷ lệ lai ghép: 0.8
3. Điều chỉnh trọng số ràng buộc mềm
4. Nhấn "Tạo lịch trực"

### Bước 4: Xem kết quả

1. Truy cập `/results`
2. Xem lịch trực theo:
   - Lịch (calendar view)
   - Bảng (table view)
   - Theo nhân viên (employee view)
3. Xuất Excel hoặc In

## 📊 API Endpoints

### REST API

- `POST /api/v1/schedule/generate` - Tạo lịch trực
- `GET /health` - Health check

### Request Example

```json
{
  "staff": [
    {
      "id": 1,
      "name": "Nguyễn Văn A",
      "role": "BacSi",
      "specialty": "Nội khoa",
      "max_hours_per_week": 40,
      "preferred_shifts": ["morning"],
      "leave_dates": []
    }
  ],
  "positions": [
    {
      "id": 1,
      "name": "Phòng khám Nội",
      "required_doctors": 1,
      "required_nurses": 1
    }
  ],
  "shifts": [
    {
      "id": 1,
      "name": "morning",
      "start_time": "07:00",
      "end_time": "15:00",
      "duration_hours": 8
    }
  ],
  "days": 30,
  "population_size": 100,
  "max_generations": 500,
  "mutation_rate": 0.1,
  "crossover_rate": 0.8
}
```

## 🧪 Testing

```bash
# Chạy tests (sẽ được implement sau)
pytest

# Coverage
pytest --cov=app
```

## 🐳 Docker

### Build image

```bash
docker build -t shiftgenix .
```

### Run container

```bash
docker run -d -p 8000:8000 shiftgenix
```

## 📚 Cơ sở khoa học

Hệ thống tuân thủ:

- **Bộ luật Lao động 2019** (Việt Nam)
- **Thông tư 03/2023/TT-BYT** - Định mức nhân lực y tế
- **Quyết định 73/2011/QĐ-TTg** - Chế độ phụ cấp trực
- Nghiên cứu quốc tế về Nurse Scheduling Problem

## 📖 Ràng buộc

### Ràng buộc Cứng (Hard Constraints)

1. Tối đa 40 giờ/tuần
2. Nghỉ ít nhất 12 giờ giữa các ca
3. Tối đa 3 ca đêm liên tiếp
4. Đúng chuyên môn và có chứng chỉ hành nghề
5. Tối thiểu 1 bác sĩ + 1 điều dưỡng/ca
6. Không xếp trực khi nghỉ phép
7. ≤65 bệnh nhân/bác sĩ/ngày (khuyến nghị)

### Ràng buộc Mềm (Soft Constraints)

1. Phân bổ đều ca khó (đêm, cuối tuần, lễ) - 30%
2. Cân bằng khối lượng công việc - 25%
3. Ưu tiên nguyện vọng cá nhân - 20%
4. Kết hợp nhân viên có kinh nghiệm và mới - 15%
5. Giảm thiểu làm thêm giờ - 10%

## 🔧 Tùy chỉnh

### Thay đổi trọng số ràng buộc

Sửa file `app/schemas/schedule.py`:

```python
weights: Dict[str, float] = {
    "fair_distribution": 0.30,      # Công bằng
    "workload_balance": 0.25,        # Khối lượng
    "respect_preferences": 0.20,     # Nguyện vọng
    "experience_mix": 0.15,          # Kinh nghiệm
    "minimize_overtime": 0.10        # Làm thêm
}
```

### Thay đổi tham số GA

Trong trang `/schedule`:
- Population size: 50-500
- Max generations: 100-2000
- Mutation rate: 0.01-0.3
- Crossover rate: 0.6-0.9

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết

## 👥 Tác giả

- **dont-wait** - Initial work

## 🙏 Lời cảm ơn

- Bộ Y tế Việt Nam - Quy định và hướng dẫn
- Các nghiên cứu quốc tế về Nurse Scheduling Problem
- FastAPI framework
- Bootstrap team

---

**Lưu ý**: Đây là phiên bản MVP (Minimum Viable Product). Các tính năng nâng cao sẽ được bổ sung trong các phiên bản tiếp theo.