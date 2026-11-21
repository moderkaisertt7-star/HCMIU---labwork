; T08: Timer1 external rising-edge 16-bit counter; 4-LED nibble display
; PB1/T1 = pulse input. PB2 and PB3 select one of four nibbles.
; Both switches released -> bits 3..0; PB2 pressed -> 7..4;
; PB3 pressed -> 11..8; both pressed -> 15..12.
.include "m32def.inc"
.org 0x0000
    rjmp RESET
RESET:
    ldi r16, HIGH(RAMEND)
    out SPH, r16
    ldi r16, LOW(RAMEND)
    out SPL, r16
    ldi r16, 0x0F
    out DDRA, r16                ; only PA0..PA3 are outputs
    clr r16
    out PORTA, r16
    cbi DDRB, PB1                ; PB1/T1: driven pulse input
    cbi PORTB, PB1               ; no pull-up on pulse input
    cbi DDRB, PB2                ; PB2: nibble selector
    cbi DDRB, PB3                ; PB3: nibble selector
    sbi PORTB, PB2               ; enable button pull-ups
    sbi PORTB, PB3
    clr r16
    out TCCR1A, r16
    out TCCR1B, r16              ; stop Timer1
    out TCNT1H, r16             ; write HIGH then LOW
    out TCNT1L, r16
    ldi r16, (1<<CS12)|(1<<CS11)|(1<<CS10)
    out TCCR1B, r16             ; external T1 rising edges
MAIN:
    in r16, TCNT1L              ; read LOW first to latch HIGH
    in r17, TCNT1H
    in r18, PINB
    ldi r19, 0                  ; selector 0..3
    sbrs r18, PB2
    ori r19, 0x01
    sbrs r18, PB3
    ori r19, 0x02
    cpi r19, 0
    breq SHOW_0
    cpi r19, 1
    breq SHOW_1
    cpi r19, 2
    breq SHOW_2
SHOW_3:
    mov r20, r17
    swap r20                    ; bits 15..12
    rjmp SHOW_OUT
SHOW_2:
    mov r20, r17                ; bits 11..8
    rjmp SHOW_OUT
SHOW_1:
    mov r20, r16
    swap r20                    ; bits 7..4
    rjmp SHOW_OUT
SHOW_0:
    mov r20, r16                ; bits 3..0
SHOW_OUT:
    andi r20, 0x0F
    out PORTA, r20
    rjmp MAIN