;===============================================================
; Lab 2 - Exercise 2: number entry with 5 buttons (calculator input)
;   SW4 digit+1   SW5 digit-1   SW6 ENTER (N = N*10 + digit)
;   SW7 DEL (N = N/10)          SW8 CLEAR (N = 0)
; Student: <name>        ID: <student ID>
; Kit: MPS 2026, ATmega32A @ 16 MHz
;===============================================================
.include "m32def.inc"
.dseg
.org    0x0060                   ;first SRAM address of the ATmega32
num:    .byte 2                  ;N, 16-bit (low byte first)
dig:    .byte 1                  ;digit being chosen, 0..9
dbuf:   .byte 5                  ;5 ASCII digits made by print_u16
.cseg
.org    0x0000
        rjmp  reset              ;reset vector
.org    INT_VECTORS_SIZE         ;program starts after the vector table
reset:  ldi   r16, high(RAMEND)  ;stack pointer -> top of SRAM
        out   sph, r16
        ldi   r16, low(RAMEND)
        out   spl, r16
        ldi   r16, 0x1F
        out   DDRA, r16          ;LEDs on PA0..PA4: the digit in binary
        out   PORTB, r16         ;pull-ups on SW4..SW8
        mov   r15, r16           ;previous button state = all released
        rcall lcd_init
        clr   r16
        sts   num, r16           ;N = 0
        sts   num+1, r16
        sts   dig, r16           ;digit = 0
        clr   r13                ;r13 = 1 -> show "TOO BIG"

main:   rcall show               ;draw N, digit, hex, LEDs
wait:   ldi   r24, 10
        rcall delay_ms           ;look at the buttons every 10 ms
        rcall keys               ;r14 = new presses (bit 0 = SW4)
        tst   r14
        breq  wait               ;nothing new -> keep waiting
        clr   r13                ;any key clears the message
        sbrc  r14, 0
        rcall dig_up             ;SW4
        sbrc  r14, 1
        rcall dig_dn             ;SW5
        sbrc  r14, 2
        rcall enter              ;SW6
        sbrc  r14, 3
        rcall del                ;SW7
        sbrc  r14, 4
        rcall clear              ;SW8
        rjmp  main

;---- keys: r14 = buttons pressed since the last call (falling edges) ----
keys:   in    r16, PINB
        andi  r16, 0x1F          ;now: 0 = pressed
        mov   r17, r16
        com   r16                ;pressed = 1
        and   r16, r15           ;... and released at the last look
        mov   r15, r17           ;remember the state for next time
        mov   r14, r16           ;drivers never change r14, r15
        ret

;---- button actions ----
dig_up: lds   r16, dig
        inc   r16
        cpi   r16, 10
        brlo  du_st
        clr   r16                ;9 + 1 -> 0
du_st:  sts   dig, r16
        ret
dig_dn: lds   r16, dig
        dec   r16
        brpl  dd_st              ;0 - 1 = $FF is negative
        ldi   r16, 9             ;-> 9
dd_st:  sts   dig, r16
        ret
enter:  lds   r22, num
        lds   r23, num+1
        lds   r16, dig
        rcall mul10_add          ;r23:r22 = N*10 + digit, C = 1 if > 65535
        brcs  en_big
        sts   num, r22
        sts   num+1, r23
        ret
en_big: inc   r13                ;keep the old N, show "TOO BIG"
        ret
del:    lds   r22, num
        lds   r23, num+1
        rcall div10              ;drop the last digit
        sts   num, r22
        sts   num+1, r23
        ret
clear:  clr   r16
        sts   num, r16
        sts   num+1, r16
        ret

;---------------------------------------------------------------
; mul10_add: r23:r22 = r23:r22 * 10 + r16    (N*10 = N*8 + N*2)
;   returns C = 1 if the result does not fit in 16 bits
;   uses r20, r21
;---------------------------------------------------------------
mul10_add:
        lsl   r22                ;N*2 : low byte, bit 7 -> C
        rol   r23                ;      high byte, C -> bit 0
        brcs  m10_end            ;bit 16 set -> too big
        mov   r20, r22           ;keep N*2 in r21:r20
        mov   r21, r23
        lsl   r22                ;N*4
        rol   r23
        brcs  m10_end
        lsl   r22                ;N*8
        rol   r23
        brcs  m10_end
        add   r22, r20           ;N*8 + N*2 = N*10
        adc   r23, r21
        brcs  m10_end
        clr   r20
        add   r22, r16           ;+ digit
        adc   r23, r20           ;carry into the high byte
