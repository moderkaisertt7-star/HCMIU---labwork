; T06: Timer2 hardware CTC toggle = 500 Hz on OC2 / PD7
; ATmega32, F_CPU=16 MHz, synchronous Timer2, N=128, OCR2=124
.include "m32def.inc"
.org 0x0000
    rjmp RESET
RESET:
    sbi DDRD, PD7             ; OC2 output pin
    cbi PORTD, PD7
    clr r16
    out TCCR2, r16            ; stop Timer2 while configuring
    out TCNT2, r16
    out ASSR, r16             ; AS2=0: system clock (synchronous)
    ldi r16, 124
    out OCR2, r16
    ldi r16, (1<<WGM21)|(1<<COM20)|(1<<CS22)|(1<<CS20)
    out TCCR2, r16            ; CTC, toggle OC2, /128
MAIN:
    rjmp MAIN                 ; OC2 output is autonomous