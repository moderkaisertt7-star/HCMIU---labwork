;===============================================================
; Lab 2 - Exercise 4: 16-bit calculator engine + self-test
;   add16, sub16, neg16, mul16, div16 and the error rules of the
;   Lab 3 calculator, checked against test vectors stored in Flash.
;   At reset all tests run -> "Self-test 12/12".  Then:
;   SW4 next test   SW5 previous test   SW8 run the self-test again
; Student: <name>        ID: <student ID>
; Kit: MPS 2026, ATmega32A @ 16 MHz
;===============================================================
.include "m32def.inc"
.equ    OP_ADD = 0               ;operator codes (same order as Ex 3a)
.equ    OP_SUB = 1
.equ    OP_MUL = 2
.equ    OP_DIV = 3
.equ    ST_OK  = 0               ;status codes of a result
.equ    ST_NEG = 1               ;  negative (A - B with A < B)
.equ    ST_OVF = 2               ;  overflow (> 65535)
.equ    ST_DV0 = 3               ;  division by zero
.equ    TSIZE  = 10              ;bytes per test vector
.equ    NTESTS = 12              ;number of test vectors (update when you add tests)
.dseg
.org    0x0060
vars:                            ;one test, addressed as Y + q:
v_op:   .byte 1                  ;Y+0  operator
v_xst:  .byte 1                  ;Y+1  expected status
v_a:    .byte 2                  ;Y+2  A
v_b:    .byte 2                  ;Y+4  B
v_xr:   .byte 2                  ;Y+6  expected result
v_xr2:  .byte 2                  ;Y+8  expected remainder
v_r:    .byte 2                  ;Y+10 result     (by calc)
v_r2:   .byte 2                  ;Y+12 remainder  (by calc)
v_st:   .byte 1                  ;Y+14 status     (by calc)
dbuf:   .byte 5                  ;digits for print_u16
.cseg
.org    0x0000
        rjmp  reset
.org    INT_VECTORS_SIZE
reset:  ldi   r16, high(RAMEND)
        out   sph, r16
        ldi   r16, low(RAMEND)
        out   spl, r16
        ldi   r16, 0x1F
        out   DDRA, r16          ;LEDs: test number in binary
        out   PORTB, r16         ;pull-ups on SW4..SW8
        mov   r15, r16
        rcall lcd_init

selftest:                        ;run every test, count the passes
        clr   r11                ;r11 = test number (calc uses r16-r25)
        clr   r12                ;r12 = passes
st_lp:  rcall load_test
        rcall calc
        rcall check              ;r13 = 1 if the test passed
        add   r12, r13
        inc   r11
        mov   r16, r11
        cpi   r16, NTESTS
        brlo  st_lp
        ldi   r16, 0x01
        rcall lcd_cmd            ;clear
        ldi   r30, low(t_self*2)
        ldi   r31, high(t_self*2)
        rcall lcd_puts           ;"Self-test "
        mov   r22, r12
        clr   r23
        rcall print_u16L
        ldi   r16, '/'
        rcall lcd_data
        ldi   r22, NTESTS
        clr   r23
        rcall print_u16L
        ldi   r20, 1
        ldi   r21, 0
        rcall lcd_gotoxy
        ldi   r30, low(t_keys*2)
        ldi   r31, high(t_keys*2)
        rcall lcd_puts           ;"SW4 > SW5 <"
        clr   r11                ;browse from test #1
        ser   r16
        out   PORTA, r16         ;all LEDs on
st_wait:
        rcall key_wait
        breq  st_wait            ;any key -> browse the tests

main:   rcall load_test          ;browse: show test r11
        rcall calc
        rcall check
        rcall show
mn_wait:
        rcall key_wait
        breq  mn_wait
        sbrc  r14, 4
        rjmp  selftest           ;SW8
        mov   r16, r11
        sbrc  r14, 0
        inc   r16                ;SW4
        sbrc  r14, 1
        dec   r16                ;SW5
        cpi   r16, NTESTS
        brlo  mn_set
        clr   r16                ;past the end -> first
        sbrc  r14, 1
        ldi   r16, NTESTS-1      ;0 - 1 -> last
