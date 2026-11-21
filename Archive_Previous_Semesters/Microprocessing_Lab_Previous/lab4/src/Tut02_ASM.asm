; T02: Software counter R20 displayed on four PORTA LEDs
; Timer0 overflow gives ~16.384 ms; 61 overflows ~0.999424 s
.include "m32def.inc"
.org 0x0000
    rjmp RESET
RESET:
    ldi r16, HIGH(RAMEND)
    out SPH, r16
    ldi r16, LOW(RAMEND)
    out SPL, r16
    ldi r16, 0x0F
    out DDRA, r16
    clr r20                 ; software count for display
    out PORTA, r20
    clr r16
    out TCCR0, r16         ; stop during setup
    out TCNT0, r16
    ldi r16, (1<<TOV0)
    out TIFR, r16          ; clear pending TOV0
    ldi r16, 0x05
    out TCCR0, r16         ; Normal mode, clk/1024
MAIN:
    ldi r21, 61
POLL:
    in r16, TIFR
    sbrs r16, TOV0
    rjmp POLL
    ldi r16, (1<<TOV0)
    out TIFR, r16          ; acknowledge exactly one overflow
    dec r21
    brne POLL
    inc r20
    mov r16, r20
    andi r16, 0x0F
    out PORTA, r16         ; show low four counter bits
    rjmp MAIN