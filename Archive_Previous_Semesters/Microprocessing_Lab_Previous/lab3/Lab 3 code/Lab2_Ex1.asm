;===============================================================
; Lab 2 - Exercise 1: arithmetic and logic flags explorer
; Student: Nguyễn Lê Minh Sang    ID: EEACIU24096
; Kit: MPS 2026, ATmega32A @ 16 MHz
;===============================================================
.include "m32def.inc"

.org    0x0000
        rjmp  reset             ; reset vector

.org    INT_VECTORS_SIZE        ; program starts after the vector table

.equ    OPA = 0x9C              ; first operand  (change, then rebuild)
.equ    OPB = 0x64              ; second operand

reset:  
        ldi   r16, high(RAMEND) ; stack pointer -> top of SRAM
        out   sph, r16
        ldi   r16, low(RAMEND)
        out   spl, r16

        ldi   r16, 0x1F
        out   PORTB, r16        ; pull-ups on SW4..SW8 (PB0..PB4)

        rcall lcd_init
        ldi   r30, low(t_help*2)
        ldi   r31, high(t_help*2)
        rcall lcd_puts          ; "4+ 5- 6& 7| 8^"

poll:   
        sbis  PINB, 0           ; SW4 -> ADD
        jmp   do_add
        sbis  PINB, 1           ; SW5 -> SUB
        jmp   do_sub
        sbis  PINB, 2           ; SW6 -> AND
        jmp   do_and
        sbis  PINB, 3           ; SW7 -> OR
        jmp   do_or
        sbis  PINB, 4           ; SW8 -> EOR
        jmp   do_eor
        rjmp  poll

; --- Operations Handlers ---
do_add: 
        ldi   r22, OPA
        ldi   r23, OPB
        add   r22, r23          ; r22 = A + B
        in    r2, SREG          ; save the flags at once!
        ldi   r25, '+'
        rjmp  show

do_sub: 
        ldi   r22, OPA
        ldi   r23, OPB
        sub   r22, r23          ; r22 = A - B
        in    r2, SREG
        ldi   r25, '-'
        rjmp  show

do_and: 
        ldi   r22, OPA
        ldi   r23, OPB
        and   r22, r23
        in    r2, SREG
        ldi   r25, '&'
        rjmp  show

do_or:  
        ldi   r22, OPA
        ldi   r23, OPB
        or    r22, r23
        in    r2, SREG
        ldi   r25, '|'
        rjmp  show

do_eor: 
        ldi   r22, OPA
        ldi   r23, OPB
        eor   r22, r23
        in    r2, SREG
        ldi   r25, '^'

; --- Display Logic ---
show:   
        ldi   r16, 0x01
        rcall lcd_cmd            ; clear the display
        ldi   r20, OPA
        rcall lcd_print_hex      ; line 0: "9C+64=00"
        mov   r16, r25
        rcall lcd_data           ; operator character
        ldi   r20, OPB
        rcall lcd_print_hex
        ldi   r16, '='
        rcall lcd_data
        mov   r20, r22
        rcall lcd_print_hex      ; result
        ldi   r20, 1
        ldi   r21, 0
        rcall lcd_gotoxy         ; line 1: "SREG --H---ZC"
        ldi   r30, low(t_sreg*2)
        ldi   r31, high(t_sreg*2)
        rcall lcd_puts
        mov   r20, r2
        rcall lcd_print_flags
        ldi   r24, 20
        rcall delay_ms           ; debounce the press

release:
        in    r16, PINB
        andi  r16, 0x1F
        cpi   r16, 0x1F          ; all five buttons released?
        brne  release
        ldi   r24, 20
        rcall delay_ms           ; debounce the release
        rjmp  poll

; --- Flash Data Tables ---
t_help: .db   "4+ 5- 6& 7| 8^", 0, 0
t_sreg: .db   "SREG ", 0

; --- Included Libraries ---
.include "lcd4.inc"
.include "lcdutil.inc"
.include "delay.inc"