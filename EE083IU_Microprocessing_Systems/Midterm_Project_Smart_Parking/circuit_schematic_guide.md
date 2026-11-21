# SƠ ĐỒ ĐẤU DÂY & HƯỚNG DẪN MÔ PHỎNG HỆ THỐNG BÃI XE PIC16F877A

Tài liệu kỹ thuật hướng dẫn kết nối ngoại vi và vận hành mô phỏng 100% trên **SimulIDE** hoặc **Proteus 8 Professional** cho đồ án môn Hệ thống Vi xử lý (MPS).

---

## 1. Bảng Ánh Xạ Chân Ngoại Vi (Pinout Mapping)

| Chân MCU | Tên chân | Hướng I/O | Ngoại vi kết nối | Chức năng chi tiết |
|---|---|---|---|---|
| **Pin 1** | `MCLR/VPP` | Input | Điện trở kéo lên 10k lên VDD | Reset vi điều khiển khi khởi động |
| **Pin 13-14**| `OSC1 - OSC2` | I/O | Thạch anh 4.0 MHz + 2 tụ 22pF | Nguồn xung nhịp hệ thống (Tcy = 1.0 µs) |
| **Pin 33** | `RB0/INT` | Input | Cảm biến xe vào (Nút nhấn Entry) | Ngắt ngoài kích hoạt cạnh lên khi phát hiện xe vào cổng |
| **Pin 34** | `RB1` | Input | Cảm biến xe ra (Nút nhấn Exit) | Cảm biến nút nhấn Active-High đồng bộ tín hiệu 5V |
| **Pin 37** | `RB4` | Output | Đèn LED Xanh (Green LED) | Báo trạng thái bãi đỗ còn chỗ trống |
| **Pin 38** | `RB5` | Output | Đèn LED Đỏ (Red LED) | Báo trạng thái bãi đỗ đã đầy (FULL) |
| **Pin 39** | `RB6` | Output | Còi Buzzer cảnh báo | Phát âm thanh cảnh báo khi bãi đầy cố tình vượt rào |
| **Pin 17** | `RC2/CCP1`| Output | Động cơ Servo / PWM Motor | Xung PWM 50Hz/1kHz điều khiển mở (90°) và đóng (0°) barrier |
| **Pin 25** | `RC6/TX` | Output | Virtual Terminal / Serial Port | Truyền log dữ liệu nối tiếp 9600 baud (8N1) lên máy tính |
| **Pin 21** | `RD2` | Output | Màn hình LCD 16x2 chân `RS` | Điều khiển thanh ghi LCD (0=Lệnh, 1=Ký tự) |
| **Pin 22** | `RD3` | Output | Màn hình LCD 16x2 chân `EN` | Xung chốt dữ liệu màn hình LCD (Enable Strobe) |
| **Pin 27-30**| `RD4-RD7` | Output | Màn hình LCD 16x2 chân `D4-D7`| Bus dữ liệu 4-bit tiết kiệm chân I/O |

---

## 2. Các Bước Khởi Chạy Mô Phỏng Trên SimulIDE

1. Khởi động phần mềm **SimulIDE** (bản 0.4.x hoặc 1.x.x).
2. Chọn **File -> Open Circuit** và trỏ đến tệp:
   `C:\Users\LENOVO\OneDrive\Desktop\Javis test\code\parking_barrier_simulide.sim1`
3. Nhấp chuột phải vào linh kiện vi điều khiển **PIC16F877A** -> chọn **Load Firmware** (Nạp phần mềm).
4. Trỏ đến file:
   `C:\Users\LENOVO\OneDrive\Desktop\Javis test\code\parking_barrier_system.hex`
5. Bấm nút **Power Circuit (Biểu tượng nút nguồn màu đỏ ở thanh công cụ)** để bắt đầu chạy mô phỏng.

---

## 3. Các Bước Khởi Chạy Mô Phỏng Trên Proteus 8 Professional

1. Mở Proteus -> Tạo New Project -> Chọn linh kiện gồm:
   - `PIC16F877A`
   - `LM016L` (Màn hình LCD 16x2 ký tự)
   - `BUTTON` (Nút nhấn xe vào và ra)
   - `LED-GREEN`, `LED-RED` và điện trở `330R`
   - `MOTOR-SERVO` hoặc `DC MOTOR`
   - `VIRTUAL TERMINAL` (Lấy trong mục Virtual Instruments)
2. Đấu dây theo đúng **Bảng Ánh Xạ Chân Ngoại Vi** ở Mục 1.
3. Đấu chân `TXD` của MCU (`RC6`, chân 25) vào chân `RXD` của **Virtual Terminal**.
4. Nhấp đúp vào MCU `PIC16F877A`:
   - Mục **Program File**: Chọn file `parking_barrier_system.hex`.
   - Mục **Processor Clock Frequency**: Điền `4MHz`.
5. Bấm nút **Play (Run Simulation)** ở góc dưới bên trái Proteus.

---

## 4. Kịch Bản Kiểm Thử Thực Tế (6 Test Cases)

1. **Test Case 1 (Khởi động hệ thống):**
   - Màn hình LCD hiển thị dòng 1 `PARKING SYSTEM`, dòng 2 `SLOTS: 10/10`.
   - Đèn LED Xanh sáng, đèn LED Đỏ tắt, barrier ở vị trí 0° (đóng).
   - Serial Monitor nhận chuỗi: `[SYS] PARKING READY`.

2. **Test Case 2 (Xe vào cổng - Còn chỗ):**
   - Nhấn nút `CAR_ENTRY` (RB0).
   - Ngắt `RB0/INT` kích hoạt: biến đếm xe tăng lên 1, LCD cập nhật `SLOTS: 9/10`.
   - Barrier nâng lên góc 90°, giữ mở trong 2 giây rồi tự động hạ xuống 0°.
   - Serial Monitor in log: `[+] ENTRY CARS:1/10`.

3. **Test Case 3 (Xe ra khỏi bãi):**
   - Nhấn nút `CAR_EXIT` (RB1).
   - Hệ thống phát hiện nút nhấn: biến đếm xe giảm xuống 1, LCD cập nhật số chỗ trống.
   - Barrier mở 90°, giữ 2 giây rồi đóng 0°.
   - Serial Monitor in log: `[-] EXIT CARS:0/10`.

4. **Test Case 4 (Bãi xe đầy - Full Lockout):**
   - Kích hoạt xe vào liên tục đến khi đạt 10 xe (`CAR_COUNT = 10`).
   - Đèn LED Xanh tắt, đèn LED Đỏ sáng rực.
   - Màn hình LCD chuyển sang hiển thị cảnh báo `** LOT FULL! **`.

5. **Test Case 5 (Xe đến khi bãi đầy - Từ chối vào):**
   - Khi bãi đầy, tiếp tục nhấn `CAR_ENTRY` (RB0).
   - Ngắt kiểm tra `CAR_COUNT == MAX_SLOTS`: Không tăng biến đếm, barrier giữ đóng cố định.
   - Còi Buzzer (RB6) kêu cảnh báo trong 500ms.
   - Serial Monitor xuất cảnh báo: `[!] FULL! ENTRY DENIED`.

6. **Test Case 6 (Chống dội phím Debounce):**
   - Nhấn nhả nhanh nút bấm hoặc tạo xung nhiễu chập chờn.
   - Thuật toán `DELAY_DEBOUNCE` (20ms) triệt tiêu hoàn toàn xung rung cơ học, đảm bảo mỗi xe chỉ nhảy đúng 1 đơn vị đếm.
