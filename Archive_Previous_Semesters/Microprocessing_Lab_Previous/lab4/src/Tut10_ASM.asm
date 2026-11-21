; T10: Timer1 input capture period check on ICP1 (PD6)
; F_CPU=16MHz, /8 => 2MHz ticks; 100Hz input => ~20,000 ticks
; PA0 ON for periods 19,000..21,000; PA1 ON otherwise.
.include "m32def.inc"
.org 0x0000
    rjmp RESET
RESET:
    ldi r16, HIGH(RAMEND)
    out SPH, r16
    ldi r16, LOW(RAMEND)
    out SPL, r16
    ldi r16, 0x03
    out DDRA, r16
    clr r16
    out PORTA, r16
    cbi DDRD, PD6              ; ICP1 input
    clr r16
    out TCCR1A, r16
    out TCCR1B, r16             ; stop Timer1
    out TCNT1H, r16
    out TCNT1L, r16
    ldi r16, (1<<ICF1)
    out TIFR, r16              ; clear stale capture flag
    ldi r16, (1<<ICES1)|(1<<CS11) ; rising capture, prescaler /8
    out TCCR1B, r16
    clr r17                    ; first capture not yet seen
WAIT_CAPTURE:
    in r16, TIFR
    sbrs r16, ICF1
    rjmp WAIT_CAPTURE
    in r18, ICR1L             ; low byte first, latches high
    in r19, ICR1H
    ldi r16, (1<<ICF1)
    out TIFR, r16             ; W1C flag
    tst r17
    brne HAVE_PREVIOUS
    mov r20, r18
    mov r21, r19
    ldi r17, 1
    rjmp WAIT_CAPTURE
HAVE_PREVIOUS:
    mov r22, r18              ; current - previous, modulo 65536
    mov r23, r19
    sub r22, r20
    sbc r23, r21
    mov r20, r18
    mov r21, r19
    ldi r24, LOW(19000)
    ldi r25, HIGH(19000)
    cp r22, r24
    cpc r23, r25
    brlo BAD
    ldi r24, LOW(21001)
    ldi r25, HIGH(21001)
    cp r22, r24
    cpc r23, r25
    brsh BAD
GOOD:
    ldi r16, 0x01             ; PA0 valid (~100 Hz)
    out PORTA, r16
    rjmp WAIT_CAPTURE
BAD:
    ldi r16, 0x02             ; PA1 invalid frequency
    out PORTA, r16
    rjmp WAIT_CAPTURE