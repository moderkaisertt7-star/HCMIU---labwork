; LAB 8.4 — Timer1 hardware OC1A toggle, 1 Hz wave on PD5
; F_CPU=16MHz, N=256, OCR1A=31249 -> compare every 0.5s
.include "m32def.inc"
.org 0x0000
    rjmp RESET

RESET:
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    sbi DDRD, 5                ; enable OC1A pin (PD5)
    cbi PORTD, 5               ; initial pin LOW
    clr r16
    out TCCR1A, r16
    out TCCR1B, r16            ; stop Timer1 for setup
    out TCNT1H, r16
    out TCNT1L, r16
    ldi r16, high(31249)
    out OCR1AH, r16            ; 16-bit write: HIGH then LOW
    ldi r16, low(31249)
    out OCR1AL, r16
    ldi r16, (1<<COM1A0)
    out TCCR1A, r16            ; toggle OC1A on compare
    ldi r16, (1<<WGM12)|(1<<CS12)
    out TCCR1B, r16            ; CTC mode, prescaler 256

RUN:
    rjmp RUN                   ; timer toggles the pin in hardware