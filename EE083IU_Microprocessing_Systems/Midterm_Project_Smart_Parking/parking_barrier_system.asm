; ==============================================================================
; PROJECT: AUTOMATED PARKING LOT & BARRIER MANAGEMENT SYSTEM
; TARGET MCU: PIC16F877A (4.0 MHz Crystal Oscillator)
; INTEGRATION: Topic 10 (Counter), Topic 7 (PWM Barrier), Topic 11 (UART Log)
; AUTHORS: Group PIC16F877A (Nguyen Le Minh Sang - Technical Lead)
; ENVIRONMENT: SimulIDE / Proteus Simulation
; TOOLCHAIN: MPASM / gpasm / Custom Python Mini-Assembler
; ==============================================================================

    LIST P=16F877A
    #INCLUDE <P16F877A.INC>

    ; Configuration: High Speed Crystal, Watchdog Off, Power-up Timer On, Low Voltage Prog Off
    __CONFIG _HS_OSC & _WDT_OFF & _PWRTE_ON & _BODEN_OFF & _LVP_OFF & _CPD_OFF & _WRT_OFF & _CP_OFF

; ------------------------------------------------------------------------------
; SYSTEM CONSTANTS
; ------------------------------------------------------------------------------
MAX_SLOTS       EQU .10         ; Maximum parking capacity
SERVO_OPEN      EQU 0x5E        ; CCPR1L = 94 -> 1.504ms duty cycle (~1.5ms, 90 deg open)
SERVO_CLOSE     EQU 0x3E        ; CCPR1L = 62 -> 0.992ms duty cycle (~1.0ms, 0 deg closed)
ASCII_OFFSET    EQU .48         ; '0' in ASCII (0x30)

; ------------------------------------------------------------------------------
; RAM VARIABLE ALLOCATION (Bank 0: 0x20 - 0x7F)
; ------------------------------------------------------------------------------
    CBLOCK 0x20
        CAR_COUNT               ; Current occupied slots (0 to 10)
        AVAILABLE_SLOTS         ; Remaining vacant slots (MAX_SLOTS - CAR_COUNT)
        EVENT_FLAGS             ; Bit 0: Entry Flag, Bit 1: Exit Flag, Bit 2: Full Flag
        TEMP_DATA               ; Scratchpad variable
        TEMP_CHAR               ; Character transmission buffer
        DELAY_VAR1              ; Nested delay loop counters (Inner 1)
        DELAY_VAR2              ; Nested delay loop counters (Inner 2)
        DELAY_VAR3              ; Nested delay loop counters (Mid 50ms / Debounce)
        DELAY_VAR4              ; Nested delay loop counters (Outer 500ms / 2sec)
        LCD_BUFFER              ; LCD data byte buffer
    ENDC

; Shared Unbanked RAM (0x70 - 0x7F) for ISR Context Saving
    CBLOCK 0x70
        W_TEMP                  ; Context: Working Register W
        STATUS_TEMP             ; Context: STATUS Register
        PCLATH_TEMP             ; Context: Program Counter Latch High
    ENDC

; Bit Definitions for EVENT_FLAGS
#DEFINE FLAG_ENTRY      EVENT_FLAGS, 0
#DEFINE FLAG_EXIT       EVENT_FLAGS, 1
#DEFINE FLAG_FULL       EVENT_FLAGS, 2

; Hardware Pin Mapping Definitions
#DEFINE BTN_CAR_EXIT    PORTB, 1    ; RB1: Car Exit Sensor (Active-High button)
#DEFINE LED_AVAILABLE   PORTB, 4    ; RB4: Green LED (Vacant slots available)
#DEFINE LED_FULL        PORTB, 5    ; RB5: Red LED (Parking Lot Full)
#DEFINE BUZZER_ALARM    PORTB, 6    ; RB6: Warning Buzzer
#DEFINE LCD_RS          PORTD, 2    ; RD2: LCD Register Select (0=Cmd, 1=Data)
#DEFINE LCD_EN          PORTD, 3    ; RD3: LCD Enable strobe pulse

; ==============================================================================
; RESET VECTOR: 0x0000
; ==============================================================================
    ORG     0x0000
    GOTO    MAIN_START

