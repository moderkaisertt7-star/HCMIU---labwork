;==================================================
; File: delay_ms.inc
; Target: ATmega328P
; Clock frequency: 16 MHz
;
; Input: R25:R24 = delay duration in milliseconds
; Range: 1 to 65535 ms
;
; R24:R25 are preserved.
; R26:R27 and status flags are modified.
;==================================================

DELAY_MS:
    PUSH R24
    PUSH R25

DMS_LOOP:
    RCALL DELAY_1MS
    SBIW R24, 1
    BRNE DMS_LOOP

    POP R25
    POP R24
    RET

;--------------------------------------------------
; Approximately 1 ms at 16 MHz, including
; calling overhead in the outer delay routine
;--------------------------------------------------

DELAY_1MS:
    LDI R26, LOW(3997)
    LDI R27, HIGH(3997)

D1_LOOP:
    SBIW R26, 1
    BRNE D1_LOOP

    RET
