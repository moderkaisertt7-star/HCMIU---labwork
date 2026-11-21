;====================================================================
; Exercise 14: Timer1 External Event Counter with 4-LED Nibble Selection & Reset
; Target MCU: ATmega32A
; Clock Frequency: 16.0 MHz External Crystal
; Description:
;   - PB1/T1 receives external clock pulse (rising edge: CS12=1, CS11=1, CS10=1)
;   - PA0..PA3 display one selected 4-bit nibble of the 16-bit TCNT1 counter
;   - PB2 and PB3 are active-LOW inputs with pull-ups to select the active nibble:
;       PB3=1, PB2=1 -> Nibble 0 (bits 3..0)
;       PB3=1, PB2=0 -> Nibble 1 (bits 7..4)
;       PB3=0, PB2=1 -> Nibble 2 (bits 11..8)
;       PB3=0, PB2=0 -> Nibble 3 (bits 15..12)
;   - PB4 is active-LOW button with pull-up to reset TCNT1 to 0 (software reset)
;     with 20 ms debounce logic.
;====================================================================

.include "m32def.inc"

.def TEMP        = r16
.def DISP_VAL    = r17
.def CNT_L       = r24       ; TCNT1 low byte
.def CNT_H       = r25       ; TCNT1 high byte

.org 0x0000
    rjmp RESET

;--------------------------------------------------------------------
; Initialization
;--------------------------------------------------------------------
RESET:
    ; 1. Stack Pointer initialization
    ldi TEMP, high(RAMEND)
    out SPH, TEMP
    ldi TEMP, low(RAMEND)
    out SPL, TEMP

    ; 2. Configure PA0..PA3 as outputs for 4-bit nibble display
    in  TEMP, DDRA
    ori TEMP, 0x0F           ; PA0..PA3 output
    out DDRA, TEMP
    in  TEMP, PORTA
    andi TEMP, 0xF0          ; LEDs OFF initially
    out PORTA, TEMP

    ; 3. Configure Port B pins:
    ;    PB1 (T1)  : Input, no pull-up (driven by external pulse generator)
    ;    PB2, PB3  : Input with pull-up (nibble select switches)
    ;    PB4       : Input with pull-up (software counter reset button)
    in  TEMP, DDRB
    andi TEMP, ~((1 << PB1) | (1 << PB2) | (1 << PB3) | (1 << PB4))
    out DDRB, TEMP

    in  TEMP, PORTB
    andi TEMP, ~(1 << PB1)   ; PB1: no pull-up
    ori  TEMP, (1 << PB2) | (1 << PB3) | (1 << PB4) ; PB2, PB3, PB4 pull-ups ON
    out PORTB, TEMP

    ; 4. Configure Timer1 as 16-bit Normal Counter on T1 rising edge
    clr TEMP
    out TCCR1A, TEMP         ; Normal mode (WGM11:10 = 0)
    out TCNT1H, TEMP         ; Clear counter register (HIGH byte first!)
    out TCNT1L, TEMP         ; LOW byte second

    ; External clock on T1 pin, clock on rising edge: CS12=1, CS11=1, CS10=1
    ldi TEMP, (1 << CS12) | (1 << CS11) | (1 << CS10)
    out TCCR1B, TEMP

;--------------------------------------------------------------------
; Main Polling & Display Loop
;--------------------------------------------------------------------
MAIN_LOOP:
    ; 1. Check PB4 (Software Reset Button)
    sbic PINB, PB4           ; Skip next if PB4 is LOW (pressed)
    rjmp CHECK_DISPLAY       ; PB4 not pressed, proceed to display

    ; PB4 pressed: Debounce delay (~20 ms)
    rcall DELAY_20MS
    sbic PINB, PB4           ; Verify PB4 is still pressed
    rjmp CHECK_DISPLAY

    ; Reset 16-bit TCNT1 to 0 (HIGH byte first!)
    clr TEMP
    out TCNT1H, TEMP
    out TCNT1L, TEMP

WAIT_RELEASE:
    sbis PINB, PB4           ; Wait until PB4 is released (HIGH)
    rjmp WAIT_RELEASE
    rcall DELAY_20MS         ; Debounce release

CHECK_DISPLAY:
    ; 2. Read 16-bit TCNT1 safely (LOW byte first, then HIGH byte)
    in  CNT_L, TCNT1L
    in  CNT_H, TCNT1H

    ; 3. Read PB2 and PB3 to select active nibble
    in  TEMP, PINB
    sbrs TEMP, PB3           ; Check PB3
    rjmp PB3_IS_LOW

PB3_IS_HIGH:
    sbrs TEMP, PB2           ; Check PB2
    rjmp SHOW_NIBBLE_1       ; PB3=1, PB2=0 -> Nibble 1 (bits 7..4)
    rjmp SHOW_NIBBLE_0       ; PB3=1, PB2=1 -> Nibble 0 (bits 3..0)

PB3_IS_LOW:
    sbrs TEMP, PB2           ; Check PB2
    rjmp SHOW_NIBBLE_3       ; PB3=0, PB2=0 -> Nibble 3 (bits 15..12)
    rjmp SHOW_NIBBLE_2       ; PB3=0, PB2=1 -> Nibble 2 (bits 11..8)

SHOW_NIBBLE_0:
    ; Nibble 0: bits 3..0 of CNT_L
    mov  DISP_VAL, CNT_L
    andi DISP_VAL, 0x0F
    rjmp UPDATE_LEDS

SHOW_NIBBLE_1:
    ; Nibble 1: bits 7..4 of CNT_L
    mov  DISP_VAL, CNT_L
    swap DISP_VAL
    andi DISP_VAL, 0x0F
    rjmp UPDATE_LEDS

SHOW_NIBBLE_2:
    ; Nibble 2: bits 11..8 of CNT_H
    mov  DISP_VAL, CNT_H
    andi DISP_VAL, 0x0F
    rjmp UPDATE_LEDS

SHOW_NIBBLE_3:
    ; Nibble 3: bits 15..12 of CNT_H
    mov  DISP_VAL, CNT_H
    swap DISP_VAL
    andi DISP_VAL, 0x0F

UPDATE_LEDS:
    ; Output DISP_VAL to PA0..PA3 preserving PA4..PA7
    in   TEMP, PORTA
    andi TEMP, 0xF0
    or   TEMP, DISP_VAL
    out  PORTA, TEMP

    rjmp MAIN_LOOP

;--------------------------------------------------------------------
; Software Delay Subroutine (~20 ms at 16 MHz)
;--------------------------------------------------------------------
DELAY_20MS:
    ldi  r18, 208
D_OUTER:
    ldi  r19, 255
D_INNER:
    dec  r19
    brne D_INNER
    dec  r18
    brne D_OUTER
    ret