; ==============================================================================
; INTERRUPT VECTOR: 0x0004
; Handles RB0/INT External Interrupt for Car Entry Detection
; ==============================================================================
    ORG     0x0004
ISR_HANDLER:
    ; --- Context Saving using SWAPF (Preserves STATUS without altering Z flag) ---
    MOVWF   W_TEMP              ; Copy W to temporary storage in unbanked RAM
    SWAPF   STATUS, W           ; Invert nibbles of STATUS into W
    CLRF    STATUS              ; Force Bank 0
    MOVWF   STATUS_TEMP         ; Store swapped STATUS
    MOVF    PCLATH, W           ; Save PCLATH
    MOVWF   PCLATH_TEMP
    CLRF    PCLATH              ; Set PCLATH for page 0

    ; Verify if interrupt source is RB0/INT
    BTFSS   INTCON, INTF
    GOTO    ISR_EXIT            ; If not RB0/INT, skip to exit

    ; Temporarily lock INTE to prevent re-triggering during event handling
    BCF     INTCON, INTE

    ; Check if lot is already at maximum capacity
    MOVF    CAR_COUNT, W
    SUBLW   MAX_SLOTS
    BTFSC   STATUS, Z           ; If CAR_COUNT == MAX_SLOTS, Z=1
    GOTO    ISR_LOT_FULL        ; Reject vehicle entry

    ; Increment car count and flag entry event
    INCF    CAR_COUNT, F
    BSF     FLAG_ENTRY          ; Set entry flag for Main Loop processing
    GOTO    ISR_CLEAR_FLAG

ISR_LOT_FULL:
    BSF     FLAG_FULL           ; Trigger full alarm flag

ISR_CLEAR_FLAG:
    BCF     INTCON, INTF        ; Clear external interrupt flag

ISR_EXIT:
    ; --- Context Restoration ---
    MOVF    PCLATH_TEMP, W
    MOVWF   PCLATH              ; Restore PCLATH
    SWAPF   STATUS_TEMP, W      ; Retrieve original STATUS nibbles
    MOVWF   STATUS              ; Restore STATUS (and original RAM bank)
    SWAPF   W_TEMP, F           ; Swap W_TEMP in-place
    SWAPF   W_TEMP, W           ; Restore W without affecting STATUS flags
    RETFIE                      ; Return from Interrupt

; ==============================================================================
; MAIN INITIALIZATION & CONFIGURATION
; ==============================================================================
MAIN_START:
    CLRF    STATUS              ; Default Bank 0

    ; --- BANK 1: PORT TRISTATE & PERIPHERAL CONFIGURATION ---
    BSF     STATUS, RP0         ; Select Bank 1
    BCF     STATUS, RP1

    ; Configure I/O Directions
    ; PORTB: RB0 (Input INT), RB1 (Input Exit), RB4-RB6 (Outputs: LEDs, Buzzer)
    MOVLW   B'00000011'
    MOVWF   TRISB

    ; PORTC: RC2 (Output CCP1 PWM), RC6 (Output TX), RC7 (Input RX)
    MOVLW   B'10000000'
    MOVWF   TRISC

    ; PORTD: RD2-RD3 (LCD Control), RD4-RD7 (LCD Data Nibble 4-bit)
    MOVLW   B'00000000'
    MOVWF   TRISD

    ; Configure RB0/INT Trigger: Interrupt on Rising Edge
    MOVLW   B'11000000'         ; Pull-ups disabled, INTEDG=1 (Rising Edge)
    MOVWF   OPTION_REG

    ; Configure Timer2 Period for PWM (50 Hz / 20ms for servo control or 1kHz)
    ; Fosc = 4MHz, Tosc = 0.25us. Prescaler 1:16 -> Tcy = 4us. PR2 = 155
    MOVLW   .155
    MOVWF   PR2

    ; Configure USART Baud Rate Generator: 9600 bps at 4MHz
    ; High Speed Mode (BRGH=1): SPBRG = (4000000 / (16 * 9600)) - 1 = 25
    MOVLW   .25
    MOVWF   SPBRG
    MOVLW   B'00100100'         ; TXEN=1, BRGH=1 (High Baud), 8-bit TX
    MOVWF   TXSTA

    ; --- BANK 0: RUNTIME OPERATION ---
    BCF     STATUS, RP0         ; Return to Bank 0

    ; Enable USART Serial Port
    MOVLW   B'10010000'         ; SPEN=1, CREN=1 (Enable Serial Port & RX)
    MOVWF   RCSTA

    ; Configure CCP1 Module for PWM Mode
    MOVLW   B'00001100'         ; CCP1M3:CCP1M0 = 1100 (PWM Mode)
    MOVWF   CCP1CON

    ; Start Timer2 with Prescaler 1:16
    MOVLW   B'00000111'         ; TMR2ON=1, Prescaler 1:16
    MOVWF   T2CON

    ; Initial Barrier Position: 0 degrees (CLOSED)
    MOVLW   SERVO_CLOSE
    MOVWF   CCPR1L

    ; Initialize Variables
    CLRF    CAR_COUNT
    CLRF    EVENT_FLAGS

    ; STEP 1: Initialize LCD 16x2 Display (4-Bit Mode)
    CALL    LCD_INIT

    ; STEP 2: Initialize Hardware Outputs & Slot State (Slot Count = 10, Green LED ON)
    CALL    UPDATE_SYSTEM_STATE

    ; STEP 3: Display Initial Header and Status on LCD
    CALL    LCD_DISPLAY_INITIAL

    ; STEP 4: Send Initial Boot Telemetry via UART
    CALL    UART_SEND_BOOT_MSG

    ; Enable Global and External Interrupts
    BCF     INTCON, INTF        ; Clear any pending flag
    BSF     INTCON, INTE        ; Enable RB0/INT External Interrupt
    BSF     INTCON, GIE         ; Enable Global Interrupts

