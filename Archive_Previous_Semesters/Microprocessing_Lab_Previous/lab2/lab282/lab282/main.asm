;====================================================================
; Course: Microprocessing Systems Laboratory (EE084IU)
; Lab 8.2 - Exercise for Lab Work 2
; Target MCU: ATmega328P @ 16 MHz
; Description:
;   Pattern 1: Bouncing LED  LED0→LED7→LED0 (no end duplication)
;              Sequence: 01,02,04,08,10,20,40,80,40,20,10,08,04,02 (repeat)
;   Pattern 2: Progressive ON  MSB→LSB: 80,C0,E0,F0,F8,FC,FE,FF
;   Pattern 3: Progressive OFF MSB→LSB: 7F,3F,1F,0F,07,03,01,00
;   Step delay: 150 ms
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

    ; Configure PORTD as all outputs (8 LEDs)
    LDI R16, 0xFF
    OUT DDRD, R16

MAIN_LOOP:
    ;------------------------------------------------------------------
    ; Pattern 1a: Bounce LEFT  (LED0 → LED7, stop before repeating LED7)
    ; Sequence:   0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80
    ;------------------------------------------------------------------
    LDI R21, 0x01               ; start at LED0
BOUNCE_LEFT:
    OUT PORTD, R21
    RCALL WAIT_150
    LSL R21
    BRNE BOUNCE_LEFT            ; loop until shifted out (carry set, R21=0)

    ;------------------------------------------------------------------
    ; Pattern 1b: Bounce RIGHT (LED6 → LED0, skip LED7 which was last)
    ; Sequence:   0x40, 0x20, 0x10, 0x08, 0x04, 0x02
    ;------------------------------------------------------------------
    LDI R21, 0x40               ; start at LED6 (skip LED7 – already shown)
BOUNCE_RIGHT:
    OUT PORTD, R21
    RCALL WAIT_150
    LSR R21
    CPI R21, 0x00               ; stop before showing LED0 again (it's the start)
    BRNE BOUNCE_RIGHT

    ;------------------------------------------------------------------
    ; Pattern 2: Progressive ON, MSB (LED7) → LSB (LED0)
    ; 0x80, 0xC0, 0xE0, 0xF0, 0xF8, 0xFC, 0xFE, 0xFF
    ;------------------------------------------------------------------
    CLR R21                     ; accumulator
    LDI R22, 0x80               ; mask starts at MSB
GROW_MSB:
    OR  R21, R22                ; add LED from MSB side
    OUT PORTD, R21
    RCALL WAIT_150
    LSR R22                     ; move mask toward LSB
    BRNE GROW_MSB               ; until mask underflows (0x00)

    ;------------------------------------------------------------------
    ; Pattern 3: Progressive OFF, MSB (LED7) → LSB (LED0)
    ; 0x7F, 0x3F, 0x1F, 0x0F, 0x07, 0x03, 0x01, 0x00
    ;------------------------------------------------------------------
    LDI R21, 0xFF               ; all LEDs on
    LDI R22, 0x80               ; clear mask starts at MSB
SHRINK_MSB:
    MOV R18, R22
    COM R18                     ; invert mask  → 0x7F, 0x3F …
    AND R21, R18                ; clear one LED
    OUT PORTD, R21
    RCALL WAIT_150
    LSR R22                     ; move mask toward LSB
    BRNE SHRINK_MSB

    RJMP MAIN_LOOP

;------------------------------------------------------------------
; WAIT_150 – calls DELAY_MS with 150 ms
;------------------------------------------------------------------
WAIT_150:
    LDI R24, LOW(150)
    LDI R25, HIGH(150)
    RCALL DELAY_MS
    RET

.INCLUDE "delay_ms.inc"
