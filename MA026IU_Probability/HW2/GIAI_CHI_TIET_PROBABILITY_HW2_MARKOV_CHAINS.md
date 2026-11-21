# PROBABILITY (MA026IU)
## HOMEWORK 2: DISCRETE-TIME MARKOV CHAINS (CHAPTER 12)

**Sinh viên:** NGUYỄN LÊ MINH SANG | **MSSV:** EEACIU24096 | **Lớp:** Probability

---


Đề bài: Xác định các phần tử còn thiếu ký hiệu là x trong ma trận xác suất chuyển trạng thái P:
P = [
  [x,   1/3, 1/3, 1/3],
  [1/10,  x, 1/5, 2/5],
  [x,     x,   x,   1],
  [3/5, 2/5,   x,   x]
]

Lời giải chi tiết:
Theo định nghĩa của ma trận xác suất chuyển trạng thái trong chuỗi Markov (Stochastic Matrix):
1. Mọi phần tử đều là xác suất nên p_ij >= 0 với mọi i, j.
2. Tổng xác suất của mỗi hàng (tổng xác suất rời khỏi trạng thái i) luôn bằng đúng 1:
   sum_{j=1}^M p_ij = 1 với mọi hàng i.

Xét từng hàng của ma trận:
- Hàng 1:
  x + 1/3 + 1/3 + 1/3 = 1  <=>  x + 1 = 1  <=>  x = 0.
  (Do đó p_11 = 0).

- Hàng 2:
  1/10 + x + 1/5 + 2/5 = 1  <=>  1/10 + x + 2/10 + 4/10 = 1  <=>  x + 7/10 = 1  <=>  x = 3/10 (0.3).
  (Do đó p_22 = 3/10).

- Hàng 3:
  x + x + x + 1 = 1  <=>  3x + 1 = 1  <=>  3x = 0  <=>  x = 0.
  (Vì p_ij >= 0 nên cả ba phần tử p_31 = p_32 = p_33 = 0).

- Hàng 4:
  3/5 + 2/5 + x + x = 1  <=>  1 + 2x = 1  <=>  2x = 0  <=>  x = 0.
  (Vì p_43 >= 0 và p_44 >= 0 nên p_43 = p_44 = 0).

Kết luận: Ma trận xác suất chuyển trạng thái hoàn chỉnh là:
P = [
  [  0,  1/3, 1/3, 1/3],
  [1/10, 3/10, 1/5, 2/5],
  [  0,    0,   0,   1],
  [3/5,  2/5,   0,   0]
]


---


Đề bài: Xét chuỗi Markov với sơ đồ chuyển trạng thái cho trong Hình 12.22 (gồm 9 trạng thái: 1, 2, 3, 4, 5, 6, 7, 8, 9).
a. Liệt kê các trạng thái tạm thời (transient), hồi quy (recurrent) và tuần hoàn (periodic).
b. Xác định các thành viên của từng chuỗi trạng thái hồi quy.
c. Lập ma trận xác suất chuyển trạng thái của quá trình.
d. Cho biết quá trình bắt đầu ở trạng thái 1, xác định xác suất quá trình ở trạng thái 8 sau vô hạn bước chuyển (n -> oo) hoặc giải thích vì sao giá trị này không tồn tại.

Lời giải chi tiết:

a. Phân loại các trạng thái:
- Trạng thái tạm thời (Transient states): {1, 2, 3, 4}.
  Giải thích: Từ nhóm {1, 2, 3, 4}, trạng thái 3 có chuyển tiếp sang trạng thái 5 (xác suất 1/6) và sang trạng thái 8 (xác suất 1/3). Khi quá trình đã nhảy vào nhóm {5, 6, 7} hoặc {8, 9}, xác suất quay trở lại {1, 2, 3, 4} bằng 0. Do đó, các trạng thái 1, 2, 3, 4 đều là transient.
- Trạng thái hồi quy (Recurrent states): {5, 6, 7, 8, 9}.
  Giải thích: Nhóm {5, 6, 7} và nhóm {8, 9} là các tập đóng (closed communicating classes), một khi đã vào thì quá trình chỉ chuyển tiếp bên trong tập đó mãi mãi với xác suất quay về bằng 1.
- Trạng thái tuần hoàn (Periodic states): Không có trạng thái nào (Tất cả đều là phi tuần hoàn / aperiodic).
  Giải thích:
  + Nhóm {8, 9} có các vòng tự lặp p_88 = 1/3 > 0 và p_99 = 3/4 > 0 nên chu kỳ d = gcd(1, ...) = 1 (aperiodic).
  + Nhóm {5, 6, 7}: từ 5 -> 6 -> 5 (độ dài chu trình 2) và 5 -> 7 -> 6 -> 5 (độ dài chu trình 3). Do gcd(2, 3) = 1 nên nhóm này cũng phi tuần hoàn (aperiodic).