; ==============================================================================
; MAIN OPERATIONAL LOOP
; Polls exit sensor, processes event flags, handles barrier & display
; ==============================================================================
MAIN_LOOP:
    ; --- Check Event 1: Vehicle Entry Flag (Triggered by ISR) ---
    BTFSS   FLAG_ENTRY
    GOTO    CHECK_EXIT_FLAG

    ; Handle Entry Event:
    BCF     FLAG_ENTRY          ; Clear flag
    CALL    UPDATE_SYSTEM_STATE ; Recalculate slots, update LEDs & LCD IMMEDIATELY
    CALL    UART_LOG_ENTRY      ; Transmit entry telemetry log
    CALL    BARRIER_OPERATE     ; Open barrier, hold 2s, close barrier
    CALL    RESET_RB_INPUTS     ; Active discharge floating lines & re-enable INTE
    GOTO    MAIN_LOOP

CHECK_EXIT_FLAG:
    ; --- Check Event 2: Vehicle Exit Sensor (Polled on RB1, Active-High) ---
    BTFSS   BTN_CAR_EXIT        ; RB1: 0 = not pressed, 1 = pressed
    GOTO    CHECK_FULL_FLAG     ; Not pressed, check next

    ; Exit Button Pressed: Debounce check
    CALL    DELAY_DEBOUNCE
    BTFSS   BTN_CAR_EXIT
    GOTO    CHECK_FULL_FLAG     ; Spurious noise pulse

    ; Exit button detected (Do NOT use WAIT_EXIT_RELEASE loop to avoid hang on floating pin)
    MOVF    CAR_COUNT, F
    BTFSC   STATUS, Z           ; If CAR_COUNT == 0, cannot decrement
    GOTO    EXIT_EMPTY_DISCHARGE

    DECF    CAR_COUNT, F        ; One vehicle departed
    CALL    UPDATE_SYSTEM_STATE ; Update LCD and LED indicators IMMEDIATELY
    CALL    UART_LOG_EXIT       ; Transmit departure telemetry log
    CALL    BARRIER_OPERATE     ; Open barrier for departing car, hold 2s, close
    CALL    RESET_RB_INPUTS     ; Active discharge floating lines & re-enable INTE
    GOTO    MAIN_LOOP

EXIT_EMPTY_DISCHARGE:
    CALL    RESET_RB_INPUTS     ; Discharge pin even when empty
    GOTO    MAIN_LOOP

CHECK_FULL_FLAG:
    ; --- Check Event 3: Full Warning Alarm ---
    BTFSS   FLAG_FULL
    GOTO    MAIN_LOOP

    BCF     FLAG_FULL           ; Clear full alarm flag
    CALL    TRIGGER_FULL_ALARM  ; Sound buzzer and transmit alert
    CALL    RESET_RB_INPUTS     ; Active discharge floating lines & re-enable INTE
    GOTO    MAIN_LOOP