m10_end:
        ret

;---------------------------------------------------------------
; div10: r23:r22 = r23:r22 / 10 by repeated subtraction (Lecture 4A)
;   uses X for the quotient
;---------------------------------------------------------------
div10:  clr   r26
        clr   r27                ;quotient = 0
d10_lp: subi  r22, 10            ;16-bit subtract 10 ...
        sbci  r23, 0             ;... with the borrow
        brcs  d10_end            ;went below 0 -> done
        adiw  r26, 1             ;one more ten
        rjmp  d10_lp
d10_end:
        movw  r22, r26           ;r23:r22 = quotient
        ret

;---------------------------------------------------------------
; print_u16: print r23:r22 (0..65535) in decimal, 5 characters,
;   leading zeros as blanks ("  123").  print_u16L: no blanks ("123").
;   Digits by repeated subtraction of 10000, 1000, 100, 10, 1
;   (table pow10 in Flash), stored in dbuf (SRAM) with ST Y+.
;   uses r16-r22, r23, Y, Z
;---------------------------------------------------------------
print_u16:
        set                      ;T = 1: print blanks
        rjmp  pu_go
print_u16L:
        clt                      ;T = 0: skip leading zeros
pu_go:  ldi   r30, low(pow10*2)
        ldi   r31, high(pow10*2)
        ldi   r28, low(dbuf)
        ldi   r29, high(dbuf)
pu_pow: lpm   r20, Z+            ;r21:r20 = next power of ten
        lpm   r21, Z+
        ldi   r16, '0'           ;digit counter, already in ASCII
pu_sub: sub   r22, r20           ;try to take one power away
        sbc   r23, r21
        brcs  pu_back            ;borrow -> it did not fit
        inc   r16
        rjmp  pu_sub
pu_back:
        add   r22, r20           ;undo the last subtraction
        adc   r23, r21
        st    Y+, r16            ;store the digit, Y -> next
        cpi   r20, 1             ;was it the last power (1)?
        brne  pu_pow
        ldi   r28, low(dbuf)     ;now print dbuf
        ldi   r29, high(dbuf)
        ldi   r19, 4             ;only the first 4 can be leading zeros
pu_lz:  ld    r16, Y
        cpi   r16, '0'
        brne  pu_out             ;first non-zero digit
        brtc  pu_skip
        ldi   r16, ' '
        rcall lcd_data           ;blank instead of the zero
pu_skip:
        adiw  r28, 1
        dec   r19
        brne  pu_lz
pu_out: ld    r16, Y+
        rcall lcd_data
        cpi   r28, low(dbuf+5)
        brne  pu_out
        ret
pow10:  .dw   10000, 1000, 100, 10, 1

;---- show: line 0 "N =  12345", line 1 "digit 7   $3039" ----
show:   ldi   r20, 0
        ldi   r21, 0
        rcall lcd_gotoxy
        ldi   r30, low(t_n*2)
        ldi   r31, high(t_n*2)
        rcall lcd_puts           ;"N = "
        lds   r22, num
        lds   r23, num+1
        rcall print_u16          ;5 characters
        ldi   r20, 1
        ldi   r21, 0
        rcall lcd_gotoxy
        ldi   r30, low(t_dig*2)
        ldi   r31, high(t_dig*2)
        rcall lcd_puts           ;"digit "
        lds   r16, dig
        out   PORTA, r16         ;digit on the LEDs
        subi  r16, -'0'
        rcall lcd_data
        tst   r13
        breq  sh_hex
        ldi   r30, low(t_big*2)
        ldi   r31, high(t_big*2)
        rjmp  lcd_puts           ;"  TOO BIG"
sh_hex: ldi   r30, low(t_hex*2)
        ldi   r31, high(t_hex*2)
        rcall lcd_puts           ;"   $"
        lds   r20, num+1
        rcall lcd_print_hex
        lds   r20, num
        rjmp  lcd_print_hex      ;its ret returns to main
t_n:    .db   "N = ", 0, 0
t_dig:  .db   "digit ", 0, 0
t_big:  .db   "  TOO BIG", 0
t_hex:  .db   "    $", 0
.include "lcd4.inc"
.include "lcdutil.inc"
.include "delay.inc"
