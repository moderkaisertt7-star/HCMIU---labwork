; LAB 8.3 — Timer0 compare interrupt, LED toggles every 500 ms
; Uses r24:r25 EXCLUSIVELY in the ISR as the persistent counter.
.include "m32def.inc"
.org 0x0000
    rjmp RESET
.org OC0addr                  ; Timer0 compare vector, 0x0014
    rjmp TIMER0_COMPARE_ISR
.org 0x002A                   ; safely after all vectors

RESET:
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    sbi DDRA, 0
    cbi PORTA, 0
    ldi r24, low(500)         ; ISR-owned 16-bit countdown
    ldi r25, high(500)
    clr r16
    out TCCR0, r16
    out TCNT0, r16
    ldi r16, 249
    out OCR0, r16
    ldi r16, (1<<OCF0)
    out TIFR, r16             ; clear pending compare flag
    ldi r16, (1<<OCIE0)
    out TIMSK, r16            ; enable Timer0 compare IRQ
    ldi r16, (1<<WGM01)|(1<<CS01)|(1<<CS00)
    out TCCR0, r16
    sei                       ; globally enable interrupts

IDLE:
    rjmp IDLE                ; CPU free for other work

TIMER0_COMPARE_ISR:
    push r16
    in r16, SREG
    push r16                 ; preserve status flags
    push r17
    sbiw r24, 1              ; one 1-ms event elapsed
    brne ISR_DONE
    ldi r24, low(500)
    ldi r25, high(500)
    in r16, PORTA
    ldi r17, 0x01
    eor r16, r17
    out PORTA, r16           ; toggle PA0 every 500 ms
ISR_DONE:
    pop r17
    pop r16
    out SREG, r16
    pop r16
    reti