; ==============================================================================
; RESET RB INPUTS ROUTINE (ACTIVE DISCHARGE FOR SIMULIDE FLOATING LINES)
; Clears residual 5V voltage on RB0/RB1 simulation wires, debounces & re-enables INTE
; ==============================================================================
RESET_RB_INPUTS:
    ; 1. Latch PORTB bits 0 & 1 to low level (0V)
    BCF     PORTB, 0
    BCF     PORTB, 1

    ; 2. Switch TRISB to output temporarily to discharge floating lines to 0V
    BSF     STATUS, RP0         ; Bank 1
    BCF     STATUS, RP1
    MOVLW   B'00000000'         ; RB0, RB1 as Output (0V discharge)
    MOVWF   TRISB
    BCF     STATUS, RP0         ; Bank 0
    NOP                         ; 2 instruction cycles active discharge
    NOP

    ; 3. Restore TRISB so RB0, RB1 are inputs again
    BSF     STATUS, RP0         ; Bank 1
    MOVLW   B'00000011'         ; RB0, RB1 back to Inputs
    MOVWF   TRISB
    BCF     STATUS, RP0         ; Bank 0

    ; 4. Debounce delay (20ms) and re-enable external interrupt
    CALL    DELAY_DEBOUNCE
    BCF     INTCON, INTF        ; Clear any spurious edge flag
    BSF     INTCON, INTE        ; Re-enable RB0/INT external interrupt
    RETURN

; ==============================================================================
; SYSTEM STATE UPDATE ROUTINE
; Updates Remaining Slots, LEDs, Buzzer, and LCD Screen
; ==============================================================================
UPDATE_SYSTEM_STATE:
    ; Calculate Available Slots = MAX_SLOTS - CAR_COUNT
    MOVF    CAR_COUNT, W
    SUBLW   MAX_SLOTS
    MOVWF   AVAILABLE_SLOTS

    ; Check if Lot is Full
    MOVF    AVAILABLE_SLOTS, F
    BTFSS   STATUS, Z
    GOTO    STATE_AVAILABLE

    ; --- STATE: FULL ---
    BCF     LED_AVAILABLE       ; Green LED OFF
    BSF     LED_FULL            ; Red LED ON
    CALL    LCD_DISPLAY_FULL
    RETURN

STATE_AVAILABLE:
    ; --- STATE: SPACES AVAILABLE ---
    BSF     LED_AVAILABLE       ; Green LED ON
    BCF     LED_FULL            ; Red LED OFF
    BCF     BUZZER_ALARM        ; Buzzer OFF
    CALL    LCD_DISPLAY_STATUS
    RETURN

; ==============================================================================
; BARRIER MOTOR / PWM CONTROL ROUTINE
; Opens barrier (90 deg), holds for 2 seconds, then closes barrier (0 deg)
; ==============================================================================
BARRIER_OPERATE:
    ; Set PWM Duty Cycle to OPEN (90 degrees)
    MOVLW   SERVO_OPEN
    MOVWF   CCPR1L

    ; Hold barrier open for vehicle passage (2.0 seconds)
    CALL    DELAY_2SEC

    ; Set PWM Duty Cycle to CLOSE (0 degrees)
    MOVLW   SERVO_CLOSE
    MOVWF   CCPR1L
    RETURN

; ==============================================================================
; FULL ALARM TRIGGER
; Sounds warning buzzer for 500ms when an entry is attempted while full
; ==============================================================================
TRIGGER_FULL_ALARM:
    BSF     BUZZER_ALARM
    CALL    DELAY_500MS
    BCF     BUZZER_ALARM
    CALL    UART_LOG_REJECT
    RETURN

; ==============================================================================
; USART TELEMETRY LOGGING ROUTINES (9600-8N1)
; ==============================================================================
UART_SEND_BYTE:
    ; Wait until Transmit Buffer is empty (TRMT=1 in TXSTA Bank 1)
    BSF     STATUS, RP0         ; Bank 1
