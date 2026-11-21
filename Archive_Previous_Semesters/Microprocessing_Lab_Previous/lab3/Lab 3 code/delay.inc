;---------------------------------------------------------------
; delay_ms  : waits r24 ms (1..255) at 16 MHz. Uses X (saved). r24 -> 0
; delay_50us: waits exactly 50 us (800 cycles incl. rcall + ret)
;---------------------------------------------------------------
delay_ms:
        push  r26
        push  r27
dms_1:  ldi   r26, low(3999)     ;inner count for exactly 1 ms
        ldi   r27, high(3999)
dms_2:  sbiw  r26, 1             ;2 cycles
        brne  dms_2              ;2 cycles (1 when X = 0)
        dec   r24
        brne  dms_1
        pop   r27
        pop   r26
        ret
delay_50us:
        push  r25                ;2
        ldi   r25, 197           ;1
d50_1:  nop                      ;1
        dec   r25                ;1
        brne  d50_1              ;2 (1 at the end)
        nop                      ;1
        pop   r25                ;2
        ret                      ;4  -> 3+2+1+787+1+2+4 = 800
