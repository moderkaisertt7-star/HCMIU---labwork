;===============================================================
; calc16.inc - Lab 2 building blocks for the Lab 3 calculator
;   MPS 2026 kit, ATmega32A @ 16 MHz.  Needs lcd4.inc + delay.inc.
;
;   keys        r14 = buttons newly pressed (bit0 = SW4 .. bit4 = SW8)
;               r15 = previous state (set r15 = $1F once at reset)
;   mul10_add   r23:r22 = r23:r22 * 10 + r16,  C = 1 -> too big
;   div10       r23:r22 = r23:r22 / 10        (uses X)
;   print_u16   r23:r22 in decimal, 5 characters, leading blanks
;   print_u16L  r23:r22 in decimal, no leading blanks
;   calc16      A = r23:r22, B = r21:r20, op = r16 (0 + 1 - 2 x 3 /)
;               -> r23:r22 result, r25:r24 remainder, r19 status
;   add16 sub16 neg16 mul16 div16   (see each routine)
;   Registers: everything r16..r25, X, Z may change; r0, r1 by MUL.
;===============================================================
.equ    OP_ADD = 0
.equ    OP_SUB = 1
.equ    OP_MUL = 2
.equ    OP_DIV = 3
.equ    ST_OK  = 0               ;status of a result
.equ    ST_NEG = 1               ;  negative, r23:r22 = |A - B|
.equ    ST_OVF = 2               ;  overflow (> 65535)
.equ    ST_DV0 = 3               ;  division by zero
.dseg
dbuf:   .byte 5                  ;digits for print_u16
.cseg

;---- keys: r14 = buttons pressed since the last call (falling edges) ----
keys:   in    r16, PINB
        andi  r16, 0x1F          ;now: 0 = pressed
        mov   r17, r16
        com   r16                ;pressed = 1
        and   r16, r15           ;... and released at the last look
        mov   r15, r17           ;remember the state for next time
        mov   r14, r16           ;drivers never change r14, r15
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
; print_u16 / print_u16L (Lab 2 Ex 2, with Y saved)
;---------------------------------------------------------------
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

;---- calc16: r23:r22 = A op B with the calculator's error rules ----
calc16: clr   r19                ;status = OK
        clr   r24                ;remainder = 0
        clr   r25
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
        ret
c_dv:   rcall div16              ;quotient r23:r22, remainder r25:r24
        ret
c_add:  rcall add16
        brcc  c_end            ;no carry -> fits in 16 bits
        ldi   r19, ST_OVF
        ret
c_sub:  rcall sub16
        brcc  c_end            ;no borrow -> A >= B
        rcall neg16              ;show |A - B| ...
        ldi   r19, ST_NEG        ;... with a minus sign
        ret
c_mul:  rcall mul16              ;32-bit product r25:r24:r23:r22
        mov   r16, r24
        or    r16, r25           ;high word = 0 ?
        breq  c_mz
        ldi   r19, ST_OVF
c_mz:   clr   r24                ;no remainder for x
        clr   r25
c_end:  ret

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

