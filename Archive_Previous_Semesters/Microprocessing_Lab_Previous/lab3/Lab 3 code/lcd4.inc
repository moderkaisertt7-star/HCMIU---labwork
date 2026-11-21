;===============================================================
; lcd4.inc - HD44780 16x2 LCD driver, 4-bit mode, MPS 2026 kit
;   RS = PD0, RW = PD1, E = PD2, D4..D7 = PD4..PD7  (PD3 untouched)
;   needs delay.inc.  Registers used: r16, r17, r18, r24 (+ X saved)
;===============================================================
.equ    LCD_PORT = PORTD
.equ    LCD_DDR  = DDRD
.equ    LCD_PIN  = PIND
.equ    LCD_RS   = 0
.equ    LCD_RW   = 1
.equ    LCD_E    = 2

; lcd_nibble: put r16 bits 7..4 on D7..D4, RS = r18 bit 0, pulse E
lcd_nibble:
        andi  r16, 0xF0          ;data nibble, RS = RW = E = 0
        sbrc  r18, 0
        ori   r16, (1<<LCD_RS)   ;RS = 1 -> data register
        in    r17, LCD_PORT
        andi  r17, 0x08          ;keep PD3 as it was
        or    r16, r17
        out   LCD_PORT, r16      ;D7..D4 + RS, E = 0
        nop                      ;address set-up time > 140 ns
        sbi   LCD_PORT, LCD_E    ;E = 1
        rjmp  PC+1               ;each "rjmp PC+1" = 2-cycle nop
        rjmp  PC+1
        rjmp  PC+1               ;E high 6 + 2 = 8 cycles = 500 ns
        cbi   LCD_PORT, LCD_E    ;E = 0 -> LCD latches the nibble
        ret

; lcd_send: send byte r16 as two nibbles (high first), r18 = RS
lcd_send:
        push  r16
        rcall lcd_nibble         ;high nibble
        pop   r16
        swap  r16                ;low nibble -> bits 7..4
        rcall lcd_nibble         ;low nibble
        rcall delay_50us         ;execution time > 37 us
        ret

; lcd_cmd: send instruction r16 (waits 2 ms after clear / home)
lcd_cmd:
        push  r16
        clr   r18                ;RS = 0: instruction register
        rcall lcd_send
        pop   r16
        cpi   r16, 0x04          ;0x01 clear, 0x02/0x03 home?
        brsh  lcd_cmd_end
        ldi   r24, 2
        rcall delay_ms           ;they need 1.52 ms
lcd_cmd_end:
        ret

; lcd_data: write character r16 at the cursor
lcd_data:
        ldi   r18, 1             ;RS = 1: data register
        rjmp  lcd_send

; lcd_init: power-on initialisation for 4-bit mode
lcd_init:
        ldi   r16, 0xF7          ;PD7..PD4, PD2..PD0 = outputs
        out   LCD_DDR, r16
        cbi   LCD_PORT, LCD_E    ;E = 0
        ldi   r24, 50
        rcall delay_ms           ;1) wait > 40 ms after power-on
        clr   r18                ;RS = 0
        ldi   r16, 0x30
        rcall lcd_nibble         ;2) 0x3 : "8-bit mode" (1st)
        ldi   r24, 5
        rcall delay_ms           ;   wait > 4.1 ms
        ldi   r16, 0x30
        rcall lcd_nibble         ;   0x3 (2nd)
        ldi   r24, 1
        rcall delay_ms           ;   wait > 100 us
        ldi   r16, 0x30
        rcall lcd_nibble         ;   0x3 (3rd)
        rcall delay_50us
        ldi   r16, 0x20
        rcall lcd_nibble         ;3) 0x2 : switch to 4-bit mode
        rcall delay_50us
        ldi   r16, 0x28          ;4) 4-bit, 2 lines, 5x8 font
        rcall lcd_cmd
        ldi   r16, 0x0C          ;   display ON, cursor OFF, blink OFF
        rcall lcd_cmd
        ldi   r16, 0x06          ;   entry mode: increment, no shift
        rcall lcd_cmd
        ldi   r16, 0x01          ;   clear display, cursor home
        rcall lcd_cmd
        ret

; lcd_puts: print the zero-terminated string at Z (Flash byte address)
lcd_puts:
        lpm   r16, Z+            ;next character
        tst   r16                ;0 = end of string
        breq  lcd_puts_end
        rcall lcd_data
        rjmp  lcd_puts
lcd_puts_end:
        ret

; lcd_gotoxy: move the cursor to row r20 (0/1), column r21 (0..15)
lcd_gotoxy:
        mov   r16, r21           ;column
        andi  r16, 0x0F
        sbrc  r20, 0
        ori   r16, 0x40          ;row 1 starts at DDRAM 0x40
        ori   r16, 0x80          ;"set DDRAM address" command
        rjmp  lcd_cmd
