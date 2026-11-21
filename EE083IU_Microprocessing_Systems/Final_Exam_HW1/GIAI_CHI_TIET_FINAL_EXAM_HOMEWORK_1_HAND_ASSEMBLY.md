# MICRO-PROCESSING SYSTEMS (EE083IU)
## FINAL EXAM REVIEW — HOMEWORK 1: HAND ASSEMBLY OF ATMEGA32 CODE

**Sinh viên:** NGUYỄN LÊ MINH SANG | **MSSV:** EEACIU24096 | **Nhóm:** G02

---

### Part A — Register and Immediate Instructions

| # | Instruction | Field Values | Binary Pattern | Hex Word | Flash Bytes |
|---|---|---|---|---|---|
| 1 | `LDI R16, 0x3F` | K=0x3F=0011 1111, d=16-16=0=0000 | `1110 0011 0000 1111` | `E30F` | **`0F E3`** |
| 2 | `LDI R31, 200` | K=200=0xC8=1100 1000, d=31-16=15=1111 | `1110 1100 1111 1000` | `ECF8` | **`F8 EC`** |
| 3 | `MOV R5, R20` | d=5=00101, r=20=10100 (r4=1, r3..0=0100) | `0010 1110 0101 0100` | `2E54` | **`54 2E`** |
| 4 | `ADD R1, R17` | d=1=00001, r=17=10001 (r4=1, r3..0=0001) | `0000 1110 0001 0001` | `0E11` | **`11 0E`** |
| 5 | `ADC R25, R30` | d=25=11001, r=30=11110 (r4=1, r3..0=1110) | `0001 1111 1001 1110` | `1F9E` | **`9E 1F`** |
| 6 | `SUB R18, R2` | d=18=10010, r=2=00010 (r4=0, r3..0=0010) | `0001 1001 0010 0010` | `1922` | **`22 19`** |
| 7 | `AND R24, R7` | d=24=11000, r=7=00111 (r4=0, r3..0=0111) | `0010 0001 1000 0111` | `2187` | **`87 21`** |
| 8 | `EOR R0, R31` | d=0=00000, r=31=11111 (r4=1, r3..0=1111) | `0010 0110 0000 1111` | `260F` | **`0F 26`** |
| 9 | `ANDI R20, 0x0F` | K=0x0F=0000 1111, d=20-16=4=0100 | `0111 0000 0100 1111` | `704F` | **`4F 70`** |
| 10 | `ORI R29, 0b10000001` | K=0x81=1000 0001, d=29-16=13=1101 | `0110 1000 1101 0001` | `68D1` | **`D1 68`** |
| 11 | `SUBI R17, 1` | K=1=0000 0001, d=17-16=1=0001 | `0101 0000 0001 0001` | `5011` | **`11 50`** |
| 12 | `CPI R26, 'A'` | K='A'=0x41=0100 0001, d=26-16=10=1010 | `0011 0100 1010 0001` | `34A1` | **`A1 34`** |
| 13 | `COM R3` | d=3=00011, opcode 1001 010d dddd 0000 | `1001 0100 0011 0000` | `9430` | **`30 94`** |
| 14 | `INC R22` | d=22=10110, opcode 1001 010d dddd 0011 | `1001 0101 0110 0011` | `9563` | **`63 95`** |
| 15 | `DEC R31` | d=31=11111, opcode 1001 010d dddd 1010 | `1001 0101 1111 1010` | `95FA` | **`FA 95`** |
| 16 | `LSR R16` | d=16=10000, opcode 1001 010d dddd 0110 | `1001 0101 0000 0110` | `9506` | **`06 95`** |
| 17 | `SWAP R9` | d=9=01001, opcode 1001 010d dddd 0010 | `1001 0100 1001 0010` | `9492` | **`92 94`** |
| 18 | `LSL R12` | Alias ADD R12, R12 (d=12=01100, r=12=01100) | `0000 1100 1100 1100` | `0CCC` | **`CC 0C`** |
| 19 | `CLR R30` | Alias EOR R30, R30 (d=30=11110, r=30=11110) | `0010 0111 1110 1110` | `27EE` | **`EE 27`** |
| 20 | `SER R19` | Alias LDI R19, 0xFF (K=0xFF, d=19-16=3=0011) | `1110 1111 0011 1111` | `EF3F` | **`3F EF`** |

