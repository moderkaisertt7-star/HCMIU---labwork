.INCLUDE "m32def.inc"
.CSEG
.ORG 0x0000
    RJMP RESET
RESET:
    LDI R16, HIGH(RAMEND)
    OUT SPH, R16
    LDI R16, LOW(RAMEND)
    OUT SPL, R16
    LDI R16, 0xFF
    OUT DDRD, R16
    CBI DDRC, 0                 ; PC0 = mode button
    SBI PORTC, 0                ; internal pull-up
    CLR R20                     ; mode 0, 1 or 2
    LDI R21, 0x01               ; one lit LED
MAIN:
    OUT PORTD, R21
    CPI R20, 0
    BREQ SLOW
    CPI R20, 1
    BREQ MEDIUM
FAST:
    LDI R24, LOW(250)
    LDI R25, HIGH(250)
    RJMP DO_WAIT
MEDIUM:
    LDI R24, LOW(500)
    LDI R25, HIGH(500)
    RJMP DO_WAIT
SLOW:
    LDI R24, LOW(1000)
    LDI R25, HIGH(1000)
DO_WAIT:
    RCALL DELAY_MS
    LSL R21
    BRNE CHECK_KEY
    LDI R21, 0x01
CHECK_KEY:
    SBIS PINC, 0                ; if released, skip jump
    RJMP DEBOUNCE
    RJMP MAIN
DEBOUNCE:
    LDI R24, LOW(20)
    LDI R25, HIGH(20)
    RCALL DELAY_MS
    SBIS PINC, 0
    RJMP PRESS_OK
    RJMP MAIN
PRESS_OK:
    INC R20
    CPI R20, 3
    BRLO WAIT_RELEASE
    CLR R20
WAIT_RELEASE:
    SBIS PINC, 0
    RJMP WAIT_RELEASE
    RJMP MAIN
.INCLUDE "delay_ms.inc"
