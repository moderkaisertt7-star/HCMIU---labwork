;===============================================================
; lcdutil.inc - number printing for the LCD (needs lcd4.inc)
;   lcd_print_hex : r20 -> two hex digits      (uses r16)
;   lcd_print_bin : r20 -> eight '0'/'1'        (uses r16, r19, r20)
;   lcd_print_flags: r20 = SREG -> "ITHSVNZC" with '-' for 0
;===============================================================
lcd_print_hex:
        mov   r16, r20
        swap  r16                ;high nibble first
        rcall hex_digit
        mov   r16, r20           ;then the low nibble (falls through)
hex_digit:
        andi  r16, 0x0F
        cpi   r16, 10
        brlo  hd_num
        subi  r16, -7            ;10..15 -> 'A'..'F'
hd_num: subi  r16, -'0'
        rjmp  lcd_data           ;lcd_data's ret returns to the caller

lcd_print_bin:
        ldi   r19, 8
pb_bit: ldi   r16, '0'
        lsl   r20                ;next bit -> C
        brcc  pb_out
        ldi   r16, '1'
pb_out: rcall lcd_data
        dec   r19
        brne  pb_bit
        ret

lcd_print_flags:                 ;prints e.g. "--H---Z-" for H = Z = 1
        ldi   r30, low(fl_names*2)
        ldi   r31, high(fl_names*2)
        ldi   r19, 8
pf_bit: lpm   r16, Z+            ;letter of this flag
        lsl   r20                ;flag bit (I first) -> C
        brcs  pf_out
        ldi   r16, '-'
pf_out: rcall lcd_data
        dec   r19
        brne  pf_bit
        ret
fl_names: .db "ITHSVNZC"