mn_set: mov   r11, r16
        rjmp  main

;---- key_wait: 10 ms, then r14 = new presses, Z flag = 1 if none ----
key_wait:
        ldi   r24, 10
        rcall delay_ms
        in    r16, PINB
        andi  r16, 0x1F
        mov   r17, r16
        com   r16
        and   r16, r15
        mov   r15, r17
        mov   r14, r16
        tst   r14
        ret

;---- load_test: copy test r11 from Flash to vars (LPM Z+ -> ST X+) ----
load_test:
        ldi   r30, low(tests*2)
        ldi   r31, high(tests*2)
        ldi   r16, TSIZE
        mul   r11, r16           ;r1:r0 = test number * 10
        add   r30, r0
        adc   r31, r1            ;Z = tests*2 + n*10
        ldi   r26, low(vars)
        ldi   r27, high(vars)
        ldi   r17, TSIZE
lt_cp:  lpm   r16, Z+            ;a byte from Flash ...
        st    X+, r16            ;... into SRAM
        dec   r17
        brne  lt_cp
        ret

;---------------------------------------------------------------
; calc: R = A op B with the calculator's error rules
;   in : vars (Y+0 op, Y+2 A, Y+4 B)
;   out: Y+10 result, Y+12 remainder, Y+14 status
;---------------------------------------------------------------
calc:   ldi   r28, low(vars)
        ldi   r29, high(vars)
        ldd   r22, Y+2           ;A -> r23:r22
        ldd   r23, Y+3
        ldd   r20, Y+4           ;B -> r21:r20
        ldd   r21, Y+5
        clr   r19                ;status = OK
        clr   r24                ;remainder = 0
        clr   r25
        ldd   r16, Y+0
        cpi   r16, OP_ADD
        breq  c_add
        cpi   r16, OP_SUB
        breq  c_sub
        cpi   r16, OP_MUL
        breq  c_mul
c_div:  mov   r16, r20           ;B = 0 ?
        or    r16, r21
        brne  c_dv
        ldi   r19, ST_DV0
        rjmp  c_store
c_dv:   rcall div16              ;quotient r23:r22, remainder r25:r24
        rjmp  c_store
c_add:  rcall add16
        brcc  c_store            ;no carry -> fits in 16 bits
        ldi   r19, ST_OVF
        rjmp  c_store
c_sub:  rcall sub16
        brcc  c_store            ;no borrow -> A >= B
        rcall neg16              ;show |A - B| ...
        ldi   r19, ST_NEG        ;... with a minus sign
        rjmp  c_store
c_mul:  rcall mul16              ;32-bit product r25:r24:r23:r22
        mov   r16, r24
        or    r16, r25           ;high word = 0 ?
        breq  c_mz
        ldi   r19, ST_OVF
c_mz:   clr   r24                ;no remainder for x
        clr   r25
c_store:
        std   Y+10, r22
        std   Y+11, r23
        std   Y+12, r24
        std   Y+13, r25
        std   Y+14, r19
        ret

;---- add16: r23:r22 += r21:r20, C = 1 -> overflow ----
add16:  add   r22, r20
        adc   r23, r21
        ret
;---- sub16: r23:r22 -= r21:r20, C = 1 -> negative (borrow) ----
sub16:  sub   r22, r20
        sbc   r23, r21
        ret
