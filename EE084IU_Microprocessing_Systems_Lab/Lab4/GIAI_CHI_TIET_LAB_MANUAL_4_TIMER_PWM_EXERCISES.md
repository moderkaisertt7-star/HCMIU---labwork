# MICRO-PROCESSING SYSTEMS LABORATORY (EE084IU)
## LAB MANUAL 4: TIMER/COUNTER PROGRAMMING & PWM CONTROL
### BẢN LỜI GIẢI CHI TIẾT & MÃ NGUỒN HOÀN CHỈNH (EXERCISE 13, 14, 15)

**Sinh viên:** NGUYỄN LÊ MINH SANG | **MSSV:** EEACIU24096 | **Lớp:** EE084IU / Group 05

---

## EXERCISE 13: Timer0 CTC 4-Bit Binary Counter


1. Tính toán lý thuyết:
- Tần số vi điều khiển: F_CPU = 16 MHz.
- Chế độ Timer0 CTC: WGM01 = 1, WGM00 = 0.
- Chọn Prescaler N = 64 (CS02 = 0, CS01 = 1, CS00 = 1).
- Tần số định thời ngắt so sánh 1 ms (1000 Hz):
  T_compare = (OCR0 + 1) * N / F_CPU = 1 ms = 0.001 s
  => OCR0 + 1 = (F_CPU * 0.001) / N = (16,000,000 * 0.001) / 64 = 250
  => OCR0 = 249.
- Để đếm tăng 1 giá trị nhị phân sau mỗi 250 ms:
  Số lần ngắt CTC cần tích lũy: count_max = 250 lần (250 * 1 ms = 250 ms).
- Hiển thị: 4 LED nối tại PA0..PA3. Chu kỳ đếm 0 -> 15 lặp lại sau: 16 * 250 ms = 4.000 s.


```assembly
; ==============================================================================
; EXERCISE 13: Timer0 CTC 4-Bit Binary Counter (PA0..PA3)
; F_CPU = 16 MHz, Prescaler = 64, OCR0 = 249 => 1 ms Compare Match Interrupt
; Every 250 compare matches (250 ms), advance 4-bit counter on PA0..PA3
; ==============================================================================
.include "m32def.inc"

.def TEMP        = R16
.def MS_COUNT    = R17       ; Đếm từ 0 đến 250
.def BIN_VAL     = R18       ; Giá trị 4-bit hiển thị (0..15)

.org 0x0000
    rjmp RESET
.org OC0addr                 ; Timer0 Compare Match Interrupt Vector (0x0014)
    rjmp TIMER0_COMP_ISR

RESET:
    ; 1. Khởi tạo con trỏ Stack
    ldi TEMP, HIGH(RAMEND)
    out SPH, TEMP
    ldi TEMP, LOW(RAMEND)
    out SPL, TEMP

    ; 2. Cấu hình cổng PA0..PA3 là Output cho 4 LED
    ldi TEMP, 0x0F
    out DDRA, TEMP
    clr BIN_VAL
    out PORTA, BIN_VAL

    ; 3. Khởi tạo biến đếm
    clr MS_COUNT

    ; 4. Cấu hình Timer0 chế độ CTC: WGM01=1, WGM00=0
    ;    Prescaler N = 64: CS01=1, CS00=1 -> TCCR0 = (1<<WGM01) | (1<<CS01) | (1<<CS00) = 0x0B
    ldi TEMP, 249
    out OCR0, TEMP
    clr TEMP
    out TCNT0, TEMP

    ; Cho phép ngắt Compare Match Timer0 (OCIE0)
    ldi TEMP, (1<<OCIE0)
    out TIMSK, TEMP

    ; Kích hoạt Timer0 chạy với Prescaler 64
    ldi TEMP, (1<<WGM01) | (1<<CS01) | (1<<CS00)
    out TCCR0, TEMP

    ; Cho phép ngắt toàn cục
    sei

MAIN_LOOP:
    rjmp MAIN_LOOP

; --- Trình phục vụ ngắt Timer0 Compare Match (mỗi 1 ms) ---
TIMER0_COMP_ISR:
    push TEMP
    in TEMP, SREG
    push TEMP

    inc MS_COUNT
    cpi MS_COUNT, 250        ; Đã đủ 250 ms chưa?
    brne ISR_EXIT

    ; Đủ 250 ms -> Tăng bộ đếm 4-bit
    clr MS_COUNT
    inc BIN_VAL
    andi BIN_VAL, 0x0F       ; Giới hạn 4-bit (0..15)
    out PORTA, BIN_VAL       ; Xuất ra 4 LED PA0..PA3

ISR_EXIT:
    pop TEMP
    out SREG, TEMP
    pop TEMP
    reti

```