### Part B — I/O and Bit Instructions

| # | Instruction | Field Values | Binary Pattern | Hex Word | Flash Bytes |
|---|---|---|---|---|---|
| 21 | `OUT PORTB, R16` | A=PORTB=0x18=011000, r=16=10000 | `1011 1011 0000 1000` | `BB08` | **`08 BB`** |
| 22 | `IN R24, PINA` | A=PINA=0x19=011001, d=24=11000 | `1011 0011 1000 1001` | `B389` | **`89 B3`** |
| 23 | `OUT DDRC, R31` | A=DDRC=0x14=010100, r=31=11111 | `1011 1011 1111 0100` | `BBF4` | **`F4 BB`** |
| 24 | `IN R0, SREG` | A=SREG=0x3F=111111, d=0=00000 | `1011 0110 0000 1111` | `B60F` | **`0F B6`** |
| 25 | `OUT SPL, R17` | A=SPL=0x3D=111101, r=17=10001 | `1011 1111 0001 1101` | `BF1D` | **`1D BF`** |
| 26 | `SBI PORTD, 7` | A=PORTD=0x12=10010, b=7=111 | `1001 1010 1001 0111` | `9A97` | **`97 9A`** |
| 27 | `CBI DDRB, 0` | A=DDRB=0x17=10111, b=0=000 | `1001 1000 1011 1000` | `98B8` | **`B8 98`** |
| 28 | `SBIS PINC, 3` | A=PINC=0x13=10011, b=3=011 | `1001 1011 1001 1011` | `9B9B` | **`9B 9B`** |
| 29 | `SBRC R20, 6` | r=20=10100, b=6=110 | `1111 1101 0100 0110` | `FD46` | **`46 FD`** |
| 30 | `OUT UDR, R18` | A=UDR=0x0C=001100, r=18=10010 | `1011 1001 0010 1100` | `B92C` | **`2C B9`** |

### Part C — Memory, Stack and Word Instructions

| # | Instruction | Field Values | Binary Pattern | Hex Word | Flash Bytes |
|---|---|---|---|---|---|
| 31 | `PUSH R16` | r=16=10000, opcode 1001 001r rrrr 1111 | `1001 0011 0000 1111` | `930F` | **`0F 93`** |
| 32 | `POP R31` | d=31=11111, opcode 1001 000d dddd 1111 | `1001 0001 1111 1111` | `91FF` | **`FF 91`** |
| 33 | `LD R10, X+` | d=10=01010, opcode 1001 000d dddd 1101 | `1001 0000 1010 1101` | `90AD` | **`AD 90`** |
| 34 | `ST -Y, R5` | r=5=00101, opcode 1001 001r rrrr 1010 | `1001 0010 0101 1010` | `925A` | **`5A 92`** |
| 35 | `LD R1, Z` | d=1=00001, opcode 1000 000d dddd 0000 | `1000 0000 0001 0000` | `8010` | **`10 80`** |
| 36 | `LPM R0, Z+` | d=0=00000, opcode 1001 000d dddd 0101 | `1001 0000 0000 0101` | `9005` | **`05 90`** |
| 37 | `ADIW R26, 1` | dd=(26-24)/2=1=01, K=1=000001 | `1001 0110 0001 0001` | `9611` | **`11 96`** |
| 38 | `SBIW R30, 32` | dd=(30-24)/2=3=11, K=32=100000 | `1001 0111 1011 0000` | `97B0` | **`B0 97`** |
| 39 | `MUL R16, R17` | d=16=10000, r=17=10001 (r4=1, r3..0=0001) | `1001 1111 0000 0001` | `9F01` | **`01 9F`** |
| 40 | `RETI` | opcode 1001 0101 0001 1000 | `1001 0101 0001 1000` | `9518` | **`18 95`** |