b. Các chuỗi trạng thái hồi quy (Recurrent classes):
- Chuỗi 1 (Class 1): {5, 6, 7}
- Chuỗi 2 (Class 2): {8, 9}

c. Ma trận xác suất chuyển trạng thái P (cỡ 9x9):
Hàng 1: [1/3, 1/6, 1/6, 1/3,   0,   0,   0,   0,   0]
Hàng 2: [1/4, 1/4, 1/2,   0,   0,   0,   0,   0,   0]
Hàng 3: [  0, 1/4,   0, 1/4, 1/6,   0,   0, 1/3,   0]
Hàng 4: [  0,   0, 1/2, 1/2,   0,   0,   0,   0,   0]
Hàng 5: [  0,   0,   0,   0,   0, 1/2, 1/2,   0,   0]
Hàng 6: [  0,   0,   0,   0, 1/3,   0, 2/3,   0,   0]
Hàng 7: [  0,   0,   0,   0, 1/4, 3/4,   0,   0,   0]
Hàng 8: [  0,   0,   0,   0,   0,   0,   0, 1/3, 2/3]
Hàng 9: [  0,   0,   0,   0,   0,   0,   0, 1/4, 3/4]

d. Xác suất quá trình ở trạng thái 8 khi n -> oo biết X_0 = 1:
Theo định lý giới hạn chuỗi Markov với nhiều lớp hấp thu hồi quy:
lim_{n->oo} P(X_n = 8 | X_0 = 1) = P(hấp thu vào Chuỗi 2 {8,9} | X_0 = 1) * pi_8^(Chuỗi 2)

Bước 1: Tính phân phối dừng của Chuỗi 2 {8, 9}:
  pi_8 = (1/3)*pi_8 + (1/4)*pi_9
  (2/3)*pi_8 = (1/4)*pi_9  <=>  pi_9 = (8/3)*pi_8
  Mặt khác: pi_8 + pi_9 = 1  <=>  pi_8 + (8/3)*pi_8 = 1  <=>  (11/3)*pi_8 = 1  <=>  pi_8 = 3/11.

Bước 2: Tính xác suất hấp thu vào Chuỗi 2 {8, 9} từ trạng thái 1 (ký hiệu a_i là xác suất hấp thu vào Chuỗi 2 từ trạng thái i trong {1,2,3,4}):
  - a_4 = (1/2)*a_3 + (1/2)*a_4  <=>  a_4 = a_3
  - a_3 = (1/4)*a_2 + (1/4)*a_4 + (1/6)*0 + (1/3)*1
        = (1/4)*a_2 + (1/4)*a_3 + 1/3  <=>  (3/4)*a_3 - (1/4)*a_2 = 1/3  <=>  3*a_3 - a_2 = 4/3  (1)
  - a_2 = (1/4)*a_1 + (1/4)*a_2 + (1/2)*a_3  <=>  (3/4)*a_2 - (1/4)*a_1 = (1/2)*a_3  <=>  3*a_2 - a_1 = 2*a_3  (2)
  - a_1 = (1/3)*a_1 + (1/6)*a_2 + (1/6)*a_3 + (1/3)*a_4
        = (1/3)*a_1 + (1/6)*a_2 + (1/6 + 1/3)*a_3 = (1/3)*a_1 + (1/6)*a_2 + (1/2)*a_3
        <=> (2/3)*a_1 = (1/6)*a_2 + (1/2)*a_3  <=>  4*a_1 = a_2 + 3*a_3  <=>  a_1 = (a_2 + 3*a_3)/4  (3)

Thay (3) vào (2):
  3*a_2 - (a_2 + 3*a_3)/4 = 2*a_3  <=>  12*a_2 - a_2 - 3*a_3 = 8*a_3  <=>  11*a_2 = 11*a_3  <=>  a_2 = a_3.
Từ đó: a_1 = a_2 = a_3 = a_4.
Thay a_2 = a_3 vào (1):
  3*a_3 - a_3 = 4/3  <=>  2*a_3 = 4/3  <=>  a_3 = 2/3.
Suy ra xác suất hấp thu từ trạng thái 1 vào Chuỗi 2 là:
  a_1 = 2/3.