```c
/*
 * EXERCISE 13: Timer0 CTC 4-Bit Binary Counter (C Implementation)
 * ATmega32A @ 16 MHz, Prescaler = 64, OCR0 = 249 -> 1 ms ISR tick
 */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

volatile uint8_t ms_count = 0;
volatile uint8_t binary_counter = 0;

ISR(TIMER0_COMP_vect) {
    ms_count++;
    if (ms_count >= 250) {
        ms_count = 0;
        binary_counter = (binary_counter + 1) & 0x0F; // Tăng giá trị 4-bit (0..15)
        PORTA = (PORTA & 0xF0) | binary_counter;      // Cập nhật PA0..PA3 mà không ảnh hưởng bit khác
    }
}

int main(void) {
    // 1. Cấu hình PA0..PA3 là Output
    DDRA |= 0x0F;
    PORTA &= 0xF0;

    // 2. Cấu hình Timer0 chế độ CTC với OCR0 = 249
    OCR0 = 249;
    TCNT0 = 0;

    // 3. Cho phép ngắt Compare Match (OCIE0) trong TIMSK
    TIMSK |= (1 << OCIE0);

    // 4. Bật Timer0: CTC mode (WGM01) và Prescaler 64 (CS01 | CS00)
    TCCR0 = (1 << WGM01) | (1 << CS01) | (1 << CS00);

    // 5. Bật ngắt toàn cục
    sei();

    while (1) {
        // CPU nhàn rỗi trong vòng lặp chính, việc tăng LED do ISR tự động xử lý
    }
    return 0;
}

```

---

## EXERCISE 14: Timer1 External Event Counter with 4 Nibbles Select


1. Tính toán lý thuyết:
- Xung đầu vào: 0..5 V tại chân PB1/T1 (Timer1 External Clock, sườn lên CS12=1, CS11=1, CS10=1).
- TCNT1 là bộ đếm 16-bit (0..65535), gồm 4 nibble:
  + Nibble 0 (Bits 3..0): TCNT1 & 0x000F
  + Nibble 1 (Bits 7..4): (TCNT1 >> 4) & 0x000F
  + Nibble 2 (Bits 11..8): (TCNT1 >> 8) & 0x000F
  + Nibble 3 (Bits 15..12): (TCNT1 >> 12) & 0x000F
- Công tắc chọn nibble (PB2, PB3) có internal pull-up:
  + PB3=1, PB2=1 -> Chọn Nibble 0 (Bit 3..0)
  + PB3=1, PB2=0 -> Chọn Nibble 1 (Bit 7..4)
  + PB3=0, PB2=1 -> Chọn Nibble 2 (Bit 11..8)
  + PB3=0, PB2=0 -> Chọn Nibble 3 (Bit 15..12)
- Nút nhấn Reset TCNT1 tại PB4 (active-LOW) kèm thuật toán chống rung phím (Debounce).