WAIT_TX:
    BTFSS   TXSTA, TRMT
    GOTO    WAIT_TX
    BCF     STATUS, RP0         ; Bank 0
    MOVWF   TXREG               ; Write byte to transmit register
    RETURN

UART_SEND_STRING:
    ; W contains table offset or call per character
    RETURN

UART_SEND_BOOT_MSG:
    MOVLW   0x0D
    CALL    UART_SEND_BYTE
    MOVLW   0x0A
    CALL    UART_SEND_BYTE
    MOVLW   '['
    CALL    UART_SEND_BYTE
    MOVLW   'S'
    CALL    UART_SEND_BYTE
    MOVLW   'Y'
    CALL    UART_SEND_BYTE
    MOVLW   'S'
    CALL    UART_SEND_BYTE
    MOVLW   ']'
    CALL    UART_SEND_BYTE
    MOVLW   ' '
    CALL    UART_SEND_BYTE
    MOVLW   'P'
    CALL    UART_SEND_BYTE
    MOVLW   'A'
    CALL    UART_SEND_BYTE
    MOVLW   'R'
    CALL    UART_SEND_BYTE
    MOVLW   'K'
    CALL    UART_SEND_BYTE
    MOVLW   'I'
    CALL    UART_SEND_BYTE
    MOVLW   'N'
    CALL    UART_SEND_BYTE
    MOVLW   'G'
    CALL    UART_SEND_BYTE
    MOVLW   ' '
    CALL    UART_SEND_BYTE
    MOVLW   'R'
    CALL    UART_SEND_BYTE
    MOVLW   'E'
    CALL    UART_SEND_BYTE
    MOVLW   'A'
    CALL    UART_SEND_BYTE
    MOVLW   'D'
    CALL    UART_SEND_BYTE
    MOVLW   'Y'
    CALL    UART_SEND_BYTE
    MOVLW   0x0D
    CALL    UART_SEND_BYTE
    MOVLW   0x0A
    CALL    UART_SEND_BYTE
    RETURN

UART_LOG_ENTRY:
    MOVLW   '['
    CALL    UART_SEND_BYTE
    MOVLW   '+'
    CALL    UART_SEND_BYTE
    MOVLW   ']'
    CALL    UART_SEND_BYTE
    MOVLW   ' '
    CALL    UART_SEND_BYTE
    MOVLW   'E'
    CALL    UART_SEND_BYTE
    MOVLW   'N'
    CALL    UART_SEND_BYTE
    MOVLW   'T'
    CALL    UART_SEND_BYTE
    MOVLW   'R'
    CALL    UART_SEND_BYTE
    MOVLW   'Y'
    CALL    UART_SEND_BYTE
    MOVLW   ' '
    CALL    UART_SEND_BYTE
    MOVLW   'C'
    CALL    UART_SEND_BYTE
    MOVLW   'A'
    CALL    UART_SEND_BYTE
    MOVLW   'R'
    CALL    UART_SEND_BYTE
    MOVLW   'S'
    CALL    UART_SEND_BYTE
    MOVLW   ':'
    CALL    UART_SEND_BYTE

    ; Check if CAR_COUNT == 10
    MOVF    CAR_COUNT, W
    SUBLW   .10
    BTFSS   STATUS, Z
    GOTO    UART_ENTRY_SINGLE_DIGIT

    ; CAR_COUNT == 10
    MOVLW   '1'
    CALL    UART_SEND_BYTE
    MOVLW   '0'
    CALL    UART_SEND_BYTE
    GOTO    UART_ENTRY_TAIL

UART_ENTRY_SINGLE_DIGIT:
    MOVF    CAR_COUNT, W
    ADDLW   ASCII_OFFSET
    CALL    UART_SEND_BYTE

UART_ENTRY_TAIL:
    MOVLW   '/'
    CALL    UART_SEND_BYTE
    MOVLW   '1'
    CALL    UART_SEND_BYTE
    MOVLW   '0'
    CALL    UART_SEND_BYTE
    MOVLW   0x0D
    CALL    UART_SEND_BYTE
    MOVLW   0x0A
    CALL    UART_SEND_BYTE
    RETURN

