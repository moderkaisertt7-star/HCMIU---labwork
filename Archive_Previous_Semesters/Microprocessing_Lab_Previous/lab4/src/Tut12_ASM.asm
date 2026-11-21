; T12: ATmega32A / 16 MHz / Timer1 CTC / polling OCF1A
; PA2 GREEN for 3 s, PA1 YELLOW for 1 s, PA0 RED for 3 s.
; Timer1 keeps running. One state transition occurs on a compare event.
.include "m32def.inc"
.org 0x0000
    rjmp RESET
RESET:
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x07
    out DDRA, r16               ; three LED outputs PA0..PA2
    clr r16
    out PORTA, r16
    out TCCR1A, r16             ; WGM11:10=00
    out TCCR1B, r16             ; timer stopped for setup
    out TCNT1H, r16
    out TCNT1L, r16
    ldi r16, high(62499)
    out OCR1AH, r16
    ldi r16, low(62499)
    out OCR1AL, r16             ; (62499+1)*256/16MHz = 1s
    ldi r16, (1<<OCF1A)
    out TIFR, r16               ; W1C pending compare flag
    ldi r16, 0x04
    out PORTA, r16              ; GREEN immediately
    ldi r20, 3                  ; seconds remaining
    clr r21                     ; state 0 GREEN, 1 YELLOW, 2 RED
    ldi r16, (1<<WGM12)|(1<<CS12)
    out TCCR1B, r16             ; CTC TOP=OCR1A; clock/256
WAIT_TICK:
    in r16, TIFR
    sbrs r16, OCF1A
    rjmp WAIT_TICK
    ldi r16, (1<<OCF1A)
    out TIFR, r16               ; acknowledge exactly one tick
    dec r20
    brne WAIT_TICK
    cpi r21, 0
    breq START_YELLOW
    cpi r21, 1
    breq START_RED
START_GREEN:
    ldi r16, 0x04
    out PORTA, r16              ; only GREEN ON
    ldi r20, 3
    clr r21
    rjmp WAIT_TICK
START_YELLOW:
    ldi r16, 0x02
    out PORTA, r16              ; only YELLOW ON
    ldi r20, 1
    ldi r21, 1
    rjmp WAIT_TICK
START_RED:
    ldi r16, 0x01
    out PORTA, r16              ; only RED ON
    ldi r20, 3
    ldi r21, 2
    rjmp WAIT_TICK