```assembly
; ==============================================================================
; EXERCISE 14: Timer1 External Event Counter (PB1/T1) with 4-Nibble Selector (PB2, PB3)
; Reset button on PB4 with debounce. Display on PA0..PA3
; ==============================================================================
.include "m32def.inc"

.def TEMP        = R16
.def TCNT_L      = R17
.def TCNT_H      = R18
.def SEL_STATE   = R19
.def DISP_VAL    = R20

.org 0x0000
    rjmp RESET

RESET:
    ldi TEMP, HIGH(RAMEND)
    out SPH, TEMP
    ldi TEMP, LOW(RAMEND)
    out SPL, TEMP

    ; 1. Cấu hình PA0..PA3 Output cho LED
    ldi TEMP, 0x0F
    out DDRA, TEMP
    out PORTA, TEMP          ; Ban đầu tắt LED (active High) hoặc hiển thị 0

    ; 2. Cấu hình PB1 (T1 Input), PB2..PB4 Input kèm Pull-up
    cbi DDRB, 1              ; PB1: T1 pulse input
    cbi DDRB, 2              ; PB2: Select switch bit 0
    cbi DDRB, 3              ; PB3: Select switch bit 1
    cbi DDRB, 4              ; PB4: Reset button

    sbi PORTB, 2             ; Kéo pull-up PB2
    sbi PORTB, 3             ; Kéo pull-up PB3
    sbi PORTB, 4             ; Kéo pull-up PB4

    ; 3. Cấu hình Timer1 đếm xung sườn lên tại T1:
    ;    TCCR1A = 0 (Normal mode)
    ;    TCCR1B = (1<<CS12) | (1<<CS11) | (1<<CS10) = 0x07 (External clock T1 rising edge)
    clr TEMP
    out TCCR1A, TEMP
    out TCNT1H, TEMP
    out TCNT1L, TEMP
    ldi TEMP, (1<<CS12) | (1<<CS11) | (1<<CS10)
    out TCCR1B, TEMP

LOOP:
    ; Kiểm tra nút Reset PB4 (Active-Low)
    sbic PINB, 4
    rjmp CHECK_SELECT

    ; Nếu PB4 được nhấn: Delay debounce ~20ms rồi reset TCNT1
    clr TEMP
    out TCNT1H, TEMP
    out TCNT1L, TEMP

WAIT_RELEASE:
    sbis PINB, 4
    rjmp WAIT_RELEASE

CHECK_SELECT:
    ; Đọc 16-bit TCNT1 (Quy tắc AVR: Đọc TCNT1L trước, rồi đọc TCNT1H)
    in TCNT_L, TCNT1L
    in TCNT_H, TCNT1H

    ; Đọc trạng thái PB2, PB3:
    ; Lấy trạng thái công tắc (bit 3 và bit 2)
    in SEL_STATE, PINB
    lsr SEL_STATE
    lsr SEL_STATE
    andi SEL_STATE, 0x03     ; SEL_STATE = {PB3, PB2}

    cpi SEL_STATE, 3
    breq SHOW_NIBBLE_0
    cpi SEL_STATE, 2
    breq SHOW_NIBBLE_1
    cpi SEL_STATE, 1
    breq SHOW_NIBBLE_2
    ; Còn lại: SEL_STATE = 0 -> SHOW_NIBBLE_3

SHOW_NIBBLE_3:
    mov DISP_VAL, TCNT_H
    swap DISP_VAL
    andi DISP_VAL, 0x0F
    rjmp UPDATE_LEDS

SHOW_NIBBLE_2:
    mov DISP_VAL, TCNT_H
    andi DISP_VAL, 0x0F
    rjmp UPDATE_LEDS

SHOW_NIBBLE_1:
    mov DISP_VAL, TCNT_L
    swap DISP_VAL
    andi DISP_VAL, 0x0F
    rjmp UPDATE_LEDS

SHOW_NIBBLE_0:
    mov DISP_VAL, TCNT_L
    andi DISP_VAL, 0x0F

UPDATE_LEDS:
    out PORTA, DISP_VAL
    rjmp LOOP

```

