;====================================================================
; Exercise 13: Timer0 CTC 4-Bit Counter with 250 ms Tick (Interrupt-Driven)
; Target MCU: ATmega32A
; Clock Frequency: 16.0 MHz External Crystal
; Description:
;   - Timer0 configured in CTC mode (WGM01=1, WGM00=0)
;   - Prescaler N = 64 (CS01=1, CS00=1)
;   - OCR0 = 249 => Interval = (249 + 1) * 64 / 16,000,000 = 1.0 ms
;   - Timer0 Compare-Match Interrupt (TIMER0 COMP) fires every 1 ms
;   - ISR counts 250 ticks (250 ms) and increments a 4-bit counter (0..15)
;   - Displayed on PA0..PA3 (4 indicator LEDs). One full cycle = 16 * 250 ms = 4.0 s
;====================================================================

.include "m32def.inc"

; Register definitions
.def TEMP        = r16
.def SREG_SAVE   = r17
.def COUNT_4BIT  = r20       ; 4-bit display value (0..15)
.def MS_L        = r24       ; 16-bit millisecond counter (low byte)
.def MS_H        = r25       ; 16-bit millisecond counter (high byte)

; Vector table
.org 0x0000
    rjmp RESET               ; Reset handler
.org OC0addr                 ; Timer0 Compare Match Interrupt Vector (0x0014)
    rjmp TIMER0_COMP_ISR
.org 0x002A                  ; End of vector table

;--------------------------------------------------------------------
; Reset Handler & Hardware Initialization
;--------------------------------------------------------------------
RESET:
    ; 1. Initialize Stack Pointer to RAMEND
    ldi TEMP, high(RAMEND)
    out SPH, TEMP
    ldi TEMP, low(RAMEND)
    out SPL, TEMP

    ; 2. Configure PORTA (PA0..PA3 as Outputs for 4-bit LED display)
    in  TEMP, DDRA
    ori TEMP, 0x0F           ; PA0..PA3 output (1), PA4..PA7 unchanged
    out DDRA, TEMP
    in  TEMP, PORTA
    andi TEMP, 0xF0          ; Turn off LEDs initially (active HIGH)
    out PORTA, TEMP

    ; 3. Initialize registers
    clr COUNT_4BIT           ; Start count at 0
    clr MS_L                 ; Reset ms counter
    clr MS_H

    ; 4. Configure Timer0 in CTC Mode (WGM01=1, WGM00=0)
    ;    Stop timer initially
    clr TEMP
    out TCCR0, TEMP
    out TCNT0, TEMP          ; Clear counter register

    ; 5. Set Compare Register OCR0 for 1 ms tick
    ;    OCR0 = (16,000,000 * 0.001 / 64) - 1 = 249
    ldi TEMP, 249
    out OCR0, TEMP

    ; 6. Clear pending compare-match flag (W1C)
    ldi TEMP, (1 << OCF0)
    out TIFR, TEMP

    ; 7. Enable Timer0 Output Compare Match Interrupt
    in  TEMP, TIMSK
    ori TEMP, (1 << OCIE0)
    out TIMSK, TEMP

    ; 8. Enable Global Interrupts
    sei

    ; 9. Start Timer0: CTC Mode with Prescaler = 64 (CS01=1, CS00=1)
    ldi TEMP, (1 << WGM01) | (1 << CS01) | (1 << CS00)
    out TCCR0, TEMP

;--------------------------------------------------------------------
; Main Loop (Idle - All timing and display updates handled in ISR)
;--------------------------------------------------------------------
MAIN_LOOP:
    rjmp MAIN_LOOP

;--------------------------------------------------------------------
; Timer0 Compare Match ISR (Fires every 1.0 ms)
;--------------------------------------------------------------------
TIMER0_COMP_ISR:
    in  SREG_SAVE, SREG      ; Preserve status register

    ; Increment 16-bit ms counter (MS_H:MS_L)
    adiw MS_L, 1

    ; Check if 250 ms elapsed (compare MS_H:MS_L with 250)
    cpi  MS_L, low(250)
    ldi  TEMP, high(250)
    cpc  MS_H, TEMP
    brne ISR_EXIT            ; If not 250 ms yet, return

    ; 250 ms reached: reset ms counter
    clr  MS_L
    clr  MS_H

    ; Increment 4-bit counter and mask to 0..15 (4 bits)
    inc  COUNT_4BIT
    andi COUNT_4BIT, 0x0F

    ; Output COUNT_4BIT to PA0..PA3 preserving PA4..PA7
    in   TEMP, PORTA
    andi TEMP, 0xF0          ; Clear lower nibble
    or   TEMP, COUNT_4BIT    ; Insert new 4-bit count
    out  PORTA, TEMP

ISR_EXIT:
    out SREG, SREG_SAVE      ; Restore status register
    reti
