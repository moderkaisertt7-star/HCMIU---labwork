.INCLUDE "m32def.inc"

.CSEG
.ORG 0x0000
    RJMP RESET

RESET:
    ; Kh?i t?o Stack Pointer cho ATmega32
    LDI R16, HIGH(RAMEND)
    OUT SPH, R16
    LDI R16, LOW(RAMEND)
    OUT SPL, R16

    ; C?u hình PORTD làm ngõ ra (8 LEDs)
    LDI R16, 0xFF
    OUT DDRD, R16

    ; C?u hình nút nh?n Mode trên PC0 (Input v?i di?n tr? kéo n?i)
    CBI DDRC, 0                 
    SBI PORTC, 0                

    CLR R20                     ; Thanh ghi luu ch? d? t?c d? (Mode 0..3)
    LDI R21, 0x01               ; Kh?i t?o 1 LED sáng b?t d?u t? bit 0 (0x01)

MAIN:
    OUT PORTD, R21              ; Xu?t tr?ng thái LED ra PORTD

    ; Ch?n th?i gian tr? d?a theo Mode t?c d? (R20)
    ; Mode 0: 1000ms, Mode 1: 500ms, Mode 2: 250ms, Mode 3: 125ms
    CPI R20, 0
    BREQ SET_1000
    CPI R20, 1
    BREQ SET_500
    CPI R20, 2
    BREQ SET_250
    ; Tru?ng h?p Mode 3: 125ms
    LDI R22, 5                  ; 5 l?n x 25ms = 125ms
    RJMP START_DELAY

SET_250:
    LDI R22, 10                 ; 10 x 25ms = 250ms
    RJMP START_DELAY

SET_500:
    LDI R22, 20                 ; 20 x 25ms = 500ms
    RJMP START_DELAY

SET_1000:
    LDI R22, 40                 ; 40 x 25ms = 1000ms

; Chia nh? th?i gian ch? thành các lát 25ms d? ki?m tra nút nh?n liên t?c
START_DELAY:
    LDI R24, LOW(25)
    LDI R25, HIGH(25)
    RCALL DELAY_MS              ; Tr? 25ms

    ; Ki?m tra nút nh?n trong lát c?t này (Active-LOW)
    SBIS PINC, 0                
    RJMP CHECK_PRESS            ; N?u có tác d?ng b?m phím

    DEC R22
    BRNE START_DELAY            ; N?u chua h?t th?i gian c?a bu?c, ti?p t?c lát tr? ti?p theo

    ; H?t th?i gian tr?, ti?n hành d?ch trái vòng LED (One-hot left shift)
    LSL R21
    BRNE MAIN
    LDI R21, 0x01               ; N?u d?ch quá bit 7 thì quay vòng v? l?i 0x01
    RJMP MAIN

CHECK_PRESS:
    ; Ch?ng d?i phím (Debounce 20ms)
    LDI R24, LOW(20)
    LDI R25, HIGH(20)
    RCALL DELAY_MS
    
    SBIS PINC, 0                
    RJMP DO_MODE_CHANGE         ; Xác nh?n b?m th?t s? h?p l?
    RJMP START_DELAY

DO_MODE_CHANGE:
    ; Chuy?n sang t?c d? k? ti?p (0 -> 1 -> 2 -> 3 -> 0)
    INC R20
    CPI R20, 4
    BRLO WAIT_KEY_RELEASE
    CLR R20

WAIT_KEY_RELEASE:
    ; Ð?m b?o không b? l?p ch? d? liên t?c n?u gi? phím quá lâu, 
    ; nhung v?n cho phép LED d?ch chuy?n theo nh?p th?i gian dang ch?y
    SBIS PINC, 0
    RJMP WAIT_KEY_RELEASE       
    RJMP START_DELAY

.INCLUDE "delay_ms.inc"
