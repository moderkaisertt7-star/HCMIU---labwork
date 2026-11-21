# BÁO CÁO GIẢI CHI TIẾT LAB 05: POINTERS (I) - SINGLE VARIABLE
**Môn học:** Programming for Engineers Laboratory (EE058IU / IT091IU - Group 02)  
**Trường:** Đại học Quốc Tế - ĐHQG TP.HCM (SEE - School of Electrical Engineering)  
**Sinh viên:** NGUYỄN LÊ MINH SANG | **MSSV:** `EEACIU24096`  
**Giảng viên hướng dẫn:** Dr. Hieu Nguyen (`nthieu@hcmiu.edu.vn`)  
**Ngày thực hiện & nộp bài:** 20/11/2026 | **Hạn chót:** 23:59 ngày 20/11/2026  

---

## MỤC TIÊU BÀI THÍ NGHIỆM
- Nắm vững bản chất con trỏ trong ngôn ngữ C: địa chỉ ô nhớ và toán tử lấy địa chỉ `&` (address-of), toán tử giải tham chiếu `*` (dereference).
- Khai báo con trỏ, trỏ tới biến nguyên thủy và đọc/ghi biến gián tiếp thông qua con trỏ.
- Phân biệt truyền tham trị (pass by value) và truyền tham chiếu (pass by reference) qua con trỏ.
- Trả về đồng thời nhiều kết quả từ hàm thông qua các tham số con trỏ.

---

## PROBLEM 1: FIRST POINTER
### Đề bài
Create an `int` variable `num = 10` and a pointer `ptr` to it. Print the address of `num`; print `num`'s value through the pointer; change `num` to `20` using only the pointer; print the new value to verify.

### Lời giải & Mã nguồn (ex1.c)
```c
#include <stdio.h>

int main(void) {
    int num = 10;
    int *ptr = &num;

    // 1. In dia chi o nho cua num
    printf("Address of num: %p\n", (void *)ptr);

    // 2. In gia tri cua num thong qua toan tu giai tham chieu *ptr
    printf("Value using pointer: %d\n", *ptr);

    // 3. Thay doi gia tri cua num thanh 20 chi dung con tro
    *ptr = 20;

    // 4. In gia tri moi cua bien num de kiem chung
    printf("New value of num: %d\n", num);

    return 0;
}
```

### Kết quả chạy thực nghiệm (Output)
```
Address of num: 00000092B1BFFABC
Value using pointer: 10
New value of num: 20
```

---

## PROBLEM 2: SWAP BY REFERENCE
### Đề bài
Read two numbers `n1` and `n2`. Write a function `swap(int *a, int *b)` that exchanges their values through pointers. Print the values after swapping.

### Lời giải & Mã nguồn (ex2.c)
```c
#include <stdio.h>

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main(void) {
    int n1, n2;

    printf("Enter n1: ");
    if (scanf("%d", &n1) != 1) return 1;

    printf("Enter n2: ");
    if (scanf("%d", &n2) != 1) return 1;

    // Truyen dia chi &n1 va &n2 vao ham swap (truyen tham chieu)
    swap(&n1, &n2);

    printf("After swap: n1 = %d, n2 = %d\n", n1, n2);

    return 0;
}
```

### Kết quả chạy thực nghiệm (Output)
```
Enter n1: 5
Enter n2: 9
After swap: n1 = 9, n2 = 5
```

---

## PROBLEM 3: SECONDS TO H:M:S
### Đề bài
Read a whole number of seconds. Write a function `convert(int total, int *h, int *m, int *s)` that returns hours, minutes and seconds through pointer parameters. Print the result in `main`.

### Lời giải & Mã nguồn (ex3.c)
```c
#include <stdio.h>

void convert(int total, int *h, int *m, int *s) {
    *h = total / 3600;
    *m = (total % 3600) / 60;
    *s = total % 60;
}

int main(void) {
    int total;
    int h, m, s;

    printf("Enter time in seconds: ");
    if (scanf("%d", &total) != 1) return 1;

    convert(total, &h, &m, &s);

    printf("%d hr %d min %d s\n", h, m, s);

    return 0;
}
```

### Kết quả chạy thực nghiệm (Output)
```
Enter time in seconds: 10000
2 hr 46 min 40 s
```

---

## PROBLEM 4: CIRCLE: TWO RESULTS AT ONCE
### Đề bài
Read a radius. Write `void calcCircle(double radius, double *circ, double *area)` that computes both the circumference and the area and returns them through pointers. Print everything from `main`, not from `calcCircle`.

### Lời giải & Mã nguồn (ex4.c)
```c
#include <stdio.h>

#define PI 3.14159265358979323846

void calcCircle(double radius, double *circ, double *area) {
    *circ = 2.0 * PI * radius;
    *area = PI * radius * radius;
}

int main(void) {
    double radius;
    double circ, area;

    printf("Enter radius: ");
    if (scanf("%lf", &radius) != 1) return 1;

    calcCircle(radius, &circ, &area);

    printf("Radius: %.2f\n", radius);
    printf("Circumference: %.2f\n", circ);
    printf("Area: %.2f\n", area);

    return 0;
}
```

### Kết quả chạy thực nghiệm (Output)
```
Enter radius: 5
Radius: 5.00
Circumference: 31.42
Area: 78.54
```

---

## PROBLEM 5: DECOMPOSE A REAL NUMBER
### Đề bài
Read one floating-point number (e.g. 3.14159). Write `void decompose(double x, int *intPart, double *fracPart)` that splits it into its integer and fractional parts and returns them through pointers (no return value). All printing is done in `main`.

### Lời giải & Mã nguồn (ex5.c)
```c
#include <stdio.h>

void decompose(double x, int *intPart, double *fracPart) {
    *intPart = (int)x;
    *fracPart = x - (double)(*intPart);
}

int main(void) {
    double x;
    int intPart;
    double fracPart;

    printf("Enter a number: ");
    if (scanf("%lf", &x) != 1) return 1;

    decompose(x, &intPart, &fracPart);

    printf("Original: %g\n", x);
    printf("Integer part: %d\n", intPart);
    printf("Fractional part: %.6f\n", fracPart);

    return 0;
}
```

### Kết quả chạy thực nghiệm (Output)
```
Enter a number: 3.14159
Original: 3.14159
Integer part: 3
Fractional part: 0.141590
```

---

## TỔNG HỢP DANH MỤC TỆP ĐÃ XUẤT BẢN
1. **File Word nộp bài:** `C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\EEACIU24096 - Nguyen Le Minh Sang - Lab 5.docx`
2. **File Markdown lưu trữ:** `C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\GIAI_CHI_TIET_LAB5_POINTERS_SINGLE_VARIABLE.md`
3. **Mã nguồn C:** `ex1.c`, `ex2.c`, `ex3.c`, `ex4.c`, `ex5.c` kèm các file thực thi `.exe` đã biên dịch qua GCC 16.1.0.
4. **Bản sao lưu trữ môn học:** `C:\Users\LENOVO\OneDrive\Desktop\UNIVERSITY\IU Junior\C lab\lab5\`
