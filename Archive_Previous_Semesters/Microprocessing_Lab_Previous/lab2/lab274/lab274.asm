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

    ; C?u hình PA0..PA6 làm ngõ ra (Output) cho LED 7 do?n
    LDI R16, 0x7F
    OUT DDRA, R16

    CLR R18                     
    CLR R20                     ; Thanh ghi d?m ký t? 0..15 (0..F)

SHOW_DIGIT:
    LDI ZL, LOW(SEG_TABLE*2)
    LDI ZH, HIGH(SEG_TABLE*2)
    
    ADD ZL, R20
    ADC ZH, R18

    LPM R16, Z                  
    OUT PORTA, R16              ; Xu?t mã ra PORTA hi?n th? lên LED 7 do?n

    ; T?o d? tr? kho?ng 1 giây (1000 ms)
    LDI R24, LOW(1000)
    LDI R25, HIGH(1000)
    RCALL DELAY_MS

    INC R20
    ANDI R20, 0x0F
    RJMP SHOW_DIGIT

SEG_TABLE:
    .DB 0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07   ; 0, 1, 2, 3, 4, 5, 6, 7
    .DB 0x7F, 0x6F, 0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71   ; 8, 9, A, b, C, d, E, F

.INCLUDE "delay_ms.inc"
