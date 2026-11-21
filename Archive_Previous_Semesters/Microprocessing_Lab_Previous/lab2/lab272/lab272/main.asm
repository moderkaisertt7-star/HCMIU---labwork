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
    OUT DDRD, R16               ; eight LED outputs
AGAIN:
    LDI R21, 0x01               ; one-hot shift LEFT
LEFT_RUN:
    OUT PORTD, R21
    RCALL WAIT_250
    LSL R21
    BRNE LEFT_RUN

    LDI R21, 0x80               ; one-hot shift RIGHT
RIGHT_RUN:
    OUT PORTD, R21
    RCALL WAIT_250
    LSR R21
    BRNE RIGHT_RUN

    CLR R21                     ; progressively switch ON
    LDI R22, 0x01
GROW:
    OR R21, R22
    OUT PORTD, R21
    RCALL WAIT_250
    LSL R22
    BRNE GROW

    LDI R21, 0xFF               ; progressively switch OFF
    LDI R22, 0x01
SHRINK:
    MOV R18, R22
    COM R18
    AND R21, R18
    OUT PORTD, R21
    RCALL WAIT_250
    LSL R22
    BRNE SHRINK
    RJMP AGAIN

WAIT_250:
    LDI R24, LOW(250)
    LDI R25, HIGH(250)
    RCALL DELAY_MS
    RET
.INCLUDE "delay_ms.inc"
