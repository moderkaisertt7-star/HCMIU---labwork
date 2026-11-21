; LAB 8.1 — Timer0 overflow polling, ATmega32, 16 MHz
; PA0 LED toggles every 31 overflows (about 0.984 Hz flashing).
.include "m32def.inc"
.org 0x0000
    rjmp RESET

RESET:
    ldi r16, high(RAMEND) ; stack for future subroutines
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    sbi DDRA, 0           ; PA0 drives the LED
    cbi PORTA, 0          ; initial LED OFF
    clr r16                ; initialize before starting Timer0
    out TCCR0, r16         ; stop Timer0 for setup
    out TCNT0, r16         ; first overflow starts from zero
    ldi r16, (1<<TOV0)
    out TIFR, r16         ; clear any pending overflow flag
    ldi r16, 0x05         ; Normal mode, internal clk /1024
    out TCCR0, r16
    clr r20               ; accumulated overflow events

WAIT_OVERFLOW:
    in r16, TIFR
    sbrs r16, TOV0        ; skip jump if overflow is set
    rjmp WAIT_OVERFLOW
    ldi r16, (1<<TOV0)   ; W1C: clear the flag by writing 1
    out TIFR, r16
    inc r20
    cpi r20, 31          ; 31 * 16.384 ms = 507.904 ms
    brne WAIT_OVERFLOW
    clr r20
    in r16, PORTA
    ldi r17, 0x01
    eor r16, r17         ; toggle only PA0
    out PORTA, r16
    rjmp WAIT_OVERFLOW