### Part D — Two-Word Instructions

| # | Instruction | Field Values & Logic | Hex Words | Flash Bytes |
|---|---|---|---|---|
| 41 | `JMP 0x0123` | k=0x0123 (22-bit, k16..21=0)
W1: 1001 0100 0000 1100, W2: 0000 0001 0010 0011 | `940C 0123` | **`0C 94 23 01`** |
| 42 | `CALL 0x3F00` | k=0x3F00 (22-bit, k16..21=0)
W1: 1001 0100 0000 1110, W2: 0011 1111 0000 0000 | `940E 3F00` | **`0E 94 00 3F`** |
| 43 | `LDS R16, 0x0060` | d=16=10000, k=0x0060
W1: 1001 0001 0000 0000, W2: 0000 0000 0110 0000 | `9100 0060` | **`00 91 60 00`** |
| 44 | `STS 0x0100, R25` | r=25=11001, k=0x0100
W1: 1001 0011 1001 0000, W2: 0000 0001 0000 0000 | `9390 0100` | **`90 93 00 01`** |

### Part E — Relative Jumps and Branches

```text
E1: RJMP START at word address 0x0000 (Target START = 0x002A)
  - Công thức: k = Target - (PC + 1) = 0x002A - (0x0000 + 1) = 0x0029 = +41 (dạng bù 2 12-bit: 0000 0010 1001)
  - Pattern: 1100 kkkk kkkk kkkk -> 1100 0000 0010 1001 = 0xC029
  - Flash bytes: 29 C0

E2: RCALL DELAY at word address 0x002F (Target DELAY = 0x0031)
  - Công thức: k = Target - (PC + 1) = 0x0031 - (0x002F + 1) = 0x0031 - 0x0030 = +1 (12-bit: 0000 0000 0001)
  - Pattern: 1101 kkkk kkkk kkkk -> 1101 0000 0000 0001 = 0xD001
  - Flash bytes: 01 D0

E3: RJMP LOOP at word address 0x0030 (Target LOOP = 0x002D)
  - Công thức: k = Target - (PC + 1) = 0x002D - (0x0030 + 1) = 0x002D - 0x0031 = -4
  - Bù 2 12-bit của -4: +4 = 0000 0000 0100 -> đảo bit + 1 = 1111 1111 1100 (0xFFC)
  - Pattern: 1100 kkkk kkkk kkkk -> 1100 1111 1111 1100 = 0xCFFC
  - Flash bytes: FC CF

E4: BRNE D1 at word address 0x0033 (Target D1 = 0x0032)
  - Công thức: k = Target - (PC + 1) = 0x0032 - (0x0033 + 1) = 0x0032 - 0x0034 = -2
  - Bù 2 7-bit của -2: +2 = 0000010 -> đảo bit + 1 = 1111110
  - Pattern BRNE: 1111 01kk kkkk k001 -> 1111 0111 1111 0001 = 0xF7F1
  - Flash bytes: F1 F7

E5: Phân tích mã CFF9 lưu tại word address 0x0100:
  - CFF9 nhị phân: 1100 1111 1111 1001. Opcode 1100 là lệnh RJMP.
  - Giá trị k 12-bit: 1111 1111 1001 (bù 2 âm: đảo bit + 1 = 0000 0000 0111 = -7).
  - Điểm nhảy: Target = PC + 1 + k = 0x0100 + 1 - 7 = 0x00FA (word address).
  - Kết luận: Lệnh là RJMP 0x00FA.

E6: Lệnh BREQ TARGET tại 0x0050 với TARGET tại 0x0095:
  - Tính offset: k = 0x0095 - (0x0050 + 1) = 0x0044 = +68 words.
  - Phân tích lỗi: Trường offset k của BRxx chỉ có 7-bit signed (-64 đến +63). Do đó +68 vượt quá tầm nhảy.
  - Trình biên dịch báo: "Relative branch out of reach".
  - Cách sửa: Đảo ngược điều kiện rẽ nhánh và dùng lệnh nhảy không điều kiện tầm xa (RJMP hoặc JMP):
      BRNE SKIP
      RJMP TARGET
  SKIP:

E7: Lệnh SBIS PINC, 3 tại 0x0040 theo sau bởi STS 0x0060, R18:
  - Khi chân PC3 = 1, lệnh SBIS kiểm tra bit có giá trị 1 nên sẽ BỎ QUA lệnh kế tiếp.
  - Vì STS là lệnh 32-bit (chiếm 2 word: word 0x0041 và word 0x0042), theo kiến trúc AVR, vi điều khiển sẽ bỏ qua cả 2 word lệnh.
  - Do đó, chương trình tiếp tục thực thi tại word address 0x0043.
```