;---- neg16: r23:r22 = -r23:r22 (two's complement) ----
neg16:  com   r23                ;invert the high byte
        neg   r22                ;two's complement of the low byte, C = (r22 != 0)
        sbci  r23, -1            ;+1 into the high byte only if r22 was 0
        ret
;---- mul16: r25:r24:r23:r22 = r23:r22 x r21:r20 (4 MULs) ----
mul16:  mul   r22, r20           ;AL x BL -> bytes 0, 1
        movw  r16, r0
        mul   r23, r21           ;AH x BH -> bytes 2, 3
        movw  r18, r0
        clr   r24                ;zero for the carries
        mul   r23, r20           ;AH x BL -> bytes 1, 2
        add   r17, r0
        adc   r18, r1
        adc   r19, r24
        mul   r22, r21           ;AL x BH -> bytes 1, 2
        add   r17, r0
        adc   r18, r1
        adc   r19, r24
        movw  r22, r16           ;low word of the product
        movw  r24, r18           ;high word
        ret
;---- div16: r23:r22 / r21:r20 -> quotient r23:r22, remainder r25:r24 ----
;     shift-and-subtract, 16 steps (like long division on paper)
div16:  clr   r24
        clr   r25                ;remainder = 0
        ldi   r17, 16
dv_lp:  lsl   r22                ;shift A left, its MSB ...
        rol   r23
        rol   r24                ;... into the remainder
        rol   r25
        brcs  dv_sub             ;17-bit remainder -> surely >= B
        cp    r24, r20
        cpc   r25, r21
        brlo  dv_nx              ;remainder < B -> quotient bit 0
dv_sub: sub   r24, r20
        sbc   r25, r21
        inc   r22                ;quotient bit = 1
dv_nx:  dec   r17
        brne  dv_lp
        ret

;---- check: r13 = 1 if status, result and remainder are as expected ----
check:  clr   r13
        ldd   r16, Y+14          ;status
        ldd   r17, Y+1           ;expected status
        cp    r16, r17
        brne  ck_end             ;wrong status -> fail
        cpi   r16, ST_OVF        ;error results have no value
        brsh  ck_ok
        ldi   r26, low(v_r)
        ldi   r27, high(v_r)
        ldi   r30, low(v_xr)
        ldi   r31, high(v_xr)
        ldi   r17, 4             ;compare 4 bytes
ck_lp:  ld    r16, X+
        ld    r18, Z+
        cp    r16, r18
        brne  ck_end
        dec   r17
        brne  ck_lp
ck_ok:  inc   r13
ck_end: ret

;---- show: "#3 5000-1234" / "=3766        OK" ----
show:   ldi   r16, 0x01
        rcall lcd_cmd            ;clear
        ldi   r16, '#'
        rcall lcd_data
        mov   r22, r11
        inc   r22                ;tests are numbered from 1
        out   PORTA, r22
        clr   r23
        rcall print_u16L
        ldi   r16, ' '
        rcall lcd_data
        lds   r22, v_a
        lds   r23, v_a+1
        rcall print_u16L         ;A
        ldi   r30, low(sym_tab*2)
        ldi   r31, high(sym_tab*2)
        lds   r16, v_op
        add   r30, r16
        clr   r16
        adc   r31, r16
        lpm   r16, Z
        rcall lcd_data           ;operator symbol
        lds   r22, v_b
        lds   r23, v_b+1
        rcall print_u16L         ;B
        ldi   r20, 1
        ldi   r21, 0
        rcall lcd_gotoxy
        ldi   r16, '='
        rcall lcd_data
        lds   r16, v_st
        cpi   r16, ST_OVF
        breq  sh_ovf
        cpi   r16, ST_DV0
        breq  sh_dv0
        cpi   r16, ST_NEG
        brne  sh_val
        ldi   r16, '-'
        rcall lcd_data
sh_val: lds   r22, v_r
        lds   r23, v_r+1
        rcall print_u16L         ;result
        lds   r16, v_op
        cpi   r16, OP_DIV
        brne  sh_res
        ldi   r16, ' '
        rcall lcd_data
        ldi   r16, 'r'
        rcall lcd_data
        lds   r22, v_r2
        lds   r23, v_r2+1
        rcall print_u16L         ;remainder
        rjmp  sh_res
sh_ovf: ldi   r30, low(t_ovf*2)
        ldi   r31, high(t_ovf*2)
        rjmp  sh_txt
sh_dv0: ldi   r30, low(t_dv0*2)
        ldi   r31, high(t_dv0*2)
sh_txt: rcall lcd_puts
sh_res: ldi   r20, 1
        ldi   r21, 13
        rcall lcd_gotoxy
        ldi   r30, low(t_ok*2)
        ldi   r31, high(t_ok*2)
        tst   r13
        brne  sh_pf
        ldi   r30, low(t_bad*2)
        ldi   r31, high(t_bad*2)
sh_pf:  rjmp  lcd_puts           ;its ret returns to main

;---- print_u16 / print_u16L: r23:r22 in decimal (see Ex 2) ----
print_u16:
        set                      ;T = 1: leading zeros -> blanks
        rjmp  pu_go
print_u16L:
        clt                      ;T = 0: leading zeros skipped
pu_go:  push  r28
        push  r29
        ldi   r30, low(pow10*2)
        ldi   r31, high(pow10*2)
        ldi   r28, low(dbuf)
        ldi   r29, high(dbuf)
pu_pow: lpm   r20, Z+
        lpm   r21, Z+
        ldi   r16, '0'
pu_sub: sub   r22, r20
        sbc   r23, r21
        brcs  pu_back
        inc   r16
        rjmp  pu_sub
pu_back:
        add   r22, r20
        adc   r23, r21
        st    Y+, r16
        cpi   r20, 1
        brne  pu_pow
        ldi   r28, low(dbuf)
        ldi   r29, high(dbuf)
        ldi   r19, 4
pu_lz:  ld    r16, Y
        cpi   r16, '0'
        brne  pu_out
        brtc  pu_skip
        ldi   r16, ' '
        rcall lcd_data
pu_skip:
        adiw  r28, 1
        dec   r19
        brne  pu_lz
pu_out: ld    r16, Y+
        rcall lcd_data
        cpi   r28, low(dbuf+5)
        brne  pu_out
        pop   r29
        pop   r28
        ret
pow10:  .dw   10000, 1000, 100, 10, 1

;---- test vectors: op, expected status, A, B, expected R, expected R2 ----
tests:
        .db OP_ADD, ST_OK
        .dw  1234,  4321,  5555, 0     ;#1
        .db OP_ADD, ST_OVF
        .dw 65535,     1,     0, 0     ;#2  carry out -> overflow
        .db OP_ADD, ST_OK
        .dw 40000, 25535, 65535, 0     ;#3  largest result
        .db OP_SUB, ST_OK
        .dw  5000,  1234,  3766, 0     ;#4
        .db OP_SUB, ST_NEG
        .dw  1234,  5000,  3766, 0     ;#5  borrow -> negative, shown as -3766
        .db OP_SUB, ST_OK
        .dw     0,     0,     0, 0     ;#6
        .db OP_MUL, ST_OK
        .dw   255,   255, 65025, 0     ;#7
        .db OP_MUL, ST_OVF
        .dw   300,   300,     0, 0     ;#8  90000 > 65535
        .db OP_MUL, ST_OK
        .dw  1000,    65, 65000, 0     ;#9
        .db OP_DIV, ST_OK
        .dw 65535,    10,  6553, 5     ;#10 quotient and remainder
        .db OP_DIV, ST_OK
        .dw   100,     7,    14, 2     ;#11
        .db OP_DIV, ST_DV0
        .dw     5,     0,     0, 0     ;#12 division by zero

sym_tab: .db "+-x/"
t_self:  .db "Self-test ", 0, 0
t_keys:  .db "SW4 > SW5 <", 0
t_ovf:   .db "OVERFLOW", 0, 0
t_dv0:   .db "DIV BY 0", 0, 0
t_ok:    .db " OK", 0
t_bad:   .db "BAD", 0
.include "lcd4.inc"
.include "delay.inc"
