; T09: Timer0 Fast PWM on PB3/OC0, button PB1 selects 25% / 75%
; Active-LOW button PB1 with pull-up: released=25%, pressed=75%
.include "m32def.inc"
.org 0x0000
    rjmp RESET
RESET:
    sbi DDRB, PB3          ; PB3 is OC0 output
    cbi DDRB, PB1          ; PB1 button input
    sbi PORTB, PB1         ; internal pull-up
    clr r16
    out TCCR0, r16
    out TCNT0, r16
    ldi r16, 64
    out OCR0, r16
    ldi r16, (1<<WGM00)|(1<<WGM01)|(1<<COM01)|(1<<CS01)|(1<<CS00)
    out TCCR0, r16         ; Fast PWM, non-inverting, /64
LOOP:
    sbis PINB, PB1         ; if released, skip BRIGHT branch
    rjmp BRIGHT
DIM:
    ldi r16, 64            ; ≈25% duty
    out OCR0, r16
    rjmp LOOP
BRIGHT:
    ldi r16, 192           ; ≈75% duty
    out OCR0, r16
    rjmp LOOP