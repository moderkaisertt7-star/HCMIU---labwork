;===============================================================
; Lab 2 - Exercise 3b: n, n squared (byte table) and n cubed (word table)
; Student: <name>        ID: <student ID>
; Kit: MPS 2026, ATmega32A @ 16 MHz
;===============================================================
.include "m32def.inc"
.org    0x0000
        rjmp  reset              ;reset vector
.org    INT_VECTORS_SIZE         ;program starts after the vector table
reset:  ldi   r16, high(RAMEND)  ;stack pointer -> top of SRAM
        out   sph, r16
        ldi   r16, low(RAMEND)
        out   spl, r16
        ldi   r16, 0x1F
        out   PORTB, r16         ;pull-ups on SW4..SW8
        rcall lcd_init
        clr   r23                ;n = 0 .. 15
show:   ldi   r16, 0x01
        rcall lcd_cmd            ;clear
        ldi   r30, low(t_n*2)
        ldi   r31, high(t_n*2)
        rcall lcd_puts           ;"n="
        mov   r20, r23
        rcall print_dec2         ;n as two digits
        ldi   r30, low(t_sq*2)
        ldi   r31, high(t_sq*2)
        rcall lcd_puts           ;" n^2="
        ; ---- n^2 from the byte table: Z = sq_tab*2 + n ----
        ldi   r30, low(sq_tab*2)
        ldi   r31, high(sq_tab*2)
        add   r30, r23
        clr   r16
        adc   r31, r16           ;16-bit add: carry into ZH
        lpm   r22, Z             ;r22 = n^2 from the table
        mov   r20, r22
        rcall print_dec3b        ;0..225 as three digits
        ; ---- check: n * n with MUL (result in r1:r0) ----
        mul   r23, r23
        ldi   r20, 1
        ldi   r21, 0
        rcall lcd_gotoxy
        ldi   r30, low(t_ok*2)
        ldi   r31, high(t_ok*2)
        cp    r0, r22            ;table value = MUL result?
        breq  chk_ok
        ldi   r30, low(t_err*2)
        ldi   r31, high(t_err*2)
chk_ok: rcall lcd_puts           ;"MUL ok" or "MULERR"
        ; ---- n^3 from the word table: Z = cu_tab*2 + 2n ----
        ldi   r30, low(t_cu*2)
        ldi   r31, high(t_cu*2)
        rcall lcd_puts           ;" n3=$"
        ldi   r30, low(cu_tab*2)
        ldi   r31, high(cu_tab*2)
        mov   r16, r23
        lsl   r16                ;2n: every .dw entry is two bytes
        add   r30, r16
        clr   r16
        adc   r31, r16
        lpm   r22, Z+            ;low byte first (little endian)
        lpm   r20, Z             ;high byte
        rcall lcd_print_hex
        mov   r20, r22
        rcall lcd_print_hex      ;n^3 as 4 hex digits
poll:   sbis  PINB, 0            ;SW4: n + 1
        rjmp  n_up
        sbis  PINB, 1            ;SW5: n - 1
        rjmp  n_dn
        rjmp  poll
n_up:   inc   r23
        rjmp  n_wrap
n_dn:   dec   r23
n_wrap: andi  r23, 0x0F          ;keep 0..15 (15 + 1 -> 0, 0 - 1 -> 15)
        ldi   r24, 20
        rcall delay_ms
rel:    in    r16, PINB
        andi  r16, 0x03
        cpi   r16, 0x03
        brne  rel
        ldi   r24, 20
        rcall delay_ms
        rjmp  show

; print_dec2: r20 (0..99) as two digits
print_dec2:
        clr   r19
pd2_t:  cpi   r20, 10
        brlo  pd2_o
        subi  r20, 10
        inc   r19
        rjmp  pd2_t
pd2_o:  mov   r25, r20
        mov   r16, r19
        subi  r16, -'0'
        rcall lcd_data
        mov   r16, r25
        subi  r16, -'0'
        rjmp  lcd_data
; print_dec3b: r20 (0..255) as three digits with leading zeros
print_dec3b:
        ldi   r16, '0'-1
pd3_h:  inc   r16                ;count hundreds directly in ASCII
        subi  r20, 100
        brcc  pd3_h              ;no borrow -> one more hundred
        subi  r20, -100          ;went one too far: add back
        rcall lcd_data
        rjmp  print_dec2
t_n:    .db   "n=", 0, 0
t_sq:   .db   " n^2=", 0
t_ok:   .db   "MUL ok", 0, 0
t_err:  .db   "MULERR", 0, 0
t_cu:   .db   " n3=$", 0
sq_tab: .db   0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225
cu_tab: .dw   0, 1, 8, 27, 64, 125, 216, 343, 512, 729, 1000, 1331, 1728, 2197, 2744, 3375
.include "lcd4.inc"
.include "lcdutil.inc"
.include "delay.inc"
