;====================================================================
; Course: Microprocessing Systems Laboratory (EE084IU)
; Lab 2.1: Designing Assembly Delay with One LED
; Target MCU: ATmega328P @ 16 MHz External Crystal
; Description: Blinks a single LED on PD0 at 1 Hz (500ms ON, 500ms OFF)
;====================================================================

.INCLUDE "m32def.inc"

.CSEG
.ORG 0x0000
    RJMP RESET

RESET:
    ; 1. Initialize Stack Pointer (SP)
    LDI R16, HIGH(RAMEND)
    OUT SPH, R16
    LDI R16, LOW(RAMEND)
    OUT SPL, R16

    ; 2. Configure PD0 as Output pin
    SBI DDRD, 0                 ; Set DDRD bit 0 to 1 (Output)

MAIN:
    ; 3. Turn LED ON for 500 ms
    SBI PORTD, 0                ; Set PD0 HIGH
    LDI R24, LOW(500)           ; Load lower byte of 500
    LDI R25, HIGH(500)          ; Load upper byte of 500
    RCALL DELAY_MS              ; Call 500 ms delay routine

    ; 4. Turn LED OFF for 500 ms
    CBI PORTD, 0                ; Clear PD0 LOW
    LDI R24, LOW(500)           ; Load lower byte of 500
    LDI R25, HIGH(500)          ; Load upper byte of 500
    RCALL DELAY_MS              ; Call 500 ms delay routine

    RJMP MAIN                   ; Loop forever

; Include external millisecond delay library
.INCLUDE "delay_ms.inc"