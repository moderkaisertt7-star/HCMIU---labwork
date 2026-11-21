;===============================================================
; Lab 2 - Set-up check: text on the LCD, running light on Port A
; Student: <name>        ID: <student ID>
; Kit: MPS 2026, ATmega32A @ 16 MHz
;===============================================================
.include "m32def.inc"
.org    0x0000
        rjmp  reset              ;reset vector
.org    INT_VECTORS_SIZE         ;program starts after the vector table
reset:  ldi   r16, high(RAMEND)  ;stack pointer -> top of SRAM
        out   sph, r16
        ldi   r16, low(RAMEND)
        out   spl, r16
        ldi   r16, 0x1F
        out   DDRA, r16          ;PA0..PA4 -> LED10..LED6 (via P19)
        rcall lcd_init           ;LCD on Port D, 4-bit mode
        ldi   r30, low(t_l1*2)   ;Z -> first text (Flash byte address)
        ldi   r31, high(t_l1*2)
        rcall lcd_puts
        ldi   r20, 1             ;row 1
        ldi   r21, 0             ;column 0
        rcall lcd_gotoxy
        ldi   r30, low(t_l2*2)
        ldi   r31, high(t_l2*2)
        rcall lcd_puts
        ldi   r17, 0x01          ;one lit LED
run:    out   PORTA, r17
        ldi   r24, 200
        rcall delay_ms
        lsl   r17                ;next LED
        cpi   r17, 0x20          ;past LED6?
        brne  run
        ldi   r17, 0x01
        rjmp  run
t_l1:   .db   "MPS LAB 2", 0     ;9 chars + 0 = 10 bytes (even)
t_l2:   .db   "Kit check OK", 0, 0
.include "lcd4.inc"
.include "delay.inc"