Bước 3: Xác suất cần tìm:
  lim_{n->oo} P(X_n = 8 | X_0 = 1) = a_1 * pi_8 = (2/3) * (3/11) = 2/11 ≈ 0.1818.


---


Đề bài: Xét chuỗi Markov 3 trạng thái trong Hình 12.23:
- Ma trận P:
  P = [
    [  0, 1/3,  2/3],
    [  0, 1/10, 9/10],
    [1/4, 1/6,  7/12]
  ]
a. Xác định trạng thái tạm thời, hồi quy, tuần hoàn và thành viên từng chuỗi hồi quy.
b. Tính xác suất giới hạn (limiting-state probabilities) hoặc giải thích vì sao không tồn tại.
c. Cho biết quá trình đang ở trạng thái 1, tính P[A], xác suất quá trình sẽ ở trạng thái 3 ít nhất 1 lần trong 2 bước chuyển kế tiếp.

Lời giải chi tiết:

a. Phân loại trạng thái:
- Tất cả 3 trạng thái {1, 2, 3} liên thông với nhau (1 -> 2 -> 3 -> 1). Chuỗi là tối giản (irreducible).
- Do đó:
  + Không có trạng thái tạm thời (Transient states: rỗng).
  + Tất cả các trạng thái đều là hồi quy (Recurrent states: {1, 2, 3}).
  + Chuỗi hồi quy duy nhất: {1, 2, 3}.
  + Vì trạng thái 2 có self-loop (1/10) và trạng thái 3 có self-loop (7/12) nên chu kỳ d = 1. Tất cả đều là phi tuần hoàn (aperiodic).

b. Xác định xác suất giới hạn pi = [pi_1, pi_2, pi_3]:
Hệ phương trình cân bằng pi * P = pi và sum pi_i = 1:
(1) pi_1 = (1/4)*pi_3
(2) pi_2 = (1/3)*pi_1 + (1/10)*pi_2 + (1/6)*pi_3
(3) pi_1 + pi_2 + pi_3 = 1

Giải hệ:
Thay (1) vào (2):
  pi_2 = (1/3)*(1/4)*pi_3 + (1/10)*pi_2 + (1/6)*pi_3
  pi_2 = (1/12 + 2/12)*pi_3 + (1/10)*pi_2 = (1/4)*pi_3 + (1/10)*pi_2
  (9/10)*pi_2 = (1/4)*pi_3  <=>  pi_2 = (10/36)*pi_3 = (5/18)*pi_3.

Thay pi_1 và pi_2 theo pi_3 vào (3):
  (1/4)*pi_3 + (5/18)*pi_3 + pi_3 = 1
  (9/36 + 10/36 + 36/36)*pi_3 = 1  <=>  (55/36)*pi_3 = 1  <=>  pi_3 = 36/55.

Từ đó:
  pi_1 = (1/4) * (36/55) = 9/55 ≈ 0.1636.
  pi_2 = (5/18) * (36/55) = 10/55 = 2/11 ≈ 0.1818.
  pi_3 = 36/55 ≈ 0.6545.

Kiểm tra: 9/55 + 10/55 + 36/55 = 55/55 = 1 (Chính xác tuyệt đối).

c. Tính P[A] (ở trạng thái 3 ít nhất 1 lần trong 2 bước tới khi X_0 = 1):
Xét biến cố đối A_bar: "Quá trình KHÔNG lần nào ghé vào trạng thái 3 trong 2 bước chuyển kế tiếp".
Nghĩa là: X_1 != 3 và X_2 != 3.
- Bước 1 từ trạng thái 1:
  X_1 chỉ có thể là trạng thái 2 (vì nếu là 3 thì vi phạm).
  P(X_1 = 2 | X_0 = 1) = p_12 = 1/3.
- Bước 2 từ trạng thái 2:
  X_2 chỉ có thể là trạng thái 2 (vì p_21 = 0, nếu là 3 thì vi phạm).
  P(X_2 = 2 | X_1 = 2) = p_22 = 1/10.

Do đó:
  P(A_bar) = P(X_1 = 2, X_2 = 2 | X_0 = 1) = p_12 * p_22 = (1/3) * (1/10) = 1/30.
Suy ra xác suất cần tìm là:
  P[A] = 1 - P(A_bar) = 1 - 1/30 = 29/30 ≈ 0.9667 (96.67%).


---