```c
/*
 * EXERCISE 14: Timer1 External Pulse Counter with 4 Nibbles Select
 * Input pulse at PB1/T1. Select switches at PB2, PB3. Reset at PB4.
 */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

int main(void) {
    // 1. Cấu hình PA0..PA3 là Output
    DDRA |= 0x0F;
    PORTA &= 0xF0;

    // 2. Cấu hình Port B: PB1 input, PB2..PB4 input có pull-up
    DDRB &= ~((1 << PB1) | (1 << PB2) | (1 << PB3) | (1 << PB4));
    PORTB |= (1 << PB2) | (1 << PB3) | (1 << PB4);

    // 3. Khởi tạo Timer1 chế độ Normal, đếm xung cạnh lên chân T1 (CS12|CS11|CS10)
    TCCR1A = 0;
    TCNT1 = 0;
    TCCR1B = (1 << CS12) | (1 << CS11) | (1 << CS10);

    while (1) {
        // Kiểm tra nút Reset PB4
        if (!(PINB & (1 << PB4))) {
            _delay_ms(20); // Debounce
            if (!(PINB & (1 << PB4))) {
                TCNT1 = 0; // Reset giá trị bộ đếm
                while (!(PINB & (1 << PB4))); // Chờ nhả phím
            }
        }

        // Đọc giá trị 16-bit TCNT1 một cách an toàn
        uint16_t count = TCNT1;

        // Đọc công tắc chọn nibble tại PB3, PB2
        uint8_t sel = (PINB >> 2) & 0x03;
        uint8_t nibble = 0;

        switch (sel) {
            case 3: // PB3=1, PB2=1 -> Nibble 0 (Bits 3..0)
                nibble = count & 0x0F;
                break;
            case 2: // PB3=1, PB2=0 -> Nibble 1 (Bits 7..4)
                nibble = (count >> 4) & 0x0F;
                break;
            case 1: // PB3=0, PB2=1 -> Nibble 2 (Bits 11..8)
                nibble = (count >> 8) & 0x0F;
                break;
            case 0: // PB3=0, PB2=0 -> Nibble 3 (Bits 15..12)
                nibble = (count >> 12) & 0x0F;
                break;
        }

        // Hiển thị ra 4 LED tại PA0..PA3
        PORTA = (PORTA & 0xF0) | (nibble & 0x0F);
    }
    return 0;
}

```

---

## EXERCISE 15: Timer1 PWM 4-Level Brightness Controller


1. Tính toán lý thuyết:
- Tần số PWM:
  f_PWM = F_CPU / (256 * N) = 16 MHz / (256 * 64) = 976.5625 Hz.
- Chế độ: Fast PWM 8-bit trên Timer1:
  + WGM13 = 0, WGM12 = 1, WGM11 = 0, WGM10 = 1 (Mode 5: Fast PWM 8-bit, TOP = 0x00FF = 255).
  + Ngõ ra: Kênh A trên chân PD5/OC1A. Chế độ non-inverting: COM1A1 = 1, COM1A0 = 0.
  + Prescaler N = 64: CS11 = 1, CS10 = 1.
- Tính giá trị OCR1A cho 4 mức độ sáng:
  + Mức 1 (~10% Duty Cycle): OCR1A = round(255 * 0.10) = 26 (Duty thực tế: 26/256 = 10.16%).
  + Mức 2 (~35% Duty Cycle): OCR1A = round(255 * 0.35) = 89 (Duty thực tế: 89/256 = 34.77%).
  + Mức 3 (~65% Duty Cycle): OCR1A = round(255 * 0.65) = 166 (Duty thực tế: 166/256 = 64.84%).
  + Mức 4 (~90% Duty Cycle): OCR1A = round(255 * 0.90) = 230 (Duty thực tế: 230/256 = 89.84%).
- Nút nhấn tại PB2 (kèm pull-up) mỗi lần nhấn sẽ chuyển tuần tự: Mức 1 -> Mức 2 -> Mức 3 -> Mức 4 -> Mức 1.


