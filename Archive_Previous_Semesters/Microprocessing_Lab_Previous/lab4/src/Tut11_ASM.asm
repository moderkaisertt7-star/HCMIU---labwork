; LAB 8.7 — Timer1 Fast PWM 8-bit, OC1A/PD5
; Cycles through OCR1A=64,128,192 every 2 s (Timer0 CTC).
.include "m32def.inc"
.org 0x0000
    rjmp RESET
RESET:
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    sbi DDRD, 5              ; OC1A output on PD5
    clr r16
    out TCCR1A, r16
    out TCCR1B, r16
    out TCNT1H, r16
    out TCNT1L, r16
    ; OCR1A is 16-bit; values below 256 need a zero high byte.
    clr r16
    out OCR1AH, r16
    ldi r16, 64
    out OCR1AL, r16
    ldi r16, (1<<COM1A1)|(1<<WGM10)
    out TCCR1A, r16         ; Fast PWM 8-bit, non-inverting
    ldi r16, (1<<WGM12)|(1<<CS11)|(1<<CS10)
    out TCCR1B, r16         ; prescale 64; ~976.56 Hz
    clr r16
    out TCCR0, r16
    out TCNT0, r16
    ldi r16, 249
    out OCR0, r16
    ldi r16, (1<<OCF0)
    out TIFR, r16
    ldi r16, (1<<WGM01)|(1<<CS01)|(1<<CS00)
    out TCCR0, r16         ; Timer0 = 1-ms CTC time base

PWM_LOOP:
    ldi r16, 0
    out OCR1AH, r16
    ldi r16, 64            ; ~25% duty
    out OCR1AL, r16
    rcall WAIT_2S
    clr r16
    out OCR1AH, r16
    ldi r16, 128           ; ~50% duty
    out OCR1AL, r16
    rcall WAIT_2S
    clr r16
    out OCR1AH, r16
    ldi r16, 192           ; ~75% duty
    out OCR1AL, r16
    rcall WAIT_2S
    rjmp PWM_LOOP

WAIT_2S:
    ldi r24, low(2000)     ; 2,000 x 1 ms
    ldi r25, high(2000)
WAIT_ONE_MS:
    in r16, TIFR
    sbrs r16, OCF0
    rjmp WAIT_ONE_MS
    ldi r16, (1<<OCF0)
    out TIFR, r16
    sbiw r24, 1
    brne WAIT_ONE_MS
    ret