### Part F — Assemble Program P1 into Intel HEX

```text
(b) File Intel HEX hoàn chỉnh:
:0200000029C015
:100054000FEF07BB10E018BB139501D0FCCF44E613
:060064004A95F1F7089531
:00000001FF

(c) Cách tính Checksum bản ghi bắt đầu tại Byte Address 0x0064 (:060064004A95F1F7089531):
  - Byte count LL = 0x06
  - Address AAAA = 0x00, 0x64
  - Record Type TT = 0x00
  - Data = 0x4A, 0x95, 0xF1, 0xF7, 0x08, 0x95
  - Tổng các byte = 06 + 00 + 64 + 00 + 4A + 95 + F1 + F7 + 08 + 95 = 0x02CF
  - Lấy byte thấp: 0xCF
  - Checksum = 0x100 - 0xCF = 0x31 (Chính xác 100%).
```

### Part G — Disassemble a HEX File

```text
(c) Phân tích hành vi chương trình:
  - Chương trình khởi tạo PORTC với giá trị 0x55.
  - Vòng lặp liên tục đọc trạng thái cổng PIND vào R17, lọc 4 bit thấp (ANDI R17, 0x0F) rồi so sánh với 10 (0x0A).
  - Cổng PIND CÓ làm thay đổi luồng thực thi: nếu PIND < 10, lệnh SWAP R17 được thực thi; sau đó lệnh COM R16 đảo bit dữ liệu và xuất ra PORTC (0x55 <-> 0xAA) tạo tín hiệu nhấp nháy/dao động logic.
```

### Part H — Instructions that cannot be encoded