```assembly
; ==============================================================================
; EXERCISE 15: Timer1 Fast PWM 8-bit on PD5/OC1A (976.56 Hz)
; 4 Brightness Levels: 10% (OCR1A=26), 35% (OCR1A=89), 65% (OCR1A=166), 90% (OCR1A=230)
; Button on PB2 advances duty cycle cyclically.
; ==============================================================================
.include "m32def.inc"

.def TEMP        = R16
.def LEVEL_IDX   = R17

.org 0x0000
    rjmp RESET

RESET:
    ldi TEMP, HIGH(RAMEND)
    out SPH, TEMP
    ldi TEMP, LOW(RAMEND)
    out SPL, TEMP

    ; 1. Cấu hình chân PD5 (OC1A) là Output cho LED điều chế xung PWM
    sbi DDRD, 5

    ; 2. Cấu hình PB2 là Input có Pull-up cho nút bấm chuyển mức
    cbi DDRB, 2
    sbi PORTB, 2

    ; 3. Cấu hình Timer1 Fast PWM 8-bit (Mode 5):
    ;    COM1A1 = 1, COM1A0 = 0 (Clear OC1A on Compare Match, Set at BOTTOM)
    ;    WGM10 = 1 (TCCR1A)
    ;    WGM12 = 1 (TCCR1B)
    ;    Prescaler 64: CS11 = 1, CS10 = 1 (TCCR1B)
    ldi TEMP, (1<<COM1A1) | (1<<WGM10)
    out TCCR1A, TEMP

    ldi TEMP, (1<<WGM12) | (1<<CS11) | (1<<CS10)
    out TCCR1B, TEMP

    ; 4. Khởi tạo mức ban đầu (Mức 1: ~10% -> OCR1A = 26)
    clr LEVEL_IDX
    rcall APPLY_LEVEL

MAIN_LOOP:
    ; Quét nút nhấn PB2 (Active-LOW)
    sbic PINB, 2
    rjmp MAIN_LOOP

    ; Phát hiện nhấn -> Chống rung phím
    rcall DELAY_DEBOUNCE
    sbic PINB, 2
    rjmp MAIN_LOOP

    ; Chuyển sang mức kế tiếp (0 -> 1 -> 2 -> 3 -> 0)
    inc LEVEL_IDX
    cpi LEVEL_IDX, 4
    brne SET_DUTY
    clr LEVEL_IDX

SET_DUTY:
    rcall APPLY_LEVEL

WAIT_RELEASE:
    sbis PINB, 2
    rjmp WAIT_RELEASE
    rcall DELAY_DEBOUNCE
    rjmp MAIN_LOOP

; --- Cập nhật OCR1A dựa trên LEVEL_IDX ---
APPLY_LEVEL:
    cpi LEVEL_IDX, 0
    breq LVL_0
    cpi LEVEL_IDX, 1
    breq LVL_1
    cpi LEVEL_IDX, 2
    breq LVL_2
    ; Mức 3 (~90%)
    ldi TEMP, 230
    rjmp WRITE_OCR1A
LVL_0:
    ldi TEMP, 26             ; 10%
    rjmp WRITE_OCR1A
LVL_1:
    ldi TEMP, 89             ; 35%
    rjmp WRITE_OCR1A
LVL_2:
    ldi TEMP, 166            ; 65%

WRITE_OCR1A:
    clr R18
    out OCR1AH, R18          ; Ghi byte cao trước
    out OCR1AL, TEMP         ; Ghi byte thấp sau
    ret

; Delay chống rung phần cứng ~20ms
DELAY_DEBOUNCE:
    ldi R18, 100
D_L1:
    ldi R19, 250
D_L2:
    dec R19
    brne D_L2
    dec R18
    brne D_L1
    ret

```

```c
/*
 * EXERCISE 15: Timer1 Fast PWM 8-bit LED Brightness (C Implementation)
 * Frequency = 976.56 Hz on PD5/OC1A. PB2 Button selects 10%, 35%, 65%, 90%
 */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

const uint8_t duty_table[4] = {26, 89, 166, 230}; // Tương ứng 10%, 35%, 65%, 90%

int main(void) {
    // 1. Cấu hình chân PD5/OC1A là Output
    DDRD |= (1 << PD5);

    // 2. Cấu hình nút nhấn PB2 Input có Pull-up
    DDRB &= ~(1 << PB2);
    PORTB |= (1 << PB2);

    // 3. Khởi tạo Timer1 Fast PWM 8-bit non-inverting trên OC1A, Prescaler 64
    TCCR1A = (1 << COM1A1) | (1 << WGM10);
    TCCR1B = (1 << WGM12) | (1 << CS11) | (1 << CS10);

    uint8_t level = 0;
    OCR1A = duty_table[level]; // Khởi tạo mức 10%

    while (1) {
        // Kiểm tra nút nhấn PB2 (Active-LOW)
        if (!(PINB & (1 << PB2))) {
            _delay_ms(25); // Debounce
            if (!(PINB & (1 << PB2))) {
                level = (level + 1) % 4;     // Tăng mức 0..3 tuần tự
                OCR1A = duty_table[level];   // Cập nhật độ rộng xung mới

                while (!(PINB & (1 << PB2))); // Chờ nhả phím
                _delay_ms(25);
            }
        }
    }
    return 0;
}

```
