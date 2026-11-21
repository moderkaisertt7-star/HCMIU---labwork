;====================================================================
; Course: Microprocessing Systems Laboratory (EE084IU)
; Lab 8.1 - Exercise for Lab Work 1
; Target MCU: ATmega328P @ 16 MHz
; Description:
;   LED on PD0: ON for 125 ms, OFF for 375 ms → 2 Hz, 25% duty cycle
;
; Timing calculation at 16 MHz:
;   125 ms = 2,000,000 clock cycles → R25:R24 = 125
;   375 ms = 6,000,000 clock cycles → R25:R24 = 375
;   Period = 125 + 375 = 500 ms → frequency = 2 Hz
;====================================================================

.INCLUDE "m32def.inc"

.CSEG
.ORG 0x0000
    RJMP RESET

RESET:
    ; Initialize Stack Pointer
    LDI R16, HIGH(RAMEND)
    OUT SPH, R16
    LDI R16, LOW(RAMEND)
    OUT SPL, R16

    ; Configure PD0 as Output
    SBI DDRD, 0                 ; PD0 = output

MAIN:
    ; LED ON for 125 ms  (25% duty cycle)
    SBI PORTD, 0                ; PD0 HIGH
    LDI R24, LOW(125)           ; 125 ms
    LDI R25, HIGH(125)
    RCALL DELAY_MS

    ; LED OFF for 375 ms (75% duty cycle)
    CBI PORTD, 0                ; PD0 LOW
    LDI R24, LOW(375)           ; 375 ms
    LDI R25, HIGH(375)
    RCALL DELAY_MS

    RJMP MAIN                   ; Loop forever

.INCLUDE "delay_ms.inc"
