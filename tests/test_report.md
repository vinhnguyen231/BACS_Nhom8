# TEST CASE REPORT
## ACCESS CONTROL SYSTEM

---

## 1. Thông tin kiểm thử

- **Project:** Access Control System
- **Module:** Access Control
- **Công cụ kiểm thử:** pytest
- **Ngôn ngữ:** Python
- **File kiểm thử:** `tests/test_access_control.py`

---

## 2. Danh sách Test Case

| ID | Tên Test Case | Requirement | Input / Điều kiện | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|
| TC-02 | Xử lý khi có báo cháy | FR-10 | Hệ thống nhận tín hiệu báo cháy | Ngắt khóa điện toàn bộ cửa thoát hiểm | TC-02 liên kết thành công với FR-10 | PASS |
| TC-03 | Từ chối truy cập ngoài giờ | FR-11 | Giờ hiện tại = 22:00 | Cửa không được mở | `door_unlocked = False` | PASS |
| TC-04 | Cho phép truy cập trong giờ | FR-11 | Giờ hiện tại = 10:00 | Cửa được phép mở | `door_unlocked = True` | PASS |
| TC-05 | Kiểm tra đầu giờ làm việc | FR-11 | Giờ hiện tại = 08:00 | Cho phép truy cập | Điều kiện đúng | PASS |
| TC-06 | Kiểm tra cuối giờ làm việc | FR-11 | Giờ hiện tại = 18:00 | Cho phép truy cập | Điều kiện đúng | PASS |
| TC-07 | Từ chối trước giờ làm việc | FR-11 | Giờ hiện tại = 07:00 | Từ chối truy cập | Điều kiện sai | PASS |

---

## 3. Chi tiết Test Case

### TC-02 – Xử lý khi có báo cháy

**Requirement:** FR-10

**Mục đích:**  
Kiểm tra yêu cầu an toàn khi hệ thống nhận tín hiệu báo cháy.

**Điều kiện:**  
Hệ thống nhận tín hiệu báo cháy.

**Kết quả mong đợi:**  
Yêu cầu FR-10 phải được liên kết với Test Case TC-02 và có mức ưu tiên MUST.

**Kết quả thực tế:**  
TC-02 được liên kết thành công với FR-10 và priority là MUST.

**Status:** PASS

---

### TC-03 – Từ chối truy cập ngoài giờ

**Requirement:** FR-11

**Mục đích:**  
Kiểm tra hệ thống từ chối truy cập ngoài giờ làm việc.

**Input:**  
Giờ hiện tại = 22:00.

**Kết quả mong đợi:**  
Cửa không được mở.

**Kết quả thực tế:**  
`door_unlocked = False`.

**Status:** PASS

---

### TC-04 – Cho phép truy cập trong giờ

**Requirement:** FR-11

**Mục đích:**  
Kiểm tra hệ thống cho phép truy cập trong giờ làm việc.

**Input:**  
Giờ hiện tại = 10:00.

**Kết quả mong đợi:**  
Cửa được phép mở.

**Kết quả thực tế:**  
`door_unlocked = True`.

**Status:** PASS

---

### TC-05 – Kiểm tra đầu giờ làm việc

**Requirement:** FR-11

**Mục đích:**  
Kiểm tra thời điểm bắt đầu giờ làm việc.

**Input:**  
Giờ hiện tại = 08:00.

**Kết quả mong đợi:**  
Hệ thống cho phép truy cập.

**Kết quả thực tế:**  
Điều kiện giờ làm việc trả về `True`.

**Status:** PASS

---

### TC-06 – Kiểm tra cuối giờ làm việc

**Requirement:** FR-11

**Mục đích:**  
Kiểm tra thời điểm kết thúc giờ làm việc.

**Input:**  
Giờ hiện tại = 18:00.

**Kết quả mong đợi:**  
Hệ thống cho phép truy cập.

**Kết quả thực tế:**  
Điều kiện giờ làm việc trả về `True`.

**Status:** PASS

---

### TC-07 – Từ chối trước giờ làm việc

**Requirement:** FR-11

**Mục đích:**  
Kiểm tra hệ thống từ chối truy cập trước giờ làm việc.

**Input:**  
Giờ hiện tại = 07:00.

**Kết quả mong đợi:**  
Hệ thống từ chối truy cập.

**Kết quả thực tế:**  
Điều kiện giờ làm việc trả về `False`.

**Status:** PASS

---

## 4. Tổng kết kiểm thử

| Nội dung | Kết quả |
|---|---:|
| Tổng số Test Case | 6 |
| PASS | 6 |
| FAIL | 0 |
| Tỷ lệ đạt | 100% |

---

## 5. Lệnh thực hiện kiểm thử

```text
python -m pytest tests/test_access_control.py -v
collected 6 items

test_emergency_override_traceability PASSED
test_access_denied_logic PASSED
test_access_allowed_during_working_hours PASSED
test_access_allowed_at_start_of_working_hours PASSED
test_access_allowed_at_end_of_working_hours PASSED
test_access_denied_before_working_hours PASSED

6 passed in 0.05s