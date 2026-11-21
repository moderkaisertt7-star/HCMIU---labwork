;===============================================================
; Lab 2 - Exercise 3a: operator menu from look-up tables (LPM)
;   SW4 next operator   SW5 previous operator    (op = 0..3)
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
        out   DDRA, r16          ;LEDs: one LED per operator
        out   PORTB, r16         ;pull-ups on SW4..SW8
        mov   r15, r16           ;previous button state = all released
        rcall lcd_init
        clr   r23                ;op = 0 (r23 is not used by the drivers)

main:   rcall show
wait:   ldi   r24, 10
        rcall delay_ms
        rcall keys               ;r14 = new presses
        sbrc  r14, 0
        inc   r23                ;SW4: next
        sbrc  r14, 1
        dec   r23                ;SW5: previous
        andi  r23, 0x03          ;keep op in 0..3 (3+1 -> 0, 0-1 -> 3)
        tst   r14
        breq  wait
        rjmp  main

keys:   in    r16, PINB
        andi  r16, 0x1F          ;now: 0 = pressed
        mov   r17, r16
        com   r16                ;pressed = 1
        and   r16, r15           ;... and released at the last look
        mov   r15, r17
        mov   r14, r16
        ret

;---- show: line 0 "Operator:  x", line 1 the name ----
show:   ldi   r20, 0
        ldi   r21, 0
        rcall lcd_gotoxy
        ldi   r30, low(t_op*2)
        ldi   r31, high(t_op*2)
        rcall lcd_puts           ;"Operator:  "
        ; ---- symbol: one byte per entry, Z = sym_tab*2 + op ----
        ldi   r30, low(sym_tab*2)
        ldi   r31, high(sym_tab*2)
        clr   r16
        add   r30, r23
        adc   r31, r16
        lpm   r16, Z
        rcall lcd_data
        ; ---- LED pattern: Z = led_tab*2 + op ----
        ldi   r30, low(led_tab*2)
        ldi   r31, high(led_tab*2)
        clr   r16
        add   r30, r23
        adc   r31, r16
        lpm   r16, Z
        out   PORTA, r16
        ; ---- name: 8 bytes per entry, Z = name_tab*2 + op*8 ----
        ldi   r20, 1
        ldi   r21, 0
        rcall lcd_gotoxy
        mov   r16, r23
        lsl   r16                ;op*2
        lsl   r16                ;op*4
        lsl   r16                ;op*8
        ldi   r30, low(name_tab*2)
        ldi   r31, high(name_tab*2)
        add   r30, r16
        clr   r16
        adc   r31, r16
        rjmp  lcd_puts           ;print the name, ret -> main

t_op:     .db "Operator:  ", 0
sym_tab:  .db "+-x/"                      ;op = 0, 1, 2, 3
led_tab:  .db 0b00001, 0b00010, 0b00100, 0b01000
name_tab: .db "PLUS   ", 0                ;each entry = 8 bytes
          .db "MINUS  ", 0
          .db "TIMES  ", 0
          .db "DIVIDE ", 0
.include "lcd4.inc"
.include "delay.inc"