Đề bài: Cho ma trận xác suất chuyển trạng thái:
P = [
  [0.6, 0.2, 0.2],
  [0.3, 0.4, 0.3],
  [0.0, 0.3, 0.7]
]
a. Vẽ / mô tả sơ đồ chuyển trạng thái.
b. Cho biết quá trình đang ở trạng thái 1, tính xác suất quá trình ở trạng thái 2 ở cuối bước chuyển thứ 3: P(X_3 = 2 | X_0 = 1).
c. Cho biết quá trình đang ở trạng thái 1, tính xác suất lần đầu tiên quá trình bước vào trạng thái 3 là ở bước chuyển thứ 4 (First passage time T_3 = 4).

Lời giải chi tiết:

a. Sơ đồ chuyển trạng thái (State-Transition Description):
- Trạng thái 1: vòng tự lặp 0.6; sang 2: 0.2; sang 3: 0.2.
- Trạng thái 2: sang 1: 0.3; vòng tự lặp 0.4; sang 3: 0.3.
- Trạng thái 3: sang 1: 0.0 (không có đường về 1 trực tiếp); sang 2: 0.3; vòng tự lặp 0.7.

b. Tính P(X_3 = 2 | X_0 = 1):
Xác suất này chính là phần tử ở hàng 1, cột 2 của ma trận luỹ thừa bậc 3: P^(3)_(1,2).
- Tính P^2:
  P^2 = P * P = [
    [0.42, 0.26, 0.32],
    [0.30, 0.31, 0.39],
    [0.09, 0.33, 0.58]
  ]
- Tính P^3:
  Hàng 1 của P^3:
  (P^3)_11 = 0.42*0.6 + 0.26*0.3 + 0.32*0.0 = 0.252 + 0.078 + 0.000 = 0.330
  (P^3)_12 = 0.42*0.2 + 0.26*0.4 + 0.32*0.3 = 0.084 + 0.104 + 0.096 = 0.2840
  (P^3)_13 = 0.42*0.2 + 0.26*0.3 + 0.32*0.7 = 0.084 + 0.078 + 0.224 = 0.386

Kết quả:
  P(X_3 = 2 | X_0 = 1) = 0.2840 (28.40%).

c. Tính xác suất lần đầu tiên vào trạng thái 3 ở bước thứ 4 (T_3 = 4):
Biến cố "lần đầu tiên vào 3 ở bước 4" đồng nghĩa với:
- X_0 = 1
- X_1 in {1, 2}
- X_2 in {1, 2}
- X_3 in {1, 2}
- X_4 = 3

Rút gọn ma trận chuyển trạng thái trên tập con {1, 2}:
Q = [
  [0.6, 0.2],
  [0.3, 0.4]
]
Vectơ xác suất chuyển vào trạng thái 3 từ {1, 2}:
R = [0.2, 0.3]^T

Vectơ phân phối tại bước 0 trên {1, 2}: pi_0 = [1, 0].
- Tại bước 1 trên {1, 2}: pi_1 = pi_0 * Q = [0.6, 0.2]
- Tại bước 2 trên {1, 2}: pi_2 = pi_1 * Q = [0.6*0.6 + 0.2*0.3, 0.6*0.2 + 0.2*0.4] = [0.42, 0.20]
- Tại bước 3 trên {1, 2}: pi_3 = pi_2 * Q = [0.42*0.6 + 0.20*0.3, 0.42*0.2 + 0.20*0.4] = [0.312, 0.164]
- Tại bước 4 nhảy vào trạng thái 3:
  P(T_3 = 4 | X_0 = 1) = pi_3 * R = 0.312 * 0.2 + 0.164 * 0.3 = 0.0624 + 0.0492 = 0.1116.

Kết quả:
  P(T_3 = 4 | X_0 = 1) = 0.1116 (11.16%).


---


Đề bài: Một tài xế taxi đón khách qua lại giữa 3 thị trấn 1, 2, 3:
- Khi ở thị trấn 1: xác suất khách kế tiếp đi thị trấn 1 là 0.3, thị trấn 2 là 0.2, thị trấn 3 là 0.5.
- Khi ở thị trấn 2: xác suất khách kế tiếp đi thị trấn 1 là 0.1, thị trấn 2 là 0.8, thị trấn 3 là 0.1.
- Khi ở thị trấn 3: xác suất khách kế tiếp đi thị trấn 1 là 0.4, thị trấn 2 là 0.4, thị trấn 3 là 0.2.

a. Xác định sơ đồ chuyển trạng thái.
b. Lập ma trận xác suất chuyển trạng thái P.
c. Tính các xác suất giới hạn (limiting-state probabilities).
d. Cho biết tài xế hiện đang ở thị trấn 2 (X_0 = 2), tính xác suất lần đầu tiên ông đón khách đi thị trấn 2 là vị khách thứ 3 trong ngày.
e. Cho biết tài xế đang ở thị trấn 2, tính xác suất vị khách thứ 3 từ bây giờ sẽ đi thị trấn 1.

