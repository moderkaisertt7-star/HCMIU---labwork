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
    LDI R20, 0x0F               ; Kh?i t?o bi?n d?m b?t d?u t? giá tr? l?n nh?t: F (15)

SHOW_DIGIT:
    LDI ZL, LOW(SEG_TABLE*2)
    LDI ZH, HIGH(SEG_TABLE*2)
    
    ADD ZL, R20
    ADC ZH, R18

    LPM R16, Z                  
    OUT PORTA, R16              ; Xu?t mã ra PORTA hi?n th? lên LED 7 do?n

    ; T?o d? tr? kho?ng 750 ms theo yêu c?u Bài 8.4
    LDI R24, LOW(750)
    LDI R25, HIGH(750)
    RCALL DELAY_MS

    ; Gi?m bi?n d?m t? F v? 0, n?u du?i 0 thì cu?n vòng (wrap-around) v? F (0x0F)
    DEC R20
    CPI R20, 0xFF               ; Ki?m tra xem R20 dã gi?m xu?ng du?i 0 chua (-1 tuong duong 0xFF)
    BRNE SHOW_DIGIT
    LDI R20, 0x0F               ; N?u dúng là du?i 0 thì gán l?i b?ng F d? d?m ngu?c ti?p
    RJMP SHOW_DIGIT

SEG_TABLE:
    .DB 0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07   ; 0, 1, 2, 3, 4, 5, 6, 7
    .DB 0x7F, 0x6F, 0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71   ; 8, 9, A, b, C, d, E, F

.INCLUDE "delay_ms.inc"