UART_LOG_EXIT:
    MOVLW   '['
    CALL    UART_SEND_BYTE
    MOVLW   '-'
    CALL    UART_SEND_BYTE
    MOVLW   ']'
    CALL    UART_SEND_BYTE
    MOVLW   ' '
    CALL    UART_SEND_BYTE
    MOVLW   'E'
    CALL    UART_SEND_BYTE
    MOVLW   'X'
    CALL    UART_SEND_BYTE
    MOVLW   'I'
    CALL    UART_SEND_BYTE
    MOVLW   'T'
    CALL    UART_SEND_BYTE
    MOVLW   ' '
    CALL    UART_SEND_BYTE
    MOVLW   'C'
    CALL    UART_SEND_BYTE
    MOVLW   'A'
    CALL    UART_SEND_BYTE
    MOVLW   'R'
    CALL    UART_SEND_BYTE
    MOVLW   'S'
    CALL    UART_SEND_BYTE
    MOVLW   ':'
    CALL    UART_SEND_BYTE

    ; Check if CAR_COUNT == 10
    MOVF    CAR_COUNT, W
    SUBLW   .10
    BTFSS   STATUS, Z
    GOTO    UART_EXIT_SINGLE_DIGIT

    ; CAR_COUNT == 10
    MOVLW   '1'
    CALL    UART_SEND_BYTE
    MOVLW   '0'
    CALL    UART_SEND_BYTE
    GOTO    UART_EXIT_TAIL

UART_EXIT_SINGLE_DIGIT:
    MOVF    CAR_COUNT, W
    ADDLW   ASCII_OFFSET
    CALL    UART_SEND_BYTE

UART_EXIT_TAIL:
    MOVLW   '/'
    CALL    UART_SEND_BYTE
    MOVLW   '1'
    CALL    UART_SEND_BYTE
    MOVLW   '0'
    CALL    UART_SEND_BYTE
    MOVLW   0x0D
    CALL    UART_SEND_BYTE
    MOVLW   0x0A
    CALL    UART_SEND_BYTE
    RETURN

UART_LOG_REJECT:
    MOVLW   '['
    CALL    UART_SEND_BYTE
    MOVLW   '!'
    CALL    UART_SEND_BYTE
    MOVLW   ']'
    CALL    UART_SEND_BYTE
    MOVLW   ' '
    CALL    UART_SEND_BYTE
    MOVLW   'F'
    CALL    UART_SEND_BYTE
    MOVLW   'U'
    CALL    UART_SEND_BYTE
    MOVLW   'L'
    CALL    UART_SEND_BYTE
    MOVLW   'L'
    CALL    UART_SEND_BYTE
    MOVLW   '!'
    CALL    UART_SEND_BYTE
    MOVLW   ' '
    CALL    UART_SEND_BYTE
    MOVLW   'E'
    CALL    UART_SEND_BYTE
    MOVLW   'N'
    CALL    UART_SEND_BYTE
    MOVLW   'T'
    CALL    UART_SEND_BYTE
    MOVLW   'R'
    CALL    UART_SEND_BYTE
    MOVLW   'Y'
    CALL    UART_SEND_BYTE
    MOVLW   ' '
    CALL    UART_SEND_BYTE
    MOVLW   'D'
    CALL    UART_SEND_BYTE
    MOVLW   'E'
    CALL    UART_SEND_BYTE
    MOVLW   'N'
    CALL    UART_SEND_BYTE
    MOVLW   'I'
    CALL    UART_SEND_BYTE
    MOVLW   'E'
    CALL    UART_SEND_BYTE
    MOVLW   'D'
    CALL    UART_SEND_BYTE
    MOVLW   0x0D
    CALL    UART_SEND_BYTE
    MOVLW   0x0A
    CALL    UART_SEND_BYTE
    RETURN

