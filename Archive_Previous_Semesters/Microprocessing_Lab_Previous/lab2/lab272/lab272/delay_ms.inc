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
