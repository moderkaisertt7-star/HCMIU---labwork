;====================================================================
; Exercise 15: Timer1 8-Bit Fast PWM Brightness Controller on OC1A / PD5
; Target MCU: ATmega32A
; Clock Frequency: 16.0 MHz External Crystal
; Description:
;   - Timer1 in 8-bit Fast PWM mode (Mode 5: WGM12=1, WGM10=1, TOP=0x00FF)
;   - Prescaler N = 64 (CS11=1, CS10=1)
;   - Carrier Frequency: f_PWM = 16,000,000 / (64 * 256) = 976.5625 Hz (~976.56 Hz)
;   - Output pin: PD5 / OC1A (Non-inverting: COM1A1=1, COM1A0=0)
;   - Pushbutton on PB2 (active LOW, internal pull-up)
;   - 4 selectable duty cycles:
;       Level 0: ~10% (OCR1A = 26)
;       Level 1: ~35% (OCR1A = 89)
;       Level 2: ~65% (OCR1A = 166)
;       Level 3: ~90% (OCR1A = 230)
;   - Each valid button press cycles: 10% -> 35% -> 65% -> 90% -> 10%
;====================================================================

.include "m32def.inc"

.def TEMP        = r16
.def MODE_IDX    = r20       ; Current setting index (0, 1, 2, 3)

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

    ; 2. Configure PD5 (OC1A) as output for hardware PWM
    sbi DDRD, PD5
    cbi PORTD, PD5

    ; 3. Configure PB2 as button input with internal pull-up enabled
    cbi DDRB, PB2
    sbi PORTB, PB2

    ; 4. Initialize duty cycle mode index to 0 (Level 0: 10%)
    clr MODE_IDX

    ; 5. Set initial compare value OCR1A = 26 (~10% duty)
    ;    AVR 16-bit register rule: write HIGH byte first, then LOW byte
    clr TEMP
    out OCR1AH, TEMP
    ldi TEMP, 26
    out OCR1AL, TEMP

    ; 6. Configure Timer1: 8-bit Fast PWM, non-inverting mode on OC1A
    ;    TCCR1A: COM1A1=1, COM1A0=0 (non-inverting OC1A), WGM10=1 (Mode 5)
    ldi TEMP, (1 << COM1A1) | (1 << WGM10)
    out TCCR1A, TEMP

    ; 7. Start Timer1: WGM12=1 (Mode 5 Fast PWM), Prescaler N=64 (CS11=1, CS10=1)
    ldi TEMP, (1 << WGM12) | (1 << CS11) | (1 << CS10)
    out TCCR1B, TEMP

;--------------------------------------------------------------------
; Main Polling Loop: Button Debounce & Duty Cycle Switching
;--------------------------------------------------------------------
MAIN_LOOP:
    ; Check if button PB2 is pressed (active LOW: 0)
    sbic PINB, PB2           ; Skip if PB2 is LOW (pressed)
    rjmp MAIN_LOOP           ; Otherwise continue waiting

    ; Button pressed: Debounce delay (~25 ms)
    rcall DELAY_25MS
    sbic PINB, PB2           ; Verify still pressed
    rjmp MAIN_LOOP

    ; Advance setting index: (MODE_IDX + 1) & 0x03
    inc  MODE_IDX
    cpi  MODE_IDX, 4
    brne APPLY_DUTY
    clr  MODE_IDX            ; Wrap around back to 0

APPLY_DUTY:
    ; Update OCR1A based on MODE_IDX
    cpi  MODE_IDX, 0
    breq SET_10_PERCENT
    cpi  MODE_IDX, 1
    breq SET_35_PERCENT
    cpi  MODE_IDX, 2
    breq SET_65_PERCENT

SET_90_PERCENT:
    ldi  TEMP, 230           ; ~90.2% (230/255)
    rjmp WRITE_OCR1A

SET_10_PERCENT:
    ldi  TEMP, 26            ; ~10.2% (26/255)
    rjmp WRITE_OCR1A

SET_35_PERCENT:
    ldi  TEMP, 89            ; ~34.9% (89/255)
    rjmp WRITE_OCR1A

SET_65_PERCENT:
    ldi  TEMP, 166           ; ~65.1% (166/255)

WRITE_OCR1A:
    ; Write HIGH byte first, then LOW byte
    clr  r17
    out  OCR1AH, r17
    out  OCR1AL, TEMP

WAIT_RELEASE:
    sbis PINB, PB2           ; Wait until button PB2 is released (HIGH)
    rjmp WAIT_RELEASE
    rcall DELAY_25MS         ; Debounce release
    rjmp MAIN_LOOP

;--------------------------------------------------------------------
; Delay Subroutine (~25 ms at 16 MHz) for pushbutton debounce
;--------------------------------------------------------------------
DELAY_25MS:
    ldi  r18, 255
D_OUTER:
    ldi  r19, 255
D_INNER:
    dec  r19
    brne D_INNER
    dec  r18
    brne D_OUTER
    ret