; ==============================================================================
; LCD 16x2 DRIVER (4-BIT MODE VIA PORTD: RD4-RD7, RD2=RS, RD3=EN)
; ==============================================================================
LCD_INIT:
    BCF     LCD_RS
    BCF     LCD_EN
    CALL    DELAY_50MS          ; Wait > 15ms after power-on

    ; Step 1: Function Set Sequence in 4-bit mode
    MOVLW   0x03
    CALL    LCD_SEND_NIBBLE
    CALL    DELAY_5MS
    MOVLW   0x03
    CALL    LCD_SEND_NIBBLE
    CALL    DELAY_5MS
    MOVLW   0x03
    CALL    LCD_SEND_NIBBLE
    CALL    DELAY_5MS
    MOVLW   0x02                ; Switch to 4-bit interface
    CALL    LCD_SEND_NIBBLE
    CALL    DELAY_5MS

    ; Step 2: Configure 2-line display, 5x8 font
    MOVLW   0x28
    CALL    LCD_CMD

    ; Step 3: Display ON, Cursor OFF
    MOVLW   0x0C
    CALL    LCD_CMD

    ; Step 4: Clear Display
    MOVLW   0x01
    CALL    LCD_CMD
    CALL    DELAY_5MS

    ; Step 5: Entry Mode Set: Increment cursor
    MOVLW   0x06
    CALL    LCD_CMD
    RETURN

LCD_CMD:
    BCF     LCD_RS              ; RS = 0 (Command)
    MOVWF   LCD_BUFFER
    ; Send high nibble
    SWAPF   LCD_BUFFER, W
    CALL    LCD_SEND_NIBBLE
    ; Send low nibble
    MOVF    LCD_BUFFER, W
    CALL    LCD_SEND_NIBBLE
    CALL    DELAY_SHORT
    RETURN

LCD_CHAR:
    BSF     LCD_RS              ; RS = 1 (Data)
    MOVWF   LCD_BUFFER
    ; Send high nibble
    SWAPF   LCD_BUFFER, W
    CALL    LCD_SEND_NIBBLE
    ; Send low nibble
    MOVF    LCD_BUFFER, W
    CALL    LCD_SEND_NIBBLE
    CALL    DELAY_SHORT
    RETURN

LCD_SEND_NIBBLE:
    ANDLW   0x0F
    MOVWF   TEMP_DATA
    MOVF    PORTD, W
    ANDLW   0x0F                ; Preserve lower control pins (RD0-RD3)
    IORWF   TEMP_DATA, W        ; Merge nibble into RD4-RD7 (if shifted)
    SWAPF   TEMP_DATA, W
    ANDLW   0xF0
    MOVWF   TEMP_DATA
    MOVF    PORTD, W
    ANDLW   0x0F
    IORWF   TEMP_DATA, W
    MOVWF   PORTD

    ; Pulse Enable Pin
    BSF     LCD_EN
    NOP
    NOP
    BCF     LCD_EN
    RETURN

LCD_DISPLAY_INITIAL:
    MOVLW   0x80                ; Line 1, Position 0
    CALL    LCD_CMD
    ; Print "PARKING SYSTEM"
    MOVLW   'P'
    CALL    LCD_CHAR
    MOVLW   'A'
    CALL    LCD_CHAR
    MOVLW   'R'
    CALL    LCD_CHAR
    MOVLW   'K'
    CALL    LCD_CHAR
    MOVLW   'I'
    CALL    LCD_CHAR
    MOVLW   'N'
    CALL    LCD_CHAR
    MOVLW   'G'
    CALL    LCD_CHAR
    MOVLW   ' '
    CALL    LCD_CHAR
    MOVLW   'S'
    CALL    LCD_CHAR
    MOVLW   'Y'
    CALL    LCD_CHAR
    MOVLW   'S'
    CALL    LCD_CHAR
    MOVLW   'T'
    CALL    LCD_CHAR
    MOVLW   'E'
    CALL    LCD_CHAR
    MOVLW   'M'
    CALL    LCD_CHAR

    ; Line 2: Status
    CALL    LCD_DISPLAY_STATUS
    RETURN

LCD_DISPLAY_STATUS:
    MOVLW   0xC0                ; Line 2, Position 0
    CALL    LCD_CMD
    MOVLW   'S'
    CALL    LCD_CHAR
    MOVLW   'L'
    CALL    LCD_CHAR
    MOVLW   'O'
    CALL    LCD_CHAR
    MOVLW   'T'
    CALL    LCD_CHAR
    MOVLW   'S'
    CALL    LCD_CHAR
    MOVLW   ':'
    CALL    LCD_CHAR
    MOVLW   ' '
    CALL    LCD_CHAR

    ; Check if Available Slots == 10
    MOVF    AVAILABLE_SLOTS, W
    SUBLW   .10
    BTFSS   STATUS, Z
    GOTO    LCD_STATUS_SINGLE_DIGIT

    ; Available Slots == 10: Print "10/10  "
    MOVLW   '1'
    CALL    LCD_CHAR
    MOVLW   '0'
    CALL    LCD_CHAR
    GOTO    LCD_STATUS_TAIL

