; LAB 8.5 — Timer0 counts rising edges at PB0/T0
; Show low four counter bits on LEDs PA0..PA3.
.include "m32def.inc"
.org 0x0000
    rjmp RESET
RESET:
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x0F
    out DDRA, r16               ; 4 LED outputs
    clr r16
    out PORTA, r16
    cbi DDRB, 0                ; T0/PB0 must be input
    cbi PORTB, 0               ; external clock actively drives pin
    out TCCR0, r16             ; stop during configuration
    out TCNT0, r16             ; reset pulse count
    ldi r16, 0x07              ; CS02:0=111, external rising
    out TCCR0, r16
LOOP:
    in r16, TCNT0              ; read hardware pulse count
    andi r16, 0x0F
    out PORTA, r16             ; show bits 3..0
    rjmp LOOP