| # | Lệnh sai | Lý do vi phạm opcode | Mã chuẩn thay thế |
|---|---|---|---|
| H1 | `LDI R10, 5` | LDI chỉ hỗ trợ thanh ghi cao R16..R31 (trường d chỉ có 4 bit, mã hoá d-16). | `LDI R16, 5
MOV R10, R16` |
| H2 | `ANDI R3, 0x0F` | ANDI chỉ hỗ trợ R16..R31 do trường d chỉ có 4 bit. | `LDI R16, 0x0F
AND R3, R16` |
| H3 | `SBI 0x25, 1` | SBI chỉ hỗ trợ vùng I/O địa chỉ 0x00..0x1F (5-bit). Địa chỉ 0x25 nằm ngoài tầm. | `IN R16, 0x25
ORI R16, (1<<1)
OUT 0x25, R16` |
| H4 | `OUT 0x40, R16` | OUT chỉ hỗ trợ địa chỉ I/O 6-bit (0x00..0x3F). Địa chỉ 0x40 nằm trong vùng SRAM mở rộng. | `STS 0x0060, R16 (địa chỉ data = 0x40 + 0x20 = 0x60)` |
| H5 | `ADIW R20, 1` | ADIW chỉ hỗ trợ 4 cặp con trỏ: R24:R25, R26:R27 (X), R28:R29 (Y), R30:R31 (Z). | `SUBI R20, -1
SBCI R21, -1` |
| H6 | `ADIW R24, 100` | Trường giá trị tức thời K của ADIW chỉ có 6-bit (0..63). 100 vượt quá 63. | `ADIW R24, 63
ADIW R24, 37` |
| H7 | `MOV R16, 25` | MOV chỉ sao chép giữa 2 thanh ghi (Rd, Rr), không nạp trực tiếp hằng số (immediate). | `LDI R16, 25` |
| H8 | `SBI PORTB, 8` | Thanh ghi I/O 8-bit chỉ có vị trí bit từ 0 đến 7 (b=0..7). Bit 8 không tồn tại. | `SBI PORTB, 7 (hoặc chọn đúng bit 0..7)` |
| H9 | `BRNE LOOP (80 words back)` | Trường nhảy rẽ nhánh BRxx chỉ có 7-bit bù 2 (-64 đến +63 words). -80 bị out of range. | `BREQ SKIP
RJMP LOOP
SKIP:` |
| H10 | `LD R16, R30` | LD là lệnh nạp gián tiếp từ con trỏ X (R27:R26), Y (R29:R28) hoặc Z (R31:R30), không dùng thanh ghi đơn. | `LD R16, Z (với Z = R31:R30)` |

### Bonus — Read a program that uses its own table

```text
B1: Giải mã bản ghi dữ liệu đầu tiên (:040000000C9420003C):
  - Địa chỉ byte: 0x0000
  - Dữ liệu: 0C 94 20 00 -> Ghép từ 16-bit: 940C 0020
  - Lệnh: JMP 0x0020 (nhảy tới word address 0x0020).
  - Điểm bắt đầu chương trình: Word address 0x0020 (tức Byte address 0x0040).

B2: Giải mã 2 từ lệnh tại word address 0x0024 và 0x0025:
  - Bản ghi :10004000: tại byte 0x0040 (word 0x0020):
    0x0020: 08 E0 -> LDI R16, 8
    0x0021: 0E BF -> OUT SPH, R16
    0x0022: 0F E5 -> LDI R16, 0x5F
    0x0023: 0D BF -> OUT SPL, R16
    0x0024: E0 E6 -> LDI R30, 0x60 (Nạp byte thấp của con trỏ Z: ZL = 0x60)
    0x0025: F0 E0 -> LDI R31, 0x00 (Nạp byte cao của con trỏ Z: ZH = 0x00) -> Con trỏ Z = 0x0060.

B3: Tại sao Z = 0x0060 trong khi bảng dữ liệu nằm ở word address 0x0030?
  - Bởi vì bộ nhớ Flash được định địa chỉ theo WORD (16-bit) cho lệnh (PC), nhưng lệnh LPM (Load Program Memory) truy xuất bộ nhớ Flash theo từng BYTE riêng biệt.
  - Byte address = Word address x 2 = 0x0030 x 2 = 0x0060. Do đó Z bắt buộc phải trỏ vào 0x0060!

B4: Bản ghi cuối cùng (:04006000030507008D):
  - Dữ liệu: 03, 05, 07, 00 tại địa chỉ byte 0x0060.
  - Đây là DỮ LIỆU CỦA BẢNG TRA (Look-up Table Data) đặt trong Flash, không phải mã lệnh thực thi.

B5: Giá trị lưu vào vùng nhớ SRAM địa chỉ 0x0060 khi chương trình kết thúc:
  - Vòng lặp thực hiện cộng dồn các phần tử trong bảng (03 + 05 + 07 = 15 = 0x0F).
  - Kết quả được lưu bằng lệnh STS 0x0060, R2 (hoặc R20): Giá trị trong ô nhớ 0x0060 là 15 (0x0F).
```