Lời giải chi tiết:

a. Sơ đồ chuyển trạng thái:
- Trạng thái 1: tự lặp 0.3, sang 2: 0.2, sang 3: 0.5.
- Trạng thái 2: sang 1: 0.1, tự lặp 0.8, sang 3: 0.1.
- Trạng thái 3: sang 1: 0.4, sang 2: 0.4, tự lặp 0.2.

b. Ma trận xác suất chuyển trạng thái P:
P = [
  [0.3, 0.2, 0.5],
  [0.1, 0.8, 0.1],
  [0.4, 0.4, 0.2]
]

c. Tính các xác suất giới hạn pi = [pi_1, pi_2, pi_3]:
Hệ phương trình cân bằng pi * P = pi và sum pi_i = 1:
(1) pi_1 = 0.3*pi_1 + 0.1*pi_2 + 0.4*pi_3  <=>  0.7*pi_1 - 0.1*pi_2 - 0.4*pi_3 = 0
(2) pi_2 = 0.2*pi_1 + 0.8*pi_2 + 0.4*pi_3  <=>  -0.2*pi_1 + 0.2*pi_2 - 0.4*pi_3 = 0
(3) pi_1 + pi_2 + pi_3 = 1

Lấy (1) trừ (2):
  (0.7 - (-0.2))*pi_1 + (-0.1 - 0.2)*pi_2 = 0  <=>  0.9*pi_1 - 0.3*pi_2 = 0  <=>  pi_2 = 3*pi_1.

Thay pi_2 = 3*pi_1 vào (1):
  0.7*pi_1 - 0.1*(3*pi_1) - 0.4*pi_3 = 0  <=>  0.4*pi_1 = 0.4*pi_3  <=>  pi_3 = pi_1.

Thay vào (3):
  pi_1 + 3*pi_1 + pi_1 = 1  <=>  5*pi_1 = 1  <=>  pi_1 = 1/5 = 0.2.
Do đó:
  pi_1 = 0.2 (20%)
  pi_2 = 0.6 (60%)
  pi_3 = 0.2 (20%)

Ý nghĩa thực tế: Về lâu dài, tài xế taxi sẽ dành 60% thời gian phục vụ tại thị trấn 2, 20% tại thị trấn 1 và 20% tại thị trấn 3.

d. Xác suất lần đầu tiên đón khách đi thị trấn 2 là ở vị khách thứ 3 (X_0 = 2):
Biến cố này yêu cầu:
- Khách 1 (X_1) KHÔNG đi thị trấn 2 (tức là đi 1 hoặc 3).
- Khách 2 (X_2) KHÔNG đi thị trấn 2 (tức là đi 1 hoặc 3).
- Khách 3 (X_3) đi thị trấn 2.

Các lộ trình hợp lệ:
1. Lộ trình 2 -> 1 -> 1 -> 2:
   P_1 = p_21 * p_11 * p_12 = 0.1 * 0.3 * 0.2 = 0.006.
2. Lộ trình 2 -> 1 -> 3 -> 2:
   P_2 = p_21 * p_13 * p_32 = 0.1 * 0.5 * 0.4 = 0.020.
3. Lộ trình 2 -> 3 -> 1 -> 2:
   P_3 = p_23 * p_31 * p_12 = 0.1 * 0.4 * 0.2 = 0.008.
4. Lộ trình 2 -> 3 -> 3 -> 2:
   P_4 = p_23 * p_33 * p_32 = 0.1 * 0.2 * 0.4 = 0.008.

Tổng xác suất:
  P = P_1 + P_2 + P_3 + P_4 = 0.006 + 0.020 + 0.008 + 0.008 = 0.0420 (4.20%).

e. Xác suất vị khách thứ 3 đi thị trấn 1 biết X_0 = 2:
Xác suất này chính là phần tử (row 2, col 1) của ma trận P^3, tức là P^(3)_(2,1):
- Tính P^2:
  P^2 = [
    [0.31, 0.42, 0.27],
    [0.15, 0.70, 0.15],
    [0.24, 0.48, 0.28]
  ]
- Phần tử hàng 2, cột 1 của P^3:
  (P^3)_21 = 0.15*0.3 + 0.70*0.1 + 0.15*0.4 = 0.045 + 0.070 + 0.060 = 0.1750.

Kết quả:
  P(X_3 = 1 | X_0 = 2) = 0.1750 (17.50%).