LCD_STATUS_SINGLE_DIGIT:
    MOVF    AVAILABLE_SLOTS, W
    ADDLW   ASCII_OFFSET
    CALL    LCD_CHAR
    MOVLW   ' '
    CALL    LCD_CHAR

LCD_STATUS_TAIL:
    MOVLW   '/'
    CALL    LCD_CHAR
    MOVLW   '1'
    CALL    LCD_CHAR
    MOVLW   '0'
    CALL    LCD_CHAR
    MOVLW   ' '
    CALL    LCD_CHAR
    MOVLW   ' '
    CALL    LCD_CHAR
    RETURN

LCD_DISPLAY_FULL:
    MOVLW   0xC0                ; Line 2, Position 0
    CALL    LCD_CMD
    MOVLW   '*'
    CALL    LCD_CHAR
    MOVLW   '*'
    CALL    LCD_CHAR
    MOVLW   ' '
    CALL    LCD_CHAR
    MOVLW   'L'
    CALL    LCD_CHAR
    MOVLW   'O'
    CALL    LCD_CHAR
    MOVLW   'T'
    CALL    LCD_CHAR
    MOVLW   ' '
    CALL    LCD_CHAR
    MOVLW   'F'
    CALL    LCD_CHAR
    MOVLW   'U'
    CALL    LCD_CHAR
    MOVLW   'L'
    CALL    LCD_CHAR
    MOVLW   'L'
    CALL    LCD_CHAR
    MOVLW   '!'
    CALL    LCD_CHAR
    MOVLW   ' '
    CALL    LCD_CHAR
    MOVLW   '*'
    CALL    LCD_CHAR
    MOVLW   '*'
    CALL    LCD_CHAR
    RETURN

; ==============================================================================
; DELAY SUBROUTINES (CALCULATED FOR 4.0 MHz OSCILLATOR, Tcy = 1.0 us)
; ==============================================================================
DELAY_SHORT:                    ; ~100 us delay
    MOVLW   .33
    MOVWF   DELAY_VAR1
D_SHORT_LOOP:
    DECFSZ  DELAY_VAR1, F
    GOTO    D_SHORT_LOOP
    RETURN

DELAY_5MS:                      ; ~5.0 ms delay
    MOVLW   .5
    MOVWF   DELAY_VAR2
D_5MS_OUTER:
    MOVLW   .250
    MOVWF   DELAY_VAR1
D_5MS_INNER:
    NOP
    DECFSZ  DELAY_VAR1, F
    GOTO    D_5MS_INNER
    DECFSZ  DELAY_VAR2, F
    GOTO    D_5MS_OUTER
    RETURN

DELAY_50MS:                     ; ~50 ms delay
    MOVLW   .10
    MOVWF   DELAY_VAR3
D_50MS_LOOP:
    CALL    DELAY_5MS
    DECFSZ  DELAY_VAR3, F
    GOTO    D_50MS_LOOP
    RETURN

DELAY_DEBOUNCE:                 ; ~20 ms switch debounce delay
    MOVLW   .4
    MOVWF   DELAY_VAR3
D_DEBOUNCE_LOOP:
    CALL    DELAY_5MS
    DECFSZ  DELAY_VAR3, F
    GOTO    D_DEBOUNCE_LOOP
    RETURN

DELAY_500MS:                    ; ~500 ms buzzer delay
    MOVLW   .10
    MOVWF   DELAY_VAR4          ; Dedicated outer loop counter
D_500MS_LOOP:
    CALL    DELAY_50MS          ; Uses DELAY_VAR3
    DECFSZ  DELAY_VAR4, F
    GOTO    D_500MS_LOOP
    RETURN

DELAY_2SEC:                     ; ~2.0 seconds barrier open hold delay
    MOVLW   .40
    MOVWF   DELAY_VAR4          ; Dedicated outer loop counter
D_2SEC_LOOP:
    CALL    DELAY_50MS          ; Uses DELAY_VAR3
    DECFSZ  DELAY_VAR4, F
    GOTO    D_2SEC_LOOP
    RETURN

    END
