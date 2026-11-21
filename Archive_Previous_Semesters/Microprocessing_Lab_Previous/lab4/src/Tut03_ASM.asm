; LAB 8.2 — Timer0 CTC compare polling, 1 Hz LED on PA0
; F_CPU=16 MHz, prescaler=64, OCR0=249 => 1 ms/event.
.include "m32def.inc"
.org 0x0000
    rjmp RESET

RESET:
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    sbi DDRA, 0
    cbi PORTA, 0
    clr r16
    out TCCR0, r16       ; timer stopped during setup
    out TCNT0, r16
    ldi r16, 249
    out OCR0, r16
    ldi r16, (1<<OCF0)
    out TIFR, r16        ; clear pending compare flag
    ldi r16, (1<<WGM01)|(1<<CS01)|(1<<CS00)
    out TCCR0, r16       ; CTC, internal clk/64
    ldi r24, low(500)    ; count 500 one-ms events
    ldi r25, high(500)

WAIT_MATCH:
    in r16, TIFR
    sbrs r16, OCF0
    rjmp WAIT_MATCH
    ldi r16, (1<<OCF0)
    out TIFR, r16        ; write 1 to clear OCF0
    sbiw r24, 1          ; decrement the 16-bit ms counter
    brne WAIT_MATCH
    ldi r24, low(500)    ; reload for next half period
    ldi r25, high(500)
    in r16, PORTA
    ldi r17, 0x01
    eor r16, r17
    out PORTA, r16
    rjmp WAIT_MATCH