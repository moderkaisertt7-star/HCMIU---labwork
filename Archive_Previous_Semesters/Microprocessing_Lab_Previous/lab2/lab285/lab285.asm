.INCLUDE "m32def.inc"

.CSEG
.ORG 0x0000
    RJMP RESET

RESET:
    LDI R16, HIGH(RAMEND)
    OUT SPH, R16
    LDI R16, LOW(RAMEND)
    OUT SPL, R16
    LDI R16, 0x7F
    OUT DDRD, R16
    CBI DDRC, 0                 
    SBI PORTC, 0                
    CLR R18                     
    CLR R20
    CLR R21                     
SHOW:
    LDI ZL, LOW(SEG_TABLE*2)
    LDI ZH, HIGH(SEG_TABLE*2)
    ADD ZL, R20
    ADC ZH, R18
    LPM R16, Z                  
    OUT PORTD, R16              
    CPI R21, 0
    BREQ SET_1000
    CPI R21, 1
    BREQ SET_500
    CPI R21, 2
    BREQ SET_250
    LDI R22, 5                  
    RJMP START_SLICED_DELAY
SET_250:
    LDI R22, 10                 
    RJMP START_SLICED_DELAY
SET_500:
    LDI R22, 20                 
    RJMP START_SLICED_DELAY
SET_1000:
    LDI R22, 40                 
START_SLICED_DELAY:
    LDI R24, LOW(25)
    LDI R25, HIGH(25)
    RCALL DELAY_MS  
    SBIS PINC, 0                
    RJMP DEBOUNCE               
    DEC R22
    BRNE START_SLICED_DELAY
    INC R20
    ANDI R20, 0x0F             
    RJMP SHOW
DEBOUNCE:
    LDI R24, LOW(20)
    LDI R25, HIGH(20)
    RCALL DELAY_MS
    SBIS PINC, 0                
    RJMP ACCEPT_KEY
    RJMP START_SLICED_DELAY     
ACCEPT_KEY:
    INC R21
    CPI R21, 4
    BRLO WAIT_RELEASE
    CLR R21
WAIT_RELEASE:
    SBIS PINC, 0
    RJMP WAIT_RELEASE
    RJMP START_SLICED_DELAY
SEG_TABLE:
    .DB 0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07  
    .DB 0x7F, 0x6F, 0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71  
.INCLUDE "delay_ms.inc"
