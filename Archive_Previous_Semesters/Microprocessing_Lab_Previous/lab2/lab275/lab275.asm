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

    ; C?u hình nút nh?n Mode trên PC0 (Input v?i di?n tr? kéo n?i)
    CBI DDRC, 0                 
    SBI PORTC, 0                

    CLR R18                     
    CLR R20                     ; Thanh ghi d?m giá tr? digit 0..15 (0..F)
    CLR R21                     ; Thanh ghi luu ch? d? t?c d? (speed mode 0..2)

SHOW:
    ; Gi?i mã ký t? t? Flash thông qua con tr? Z
    LDI ZL, LOW(SEG_TABLE*2)
    LDI ZH, HIGH(SEG_TABLE*2)
    ADD ZL, R20
    ADC ZH, R18
    LPM R16, Z                  
    OUT PORTA, R16              ; Xu?t mã ra PORTA hi?n th? lên LED 7 do?n

    ; Ki?m tra ch? d? t?c d? hi?n t?i trong R21 d? gán th?i gian tr? tuong ?ng
    CPI R21, 0
    BREQ SEC_1
    CPI R21, 1
    BREQ SEC_HALF

SEC_QUARTER:
    LDI R24, LOW(250)
    LDI R25, HIGH(250)
    RJMP WAIT_DIGIT

SEC_HALF:
    LDI R24, LOW(500)
    LDI R25, HIGH(500)
    RJMP WAIT_DIGIT

SEC_1:
    LDI R24, LOW(1000)
    LDI R25, HIGH(1000)

WAIT_DIGIT:
    RCALL DELAY_MS              ; Ch? theo th?i gian dã ch?n
    
    ; Tang giá tr? d?m hi?n th? ti?p theo
    INC R20
    ANDI R20, 0x0F              ; Gi?i h?n t? 0 d?n 15 (0x0F)

    ; Ki?m tra tr?ng thái nút nh?n trên PC0 (Active-LOW)
    SBIS PINC, 0                
    RJMP DEBOUNCE
    RJMP SHOW

DEBOUNCE:
    ; Ch?ng d?i phím (Debounce delay 20ms)
    LDI R24, LOW(20)
    LDI R25, HIGH(20)
    RCALL DELAY_MS
    
    SBIS PINC, 0                
    RJMP ACCEPT_KEY
    RJMP SHOW

ACCEPT_KEY:
    ; Chuy?n sang ch? d? t?c d? ti?p theo (0 -> 1 -> 2 -> quay v? 0)
    INC R21
    CPI R21, 3
    BRLO WAIT_RELEASE
    CLR R21

WAIT_RELEASE:
    ; Ch? ngu?i dùng th? nút nh?n ra tru?c khi ti?p t?c chu k? m?i
    SBIS PINC, 0
    RJMP WAIT_RELEASE
    RJMP SHOW

SEG_TABLE:
    .DB 0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07   ; 0, 1, 2, 3, 4, 5, 6, 7
    .DB 0x7F, 0x6F, 0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71   ; 8, 9, A, b, C, d, E, F

.INCLUDE "delay_ms.inc"
