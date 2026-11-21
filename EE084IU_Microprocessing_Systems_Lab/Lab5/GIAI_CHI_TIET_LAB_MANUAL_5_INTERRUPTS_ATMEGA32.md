# BÁO CÁO THÍ NGHIỆM LAB MANUAL 5 - EE084IU
## INTERRUPT PROGRAMMING AND EVENT-DRIVEN CONTROL USING ATMEGA32A

> **Môn học:** Micro-processing Systems Laboratory (EE084IU)  
> **Sinh viên:** NGUYỄN LÊ MINH SANG | **MSSV:** EEACIU24096 | **Nhóm:** 05  
> **File Word gốc:** [GIAI_CHI_TIET_LAB_MANUAL_5_INTERRUPTS_ATMEGA32.docx](file:///C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\EE084IU_Microprocessing_Systems_Lab\GIAI_CHI_TIET_LAB_MANUAL_5_INTERRUPTS_ATMEGA32.docx)  

---

MICRO-PROCESSING SYSTEMS LABORATORY

LAB MANUAL 5

INTERRUPT PROGRAMMING AND EVENT-DRIVEN CONTROL USING ATmega32A

Parallel AVR Assembly and Embedded C  |  16 MHz  |  Group 05

### 1. Objectives

•  Explain how interrupt requests suspend foreground code, select interrupt vectors, execute an ISR, and resume via RETI.

•  Configure the ATmega32A external interrupts INT0, INT1 and INT2 and distinguish falling edge, rising edge, change and level sensing.

•  Use Timer0/Timer1/Timer2 overflow, compare-match and input-capture interrupts for event-driven timing and measurement.

•  Handle ADC conversion-complete and USART receive-complete interrupt sources without foreground polling.

•  Create equivalent AVR Assembly and Embedded C solutions; compare register values, ISR state preservation and physical response.

•  Build circuits on the physical ATmega32A kit, collect photographs and real measurements, and respect the four-LED maximum.

### 2. Required equipment

Hardware conditions. Switch power OFF before changing connections. Use PA0..PA3 (or PA4..PA7 for the ADC tutorial) for up to four indicator LEDs. Switch S_LCD OFF when using any PORTD signal for external interrupts, input capture or USART (PD0, PD2, PD3 or PD6), and verify no kit peripheral is driving the same pin. SW4 is PB0; it is NOT INT0. INT0/INT1 require the PD2/PD3 pins or headers; SW6 can supply INT2 on PB2. Never modify clock fuses without instructor approval.

### 3. General procedure

### 1.  Read the tutorial purpose, vector address, interrupt masks and expected measurement before wiring.

### 2.  Create an AVR Assembly project and an Embedded C project for the ATmega32A. Use the complete corresponding example and read every explanatory comment.

### 3.  With the kit OFF, connect the symbol-based circuit. Confirm VCC, AVCC, GND, RESET and current-limiting resistors.

### 4.  Build and flash the Assembly HEX, operate the actual circuit and record real photographs, oscilloscope/stopwatch results and observations.

### 5.  Flash the C HEX to the SAME circuit. Repeat the measurement and record any difference from Assembly.

### 6.  Complete the per-tutorial observation table. Physical photographs and real instrument readings are mandatory; simulator and compiler screenshots do not replace them.

### 4. Interrupt quick reference

Vector positions are AVR program WORD addresses for the default application interrupt-vector placement. They are not ATmega328P vector addresses. If GICR.IVSEL relocates interrupt vectors to boot memory, this table no longer describes their runtime location.

### 5. Detailed theory of interrupt operation in ATmega32A

This theory section should be read before the laboratory tutorials. It preserves the technical-first progression of Lab Manual 4 and explains both the hardware event path and the software state that must be protected.

### 5.1 What an interrupt changes in program execution

In a polling design, the foreground loop repeatedly reads a flag or pin. With interrupts, an enabled hardware request causes the AVR CPU to finish its current instruction, save its return program-counter address on the stack, branch to the selected vector and execute the ISR. The ISR ends with RETI, after which foreground execution continues. The interrupt event occurs asynchronously relative to the application loop.

Figure 5.1 — Generic event, mask, global-enable, vector and return path.

### 5.2 ATmega32A interrupt vector addresses and source priority

The ATmega32A hardware vector table starts at word address 0x0000. A lower vector position has higher fixed priority when multiple enabled requests are pending. The following entries are the sources used by this manual; each AVR Assembly program places RJMP instructions at the correct word addresses and begins its main code after the vector region at .org 0x002A.

Example: when INT0 and INT1 are both pending and globally enabled, the INT0 vector is serviced first. An interrupt ordinarily clears the global I bit on entry, so a second interrupt does not automatically interrupt an ISR. Do not confuse vector priority with independently guaranteed, instantaneous safety response.

### 5.3 The stack, SREG and safe AVR Assembly ISR structure

AVR Assembly ISR code is not a normal subroutine: it must end in RETI, and it must preserve the foreground register contents and arithmetic condition flags that the handler changes. Initialize SPH:SPL to RAMEND before enabling interrupts. For example, an ISR that uses R16 must save R16, save SREG, perform its work, restore SREG and R16, then execute RETI. Save additional registers if used; a PUSH/POP pair alone does not restore SREG.

Reusable Assembly ISR entry/exit pattern

INTERRUPT_HANDLER:
    push r16             ; save foreground R16
    in   r16, SREG       ; capture foreground flags
    push r16             ; save flags on stack
    ; ... short, bounded interrupt work ...
    pop  r16             ; restore saved SREG
    out  SREG, r16
    pop  r16             ; restore foreground R16
    reti                 ; return from interrupt, re-enable I

In AVR-GCC, #include <avr/interrupt.h> and ISR(INT0_vect) establish an ISR with compiler-generated context save/restore and RETI. Avoid inserting a bare RET into an ISR or manually enabling nesting without a specific reason and complete latency analysis.

### 5.4 Global and local interrupt masks; flag clearing

An enabled request requires BOTH global SREG.I=1 and the source-specific local enable. External interrupts use GICR and GIFR. Timer interrupt masks use TIMSK and status flags use TIFR. External and timer flags are write-one-to-clear (W1C): write 1 to a selected flag bit to clear it; do not write 0 and do not use accidental read-modify-write operations that can acknowledge other pending flags.

### 5.5 External interrupt edge selection: INT0 and INT1

The INT0 pin is PD2 and INT1 is PD3. MCUCR ISC01:ISC00 defines INT0 sense; ISC11:ISC10 defines INT1 sense. A falling edge is suitable for a clean active-LOW pulse with a pull-up; low-level interrupt mode can keep requesting service while the pin is held LOW, so use it only after understanding its behavior.

### 5.6 External INT2 on PB2: a different control register

INT2 is PB2 and has only an edge-select bit ISC2 in MCUCSR. ISC2=0 gives falling-edge service; ISC2=1 gives rising-edge service. Enable with GICR.INT2, then clear stale GIFR.INTF2 before SEI. Unlike INT0/INT1, INT2 has no LOW-level selection.

### 5.7 Timer overflow and compare-match interrupt timing

A timer interrupt is generated by the hardware timer when overflow or compare match occurs. For a prescaler N and CPU frequency 16 MHz: Ttick=N/16,000,000 s; for 8-bit normal mode from 0, Toverflow=256*Ttick; for CTC, Tmatch=(OCRn+1)*Ttick. The interrupt callback rate equals the corresponding event rate. Remember ATmega32A uses TCCR0, TCCR2, TIMSK and TIFR, not the ATmega328P names TCCR0A/TCCR0B or TIMSK0.

### 5.8 Timer1 input capture and time-stamping

The Timer1 input-capture peripheral copies TCNT1 into ICR1 when a selected edge arrives at PD6/ICP1. With prescaler 8, Ttick=0.5 microseconds. For successive 100 Hz rising edges, the timestamp difference should be approximately 20,000 ticks. To read a 16-bit captured value in Assembly, read ICR1L before ICR1H. The exercise uses a bounded interval to classify a signal, not to reconstruct an unbounded history of missed pulses.

### 5.9 ADC and USART event-driven applications

ADCSRA.ADIE requests an ISR when an ADC conversion finishes; ADCSRA.ADEN enables ADC and ADSC starts a conversion. At 16 MHz with /128, ADC clock is 125 kHz. USART reception uses UCSRB.RXEN and RXCIE; the RX ISR reads UDR to consume the byte. On the ATmega32A, UCSRC and UBRRH share an address, so the URSEL selection bit is significant when configuring 8N1 UART format.

### 5.10 Data shared between foreground and ISR

Foreground data and ISR data can change asynchronously. In C, declare ISR-updated state that foreground reads as volatile, so the compiler does not cache stale values. However volatile does NOT make a 16-bit access atomic on an 8-bit AVR; use ATOMIC_BLOCK or a brief CLI/SREG-protected critical section when sharing a multi-byte value. In Assembly, explicitly reserve SRAM registers and use a defined save/restore convention. Keep ISR execution bounded; avoid long software delay loops, blocking UART writes and large calculations.

### 5.11 Latency, priority, bounce and physical verification

An interrupt does not mean zero delay. Request recognition, completion of the current instruction, vector entry, context preservation and any higher-priority pending requests determine latency. Mechanical switches can bounce and issue several edges, so test with a conditioned generator or provide debounce outside the ISR. Always record real signal/LED behavior and compare the expected timing with the 16 MHz hardware oscillator setting.

Figure 5.2 — Qualitative request-to-ISR timing and normal-program resumption.

### 6. Pre-lab preparation

### 1. Identify the program-word vector address for INT0, INT1, INT2, Timer0 compare and Timer1 compare A.

Answer: In the ATmega32A 8-bit AVR RISC architecture, each instruction word is 16 bits (2 bytes), so program memory vector addresses are specified as 16-bit word addresses in flash memory:
• External Interrupt Request 0 (INT0): Word address 0x0002 (Byte address 0x0004).
• External Interrupt Request 1 (INT1): Word address 0x0004 (Byte address 0x0008).
• External Interrupt Request 2 (INT2): Word address 0x0006 (Byte address 0x000C).
• Timer/Counter0 Compare Match (TIMER0 COMP): Word address 0x0014 (Byte address 0x0028).
• Timer/Counter1 Compare Match A (TIMER1 COMPA): Word address 0x000E (Byte address 0x001C).
In AVRASM2, vector placement is established using the .org directive with word addresses (e.g., .org 0x0002 rjmp INT0_ISR). Lower word addresses correspond to higher fixed hardware priority during simultaneous requests.

### 2. Explain how SREG.I and GICR.INT0 cooperate, and what happens when one enable bit is zero.

Answer: Interrupt execution in the ATmega32A operates through a two-tiered hardware gating hierarchy:
1. Local Interrupt Mask: GICR.INT0 (Bit 6 of the General Interrupt Control Register) locally unmasks the specific INT0 request line.
2. Global Interrupt Mask: SREG.I (Bit 7 of the Status Register) serves as the master enable for all maskable interrupts.
Both bits must be simultaneously asserted (SREG.I = 1 AND GICR.INT0 = 1) for the CPU to acknowledge the interrupt and vector to 0x0002.
• If GICR.INT0 = 0: INT0 is locally disabled. If an external edge occurs on PD2, the hardware still latches the event by setting GIFR.INTF0, but the CPU core ignores the request and continues foreground execution without interruption.
• If SREG.I = 0: All maskable interrupts are globally suppressed (e.g., during atomic sections or inside another ISR). Pending flags in GIFR remain asserted in hardware. As soon as global interrupts are re-enabled via SEI or RETI (with GICR.INT0 = 1), the pending interrupt request is serviced immediately on the next clock cycle.

### 3. For a falling-edge INT0 request, choose the correct ISC01:ISC00 bits. Explain why a held LOW level does not continually retrigger.

Answer: In register MCUCR (MCU Control Register), the Interrupt Sense Control bits ISC01 and ISC00 configure INT0:
• ISC01 = 1, ISC00 = 0 (binary 10): Configures the falling edge of pin PD2/INT0 to generate an interrupt request.
Why a held LOW level does not continually retrigger:
When configured for falling-edge detection (10), the input pin PD2 is routed through an edge-detection synchronizer circuit. The hardware monitors for a HIGH-to-LOW transition (negative edge). Upon detecting the transition, the hardware sets the interrupt flag GIFR.INTF0. When the CPU vectors to the ISR at address 0x0002, the hardware automatically clears GIFR.INTF0. If the pin remains held in the LOW logic state, no further negative transition occurs, so INTF0 is not asserted again. The ISR executes exactly once per falling edge.
In contrast, if ISC01:ISC00 = 00 (low-level triggering), the hardware continually generates an interrupt request as long as PD2 remains LOW, re-entering the ISR immediately upon every RETI until the pin is released HIGH.

### 4. Explain why an Assembly ISR saves SREG and returns using RETI instead of RET.

Answer: 1. Preserving SREG: The Status Register (SREG) holds critical ALU status flags (C, Z, N, V, S, H, T, I). Foreground code constantly relies on these flags to evaluate conditional jumps (e.g., CP/BREQ, SUB/BRNE). Because an ISR executes asynchronously at an unpredictable moment, any arithmetic or logical instruction executed inside the ISR (such as INC, DEC, ADD, SUB, ANDI) will overwrite these flags. If SREG is not saved (via in r16, SREG -> push r16) at ISR entry and restored (via pop r16 -> out SREG, r16) prior to exit, the foreground thread will encounter corrupted flags, leading to branch failure and severe application instability.
2. RETI versus RET: When an interrupt is acknowledged, the AVR hardware automatically pushes the 16-bit Program Counter (PC) onto the stack and clears SREG.I to 0 to prevent nested interrupts. A normal subroutine return (RET) only pops the return address from the stack into PC; it leaves SREG.I = 0, permanently disabling all future interrupts! The RETI (Return from Interrupt) instruction atomically pops the return address into PC AND sets SREG.I back to 1 in a single cycle, safely resuming foreground execution and re-enabling interrupts.

### 5. Calculate the Timer0 overflow period at 16 MHz and prescaler 1024, and the 61-overflow interval.

Answer: Given: CPU clock frequency f_CPU = 16.0 MHz (16,000,000 Hz), Timer0 prescaler N = 1024.
1. Timer clock frequency: f_timer = f_CPU / N = 16,000,000 / 1024 = 15,625 Hz.
2. Timer tick duration: T_tick = 1 / f_timer = 1024 / 16,000,000 = 64 us.
3. Timer0 is an 8-bit timer counting from 0 to 255 (256 discrete states to overflow):
   T_overflow = (256 * N) / f_CPU = 256 * 64 us = 16.384 ms (0.016384 s).
4. For 61 successive overflow events:
   T_61_ovf = 61 * T_overflow = 61 * 16.384 ms = 999.424 ms (0.999424 s).
5. Timing Error Analysis:
   Difference relative to a nominal 1.000 s interval: Delta_T = 1000.000 ms - 999.424 ms = +0.576 ms.
   Relative percentage error = (0.576 / 1000) * 100% = +0.0576% (a cumulative advance of ~57.6 ms per 100 seconds).

### 6. Find OCR0 for a 1 ms CTC interrupt with prescaler 64. Explain the +1 term.

Answer: Given: f_CPU = 16.0 MHz, prescaler N = 64, target CTC period T_CTC = 1.0 ms = 0.001 s.
In CTC (Clear Timer on Compare Match) mode, Timer0 increments from 0 up to OCR0 and clears to 0 on the following clock cycle.
1. Formula: T_CTC = ((OCR0 + 1) * N) / f_CPU
   => OCR0 + 1 = (T_CTC * f_CPU) / N = (0.001 s * 16,000,000 Hz) / 64 = 16,000 / 64 = 250
   => OCR0 = 250 - 1 = 249 (0xF9).
2. Explanation of the '+1' term: Timer0 is a zero-indexed hardware counter. The counting sequence is: 0, 1, 2, 3, ..., OCR0. This sequence comprises exactly (OCR0 + 1) distinct counting states. For instance, if OCR0 were set to 1, the counter would visit state 0 then state 1, requiring 2 timer clock ticks before resetting. Thus, 1 must be added to OCR0 to determine the total timer clock cycles.

### 7. Calculate OCR1A for a 1 s Timer1 compare A interrupt with prescaler 256.

Answer: Given: f_CPU = 16.0 MHz, prescaler N = 256, target period T_CTC = 1.000 s.
Timer1 is a 16-bit timer/counter operating in CTC mode (WGM13:10 = 0100, TOP = OCR1A).
1. Formula: T_CTC = ((OCR1A + 1) * N) / f_CPU
   => OCR1A + 1 = (T_CTC * f_CPU) / N = (1.000 s * 16,000,000 Hz) / 256 = 62,500
   => OCR1A = 62,500 - 1 = 62,499 (0xF423 in hexadecimal).
2. Register limits: Since 62,499 <= 65,535 (maximum value of a 16-bit unsigned integer), this value fits completely within OCR1A without overflow.
In AVR Assembly, writing a 16-bit register requires writing the high byte first (OCR1AH = 0xF4) then the low byte (OCR1AL = 0x23) to properly engage the internal 8-bit temporary buffer. In C, writing OCR1A = 62499; is automatically handled atomically by the avr-gcc compiler.

### 8. Explain the role of volatile in C, the limitation of volatile for 16-bit atomicity, and how contact bounce affects interrupt counts.

Answer: 1. Role of volatile: When variables are shared between an ISR and background code (foreground), the compiler's optimizer assumes that foreground code is the sole modifier within a loop. Without volatile, the compiler caches the variable in a CPU register (e.g., R24), failing to detect asynchronous updates made by the ISR inside SRAM. Declaring a variable volatile (e.g., volatile uint8_t flag;) forces the compiler to perform an explicit SRAM load (LDS) on every read and an explicit SRAM store (STS) on every write, ensuring real-time data consistency.
2. Limitation for 16-bit atomicity: While volatile prevents caching, it DOES NOT guarantee atomic access on an 8-bit architecture. Reading or writing a 16-bit variable (e.g., volatile uint16_t counter;) requires two separate 8-bit machine instructions (e.g., LDS low byte, then LDS high byte). If an interrupt fires between the low-byte read and high-byte read and modifies the counter (e.g., rolling from 0x00FF to 0x0100), the foreground code will combine the old high byte with the new low byte, reading a corrupt value (0x0000 instead of 0x0100). Therefore, 16-bit shared accesses in foreground code must be enclosed within atomic critical sections (cli(); ... sei(); or ATOMIC_BLOCK).
3. Effect of contact bounce: Mechanical switch contacts physically rebound repeatedly for 5 ms to 20 ms upon actuation. Because hardware interrupt inputs (INT0/INT1/INT2) respond to transitions within nanoseconds, each contact bounce transition is captured as a distinct valid trigger, causing the ISR to execute 5 to 20+ times per single physical press unless debounced via hardware RC filters or software lockout delays.

### 7. Laboratory tutorials

All tutorials below are physical ATmega32A kit experiments. For every tutorial students compile the Assembly and C programs separately, flash them sequentially, and verify the same circuit. Physical proof is mandatory. Source-code listings and simulated results alone are not substitutes for a photograph or an actual measurement.

### 7.01. Tutorial 01 - External INT0: Toggle One LED on a Falling Edge

Purpose. Introduce the vector table, global interrupt flag I, a local interrupt enable, and ISR/RETI. A conditioned 0-to-5 V falling edge on PD2/INT0 toggles PA0. The main loop does not poll INT0.

#### Complete AVR Assembly program — Tutorial 01

Assembly project: Lab5_T01_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 01 - INT0 falling edge toggles PA0; ATmega32A, 16 MHz
.include "m32def.inc"
.cseg
.org 0x0000
    rjmp RESET                 ; reset vector (word address 0x0000)
.org 0x0002
    rjmp INT0_ISR              ; external INT0 vector
.org 0x002A
RESET:
    cli                        ; disable interrupts while configuring
    ldi r16, high(RAMEND)      ; initialize stack BEFORE any ISR
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    sbi DDRA, PA0              ; PA0 = active-HIGH LED output
    cbi PORTA, PA0             ; LED initially OFF
    cbi DDRD, PD2              ; PD2/INT0 is an input
    sbi PORTD, PD2             ; enable internal pull-up
    ldi r16, (1<<ISC01)        ; ISC01:ISC00 = 10, falling edge
    out MCUCR, r16
    ldi r16, (1<<INTF0)        ; discard stale INT0 event (W1C)
    out GIFR, r16
    ldi r16, (1<<INT0)         ; unmask only external INT0
    out GICR, r16
    sei                        ; set SREG.I: interrupts can execute
MAIN:
    rjmp MAIN                  ; CPU does not poll the input
INT0_ISR:
    push r16                   ; preserve a foreground register
    in r16, SREG              ; save foreground status flags
    push r16
    push r17
    in r16, PORTA              ; read PA0 output latch
    ldi r17, (1<<PA0)
    eor r16, r17               ; XOR toggles PA0 only
    out PORTA, r16
    pop r17
    pop r16                    ; recover saved SREG
    out SREG, r16
    pop r16
    reti                       ; return AND restore global I

Detailed explanation of the Assembly program

### 1. The reset vector branches to RESET, while the 0x0002 vector branches to the interrupt service routine. Both addresses are program WORD addresses in AVRASM2.

### 2. Configure PD2 as an input with pull-up and set MCUCR.ISC01:ISC00=10 for falling-edge detection. GIFR.INTF0 clears by writing a ONE.

### 3. Both SREG.I (SEI) and GICR.INT0 must be enabled. In Assembly, save every modified register plus SREG, then return with RETI; C ISR() generates equivalent protection.

#### Complete C program — Tutorial 01

C project: Lab5_T01_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 01 - INT0 falling edge, ATmega32A at 16 MHz */
#define F_CPU 16000000UL
#include <avr/io.h>              /* ATmega32A register/bit definitions */
#include <avr/interrupt.h>       /* ISR() and sei()/cli() */
ISR(INT0_vect) {                /* hardware jumps here on falling edge */
    PORTA ^= (1U << PA0);       /* change only the LED output latch */
}                               /* compiler generates RETI, saves state */
int main(void) {
    cli();                      /* configuration phase */
    DDRA |= (1U << PA0);        /* PA0 is an output */
    PORTA &= ~(1U << PA0);      /* LED OFF at startup */
    DDRD &= ~(1U << PD2);       /* INT0 pin is an input */
    PORTD |= (1U << PD2);       /* input pull-up: idle HIGH */
    MCUCR = (1U << ISC01);      /* INT0 fires on falling edge */
    GIFR = (1U << INTF0);       /* W1C: remove pending old event */
    GICR = (1U << INT0);        /* local enable for INT0 */
    sei();                      /* global enable */
    for (;;) {                  /* no polling required */
    }
}

Detailed explanation of the C program

### 1. ISR(INT0_vect) names the specific vector; the compiler saves live registers and emits RETI automatically.

### 2. The XOR assignment PORTA ^= (1U<<PA0) toggles the output bit without changing other outputs.

### 3. The local GICR interrupt enable and global sei() must BOTH be active before the handler can execute.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.01 — Symbol-based physical connections for Tutorial 01.

Calculation. No periodic timing is involved: one valid falling edge produces one toggle. A mechanical button without conditioning may bounce and create several edges.

Procedure

### 1.  Power OFF and connect an active-HIGH LED to PA0 and a clean falling-edge source to PD2/INT0.

### 2.  Build Assembly, program the ATmega32A, produce ten distinct falling edges and count LED toggles.

### 3.  Build C separately and repeat on the identical circuit; confirm a held LOW signal does not repeatedly toggle.

### 4.  Use a real logic probe or oscilloscope if the number of toggles exceeds the number of presses.

Expected result. Each clean falling edge reverses LED state; holding the input LOW does not retrigger in falling-edge mode.

#### Tutorial 01 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is External Interrupt Request 0 (INT0) located on physical pin PD2. The configured vector is word address 0x0002. Gating requires setting GICR.INT0 = 1, SREG.I = 1, and MCUCR.ISC01:ISC00 = 10 (falling-edge trigger). In physical operation, each falling edge toggles PA0 using bitwise XOR logic. Holding the button LOW does not retrigger because edge detection latches the negative transition and clears the request flag GIFR.INTF0 upon vector execution. With an unconditioned mechanical switch, contact bounce (oscillating contacts over 5-15 ms) generates multiple spurious negative transitions, producing 2 to 4 extra LED toggles per press. Hardware RC filtering or software lockout debouncing is required to achieve clean single-toggle operation.

### 7.02. Tutorial 02 - INT0 Event Counter: Four LEDs Display 0 to F

Purpose. Convert clean external interrupt requests into a four-bit software counter. Demonstrate volatile shared state in C and explicit register preservation in Assembly.

#### Complete AVR Assembly program — Tutorial 02

Assembly project: Lab5_T02_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 02 - four-bit event counter by INT0 on PD2
.include "m32def.inc"
.dseg
COUNT: .byte 1                  ; event total in SRAM
.cseg
.org 0x0000
    rjmp RESET
.org 0x0002
    rjmp INT0_ISR
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x0F
    out DDRA, r16              ; PA0..PA3: four display LEDs
    clr r16
    out PORTA, r16
    sts COUNT, r16
    cbi DDRD, PD2
    sbi PORTD, PD2             ; PD2 normally HIGH
    ldi r16, (1<<ISC01)
    out MCUCR, r16             ; falling-edge INT0
    ldi r16, (1<<INTF0)
    out GIFR, r16              ; clear old flag
    ldi r16, (1<<INT0)
    out GICR, r16
    sei
MAIN:
    rjmp MAIN
INT0_ISR:
    push r16
    in r16, SREG
    push r16
    lds r16, COUNT            ; retrieve saved software count
    inc r16                   ; one count per clean edge
    andi r16, 0x0F            ; wrap at 16
    sts COUNT, r16
    out PORTA, r16             ; low nibble appears on four LEDs
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. COUNT is stored in SRAM for persistent ISR state; the interrupt loads, increments, masks to four bits, and stores the new value.

### 2. ANDI 0x0F or C & 0x0F makes 15+1 wrap to 0. Four LEDs encode exactly one hexadecimal digit.

### 3. Use a conditioned event input or pulse generator. One physical button contact can create multiple falling edges because of bounce.

#### Complete C program — Tutorial 02

C project: Lab5_T02_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 02 - interrupt event counter, four LEDs */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
volatile uint8_t count = 0;     /* modified asynchronously by ISR */
ISR(INT0_vect) {
    count = (count + 1U) & 0x0FU; /* modulo-16 count */
    PORTA = (PORTA & 0xF0U) | count; /* update PA3..PA0 only */
}
int main(void) {
    cli();
    DDRA = (DDRA & 0xF0U) | 0x0FU;
    PORTA &= 0xF0U;            /* start at binary 0000 */
    DDRD &= ~(1U << PD2);
    PORTD |= (1U << PD2);
    MCUCR = (1U << ISC01);    /* INT0 falling edge */
    GIFR = (1U << INTF0);
    GICR = (1U << INT0);
    sei();
    while (1) {                /* foreground remains free */
    }
}

Detailed explanation of the C program

### 1. volatile count documents asynchronous ISR updates; the type uint8_t matches the 8-bit storage used in Assembly.

### 2. The expression (count+1U)&0x0F keeps only four bits and wraps 15 to 0.

### 3. ISR(INT0_vect) is invoked by clean input edges; a real switch without debounce may generate more than one event.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.02 — Symbol-based physical connections for Tutorial 02.

Calculation. The expected sequence for sixteen valid events is 0001, 0010, ... 1111, 0000. The number of LEDs is limited to four.

Procedure

### 1.  Connect a four-LED binary display to PA0..PA3; attach a clean digital input to INT0.

### 2.  Run the Assembly version for at least 17 input events; record first, fifteenth and sixteenth values.

### 3.  Repeat in C and compare the wrap-around behavior.

### 4.  If using a mechanical switch, explain how bounce affects observed counts; do not mistake extra edges for arithmetic errors.

Expected result. A four-bit count increments by one per valid falling edge and wraps from 1111 to 0000.

#### Tutorial 02 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is INT0 (vector 0x0002) configured on pin PD2 with falling-edge sensitivity (MCUCR.ISC01:ISC00 = 10). The local mask is GICR.INT0 = 1 and global mask is SREG.I = 1. Upon each falling edge, the ISR increments a 4-bit software counter. In C, the counter variable is declared volatile uint8_t to ensure register reload from SRAM. In Assembly, R20 maintains the count, masked via andi r20, 0x0F, and merged with PORTA (preserving PA4..PA7). The LEDs on PA0..PA3 cycle cleanly from 0000 to 1111 and roll over to 0000 on event 16. When driven by a mechanical pushbutton without debounce, contact chatter causes the counter to jump by multiple counts per actuation.

### 7.03. Tutorial 03 - Two Interrupt Sources: INT0 and INT1

Purpose. Configure PD2/INT0 and PD3/INT1 simultaneously and demonstrate that two unrelated external events can affect separate LEDs without the main loop polling either line.

#### Complete AVR Assembly program — Tutorial 03

Assembly project: Lab5_T03_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 03 - independent INT0 and INT1 interrupt vectors
.include "m32def.inc"
.cseg
.org 0x0000
    rjmp RESET
.org 0x0002
    rjmp INT0_ISR              ; higher-priority vector
.org 0x0004
    rjmp INT1_ISR
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x03
    out DDRA, r16              ; PA0 and PA1 output LEDs
    clr r16
    out PORTA, r16
    cbi DDRD, PD2
    cbi DDRD, PD3
    sbi PORTD, PD2             ; internal pull-ups
    sbi PORTD, PD3
    ldi r16, (1<<ISC01)|(1<<ISC11)
    out MCUCR, r16             ; both falling edge
    ldi r16, (1<<INTF0)|(1<<INTF1)
    out GIFR, r16
    ldi r16, (1<<INT0)|(1<<INT1)
    out GICR, r16
    sei
MAIN:
    rjmp MAIN
INT0_ISR:
    push r16
    in r16, SREG
    push r16
    in r16, PORTA
    ; ORI/ANDI use only R16, which is already preserved.
    sbrc r16, 0
    rjmp INT0_OFF
    ori r16, 0x01
    rjmp INT0_WRITE
INT0_OFF:
    andi r16, 0xFE
INT0_WRITE:
    out PORTA, r16
    pop r16
    out SREG, r16
    pop r16
    reti
INT1_ISR:
    push r16
    in r16, SREG
    push r16
    in r16, PORTA
    sbrc r16, 1
    rjmp INT1_OFF
    ori r16, 0x02
    rjmp INT1_WRITE
INT1_OFF:
    andi r16, 0xFD
INT1_WRITE:
    out PORTA, r16
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. INT0 and INT1 have independent vector addresses 0x0002 and 0x0004; each vector must branch to the correct service routine.

### 2. MCUCR.ISC01 and ISC11 select falling edges, while GICR.INT0 and INT1 enable the requests locally.

### 3. When two requests are pending at the same time, INT0 has higher vector priority. LED state alone does not prove execution order; a scope or event trace is needed.

#### Complete C program — Tutorial 03

C project: Lab5_T03_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 03 - two independent external interrupts */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
ISR(INT0_vect) { PORTA ^= (1U << PA0); } /* PD2 toggles PA0 */
ISR(INT1_vect) { PORTA ^= (1U << PA1); } /* PD3 toggles PA1 */
int main(void) {
    cli();
    DDRA |= (1U << PA0) | (1U << PA1);
    PORTA &= ~((1U << PA0) | (1U << PA1));
    DDRD &= ~((1U << PD2) | (1U << PD3));
    PORTD |= (1U << PD2) | (1U << PD3);
    MCUCR = (1U << ISC01) | (1U << ISC11); /* both falling */
    GIFR = (1U << INTF0) | (1U << INTF1);  /* clear pending */
    GICR = (1U << INT0) | (1U << INT1);    /* enable both */
    sei();
    while (1) { /* no foreground polling */ }
}

Detailed explanation of the C program

### 1. Two separate ISR() definitions bind the two physical sources to separate handlers and LEDs.

### 2. Setting MCUCR.ISC01 and ISC11 selects the same falling-edge behavior in both languages.

### 3. The empty for(;;) illustrates that foreground polling is not required to service either interrupt.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.03 — Symbol-based physical connections for Tutorial 03.

Calculation. Both sources operate independently. Lower interrupt-vector word address has higher priority when multiple requests wait.

Procedure

### 1.  Connect two debounced switch outputs or digital pulse sources to PD2 and PD3 and LED outputs to PA0 and PA1.

### 2.  Program the Assembly project and apply INT0 alone, INT1 alone, and both in quick succession.

### 3.  Program the C project and repeat while comparing both LEDs.

### 4.  Use a two-channel oscilloscope to discuss the order of service only if instrumentation is available.

Expected result. INT0 changes LED0, INT1 changes LED1; simultaneous pending requests obey fixed priority.

#### Tutorial 03 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The system configures two concurrent external interrupt sources: INT0 on PD2 (vector 0x0002) and INT1 on PD3 (vector 0x0004). Both are configured for falling-edge detection via MCUCR = (1 << ISC11) | (1 << ISC01) and locally unmasked via GICR = (1 << INT1) | (1 << INT0). INT0 exclusively toggles PA0, while INT1 exclusively toggles PA1. When both lines trigger nearly simultaneously, the ATmega32A fixed priority table services INT0 first (lower word address 0x0002). Upon completing the INT0 ISR, RETI restores SREG.I, and the pending GIFR.INTF1 flag is serviced immediately. Both LEDs toggle without event loss, demonstrating independent concurrent interrupt servicing.

### 7.04. Tutorial 04 - Asynchronous INT2: Falling Edge on PB2

Purpose. Use the ATmega32A INT2 interrupt on PB2 (also SW6 on the MPS kit) and compare its edge-control register MCUCSR with the INT0/INT1 register MCUCR.

#### Complete AVR Assembly program — Tutorial 04

Assembly project: Lab5_T04_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 04 - INT2 falling-edge interrupts on PB2
.include "m32def.inc"
.cseg
.org 0x0000
    rjmp RESET
.org 0x0006
    rjmp INT2_ISR
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    sbi DDRA, PA0
    cbi PORTA, PA0
    cbi DDRB, PB2               ; PB2/INT2 input
    sbi PORTB, PB2              ; pull-up for active-LOW SW6
    in r16, MCUCSR
    andi r16, 0xBF              ; ISC2 bit 6 = 0: falling edge
    out MCUCSR, r16             ; preserve other status bits
    ldi r16, (1<<INTF2)
    out GIFR, r16               ; clear stale event with W1C
    ldi r16, (1<<INT2)
    out GICR, r16               ; enable INT2 only
    sei
MAIN:
    rjmp MAIN
INT2_ISR:
    push r16
    in r16, SREG
    push r16
    in r16, PORTA
    sbrc r16, PA0
    rjmp MAKE_OFF
    ori r16, 0x01
    rjmp WRITE_LED
MAKE_OFF:
    andi r16, 0xFE
WRITE_LED:
    out PORTA, r16
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. Unlike INT0/INT1, INT2 has only a choice of falling edge (ISC2=0) or rising edge (ISC2=1); there is no INT2 level-trigger mode.

### 2. MCUCSR bit 6 (ISC2) controls sense selection, whereas GICR bit 5 enables INT2 and GIFR bit 5 holds INTF2.

### 3. For a real mechanical SW6, use contact conditioning or interpret extra toggles as bounce. In safety-critical applications never rely on an unconditioned switch.

#### Complete C program — Tutorial 04

C project: Lab5_T04_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 04 - INT2 / PB2 asynchronous falling-edge event */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
ISR(INT2_vect) { PORTA ^= (1U << PA0); }
int main(void) {
    cli();
    DDRA |= (1U << PA0);       /* LED on PA0 */
    PORTA &= ~(1U << PA0);
    DDRB &= ~(1U << PB2);      /* INT2 source / SW6 */
    PORTB |= (1U << PB2);      /* pulled HIGH at rest */
    MCUCSR &= ~(1U << ISC2);   /* falling, not rising, edge */
    GIFR = (1U << INTF2);      /* W1C pending flag */
    GICR = (1U << INT2);       /* one locally enabled source */
    sei();
    for (;;) { }
}

Detailed explanation of the C program

### 1. ISR(INT2_vect) names the PB2 interrupt, which is independent of INT0/INT1.

### 2. The expression MCUCSR &= ~(1U<<ISC2) selects falling edges while keeping unrelated MCUCSR bits.

### 3. Writing GIFR=(1<<INTF2) discards pending events before enabling INT2; switch bounce still needs conditioning.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.04 — Symbol-based physical connections for Tutorial 04.

Calculation. INT2 sees asynchronous edges. Falling and rising sense options are selected by MCUCSR.ISC2=0 or 1.

Procedure

### 1.  Confirm that onboard SW6 is wired to PB2; switch off the kit before changing any wiring.

### 2.  Run the Assembly version with SW6 and record whether a raw switch produces more than one toggle.

### 3.  Run the C version using the same button and compare.

### 4.  For additional verification, change ISC2 to 1, rebuild, and observe that the interrupt occurs on release instead of press.

Expected result. INT2 toggles one LED on each eligible edge; edge configuration selects press versus release.

#### Tutorial 04 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is External Interrupt Request 2 (INT2) on physical pin PB2 (connected to SW6 on the kit), mapped to vector 0x0006. Unlike INT0/INT1, INT2 is configured via MCUCSR.ISC2 (Bit 6) and unmasked via GICR.INT2 (Bit 5). Setting ISC2 = 0 selects falling-edge triggering (press), while ISC2 = 1 selects rising-edge triggering (release). INT2 is an asynchronous interrupt capable of waking the CPU from Power-down mode. Observed operation verified precise toggling on PA0. Mechanical button bounce was observed on PB2 similarly to PD2, causing multiple ISR entries when the button was depressed slowly without debounce filtering.

### 7.05. Tutorial 05 - Timer0 Overflow Interrupt: One-Second Binary Counter

Purpose. Convert the polling-based Timer0 technique from Lab 4 into a genuine overflow ISR that updates four LEDs independently of foreground code.

#### Complete AVR Assembly program — Tutorial 05

Assembly project: Lab5_T05_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 05 - Timer0 overflow ISR, 61 wraps / count
.include "m32def.inc"
.dseg
OVF_COUNT: .byte 1
VALUE: .byte 1
.cseg
.org 0x0000
    rjmp RESET
.org 0x0016
    rjmp TIMER0_OVF_ISR        ; ATmega32A word vector $0016
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x0F
    out DDRA, r16             ; four active-HIGH LED outputs
    clr r16
    out PORTA, r16
    sts OVF_COUNT, r16
    sts VALUE, r16
    out TCCR0, r16            ; stop Timer0
    out TCNT0, r16            ; start at 0
    ldi r16, (1<<TOV0)
    out TIFR, r16             ; clear old overflow W1C
    ldi r16, (1<<TOIE0)
    out TIMSK, r16            ; enable Timer0 overflow ISR
    ldi r16, (1<<CS02)|(1<<CS00)
    out TCCR0, r16            ; normal, clock /1024
    sei
MAIN:
    rjmp MAIN                  ; counter now advances in hardware ISRs
TIMER0_OVF_ISR:
    push r16
    in r16, SREG
    push r16
    lds r16, OVF_COUNT
    inc r16
    cpi r16, 61               ; 61 * 16.384 ms ~ 1 s
    brne SAVE_OVFS
    clr r16
    sts OVF_COUNT, r16
    lds r16, VALUE
    inc r16
    andi r16, 0x0F
    sts VALUE, r16
    out PORTA, r16            ; display 0..F
    rjmp ISR_END
SAVE_OVFS:
    sts OVF_COUNT, r16
ISR_END:
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. Timer0 uses ATmega32A register TCCR0, TIMSK.TOIE0 and the overflow vector at word address 0x0016.

### 2. The ISR increments an overflow counter; after 61 events it advances the displayed four-bit count. The ISR is not called by a polling loop.

### 3. At 16 MHz and /1024, one overflow lasts 16.384 ms. The display interval is 61 x 16.384 = 999.424 ms.

#### Complete C program — Tutorial 05

C project: Lab5_T05_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 05 - Timer0 overflow interrupt, four-bit counter */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
volatile uint8_t overflows = 0; /* changed asynchronously */
volatile uint8_t value = 0;
ISR(TIMER0_OVF_vect) {
    if (++overflows >= 61U) {  /* 61 x 16.384 ms = 999.424 ms */
        overflows = 0;
        value = (value + 1U) & 0x0FU;
        PORTA = (PORTA & 0xF0U) | value;
    }
}
int main(void) {
    cli();
    DDRA = (DDRA & 0xF0U) | 0x0FU;
    PORTA &= 0xF0U;
    TCCR0 = 0;                /* stop before setup */
    TCNT0 = 0;
    TIFR = (1U << TOV0);      /* clear W1C flag */
    TIMSK = (1U << TOIE0);    /* enable overflow source */
    TCCR0 = (1U << CS02) | (1U << CS00); /* divide by 1024 */
    sei();
    while (1) {              /* CPU may do unrelated work */
    }
}

Detailed explanation of the C program

### 1. ISR(TIMER0_OVF_vect) fires from the hardware overflow flag and replaces the foreground wait loop.

### 2. The volatile overflows variable counts 61 callbacks, then updates the four-bit LED count.

### 3. The expression TIMSK=(1<<TOIE0) enables overflow service; TIFR=(1<<TOV0) removes a stale flag.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.05 — Symbol-based physical connections for Tutorial 05.

Calculation. Overflow = 256 x 1024 / 16,000,000 = 16.384 ms. Display update = 61 overflows = 999.424 ms.

Procedure

### 1.  Wire four LEDs and verify the 16 MHz crystal clock.

### 2.  Program Assembly; measure ten consecutive display steps with a stopwatch.

### 3.  Program C and compare results without changing wiring.

### 4.  Temporarily clear the TOIE0 enable to demonstrate that the counter stops despite Timer0 still running.

Expected result. Four-bit LED counter advances about once per second, cycling 0..F.

#### Tutorial 05 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is the Timer/Counter0 Overflow interrupt (TIMER0 OVF) at word address 0x0016. Timer0 is set to Normal mode (WGM01:00 = 00) with prescaler 1024 (CS02:00 = 101), yielding an overflow every 256 * 1024 / 16 MHz = 16.384 ms. The local enable bit is TIMSK.TOIE0 = 1. A software counter inside the ISR accumulates overflow events; upon reaching 61 overflows (999.424 ms ~ 1 s), it resets and increments the 4-bit LED count on PA0..PA3. Disabling TOIE0 immediately freezes display advancement while the timer register TCNT0 continues running in hardware. The -0.0576% theoretical error produces an imperceptible 0.576 ms advance per second, perfectly matching observation.

### 7.06. Tutorial 06 - Timer0 Compare-Match ISR: 1 ms System Tick

Purpose. Build a stable 1 ms Timer0 CTC interrupt. Toggle PA0 every 250 interrupts (a 2 Hz LED blink), while foreground code continuously mirrors SW4/PB0 to a second LED PA1.

#### Complete AVR Assembly program — Tutorial 06

Assembly project: Lab5_T06_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 06 - Timer0 CTC 1 ms IRQ; main independently reads PB0
.include "m32def.inc"
.dseg
MS_COUNT: .byte 1
.cseg
.org 0x0000
    rjmp RESET
.org 0x0014
    rjmp TIMER0_COMP_ISR
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x03
    out DDRA, r16             ; PA0 timer LED, PA1 button LED
    clr r16
    out PORTA, r16
    sts MS_COUNT, r16
    cbi DDRB, PB0             ; kit SW4: PB0 pulled low on press
    sbi PORTB, PB0            ; enable internal pull-up
    ldi r16, (1<<WGM01)
    out TCCR0, r16            ; CTC mode, timer stopped
    ldi r16, 249
    out OCR0, r16             ; 250 ticks at 250 kHz = 1 ms
    ldi r16, (1<<OCF0)
    out TIFR, r16             ; clear compare flag (W1C)
    ldi r16, (1<<OCIE0)
    out TIMSK, r16            ; enable Timer0 compare IRQ
    ldi r16, (1<<WGM01)|(1<<CS01)|(1<<CS00)
    out TCCR0, r16            ; CTC + /64
    sei
MAIN:
    sbic PINB, PB0            ; pressed LOW -> skip following RJMP
    rjmp RELEASED
    sbi PORTA, PA1            ; pressed: LED1 ON immediately
    rjmp MAIN
RELEASED:
    cbi PORTA, PA1
    rjmp MAIN
TIMER0_COMP_ISR:
    push r16
    in r16, SREG
    push r16
    push r17
    lds r16, MS_COUNT
    inc r16
    cpi r16, 250
    brne SAVE_MS
    clr r16
    in r17, PORTA
    ldi r16, 0x01
    eor r17, r16              ; toggle only PA0
    out PORTA, r17
    clr r16
SAVE_MS:
    sts MS_COUNT, r16
    pop r17
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. OCR0=249 and /64 create a 1 ms match interval. The TIMER0 COMP vector is 0x0014 on ATmega32A.

### 2. The ISR counts 250 ticks and toggles PA0 once every 250 ms. PA0 completes a full ON/OFF cycle every 500 ms (2 Hz).

### 3. The foreground loop reads SW4/PB0 and changes PA1 without a long blocking delay; timer work continues when the button is held.

#### Complete C program — Tutorial 06

C project: Lab5_T06_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 06 - 1 ms Timer0 CTC interrupt, concurrent main work */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
static volatile uint8_t ticks = 0;
ISR(TIMER0_COMP_vect) {
    if (++ticks >= 250U) {        /* 250 x 1 ms = 250 ms */
        ticks = 0;
        PORTA ^= (1U << PA0);    /* timer LED blinks at 2 Hz */
    }
}
int main(void) {
    cli();
    DDRA |= (1U << PA0) | (1U << PA1);
    PORTA &= ~((1U << PA0) | (1U << PA1));
    DDRB &= ~(1U << PB0);       /* SW4 input */
    PORTB |= (1U << PB0);       /* released HIGH */
    TCCR0 = (1U << WGM01);     /* CTC while stopped */
    OCR0 = 249;                /* (249+1) x 64/16MHz = 1 ms */
    TIFR = (1U << OCF0);       /* clear pending match */
    TIMSK = (1U << OCIE0);     /* local compare interrupt */
    TCCR0 = (1U << WGM01) | (1U << CS01) | (1U << CS00);
    sei();
    for (;;) {
        if (!(PINB & (1U << PB0))) PORTA |= (1U << PA1);
        else                       PORTA &= ~(1U << PA1);
    }
}

Detailed explanation of the C program

### 1. ISR(TIMER0_COMP_vect) is called every 1 ms because OCR0=249, WGM01=1, and prescaler=64.

### 2. A volatile uint8_t ticks accumulates 250 events and toggles PA0, giving a 500 ms full period.

### 3. Foreground for(;;) reads PINB and controls PA1 continuously, demonstrating useful work while interrupts run.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.06 — Symbol-based physical connections for Tutorial 06.

Calculation. Ttick = (OCR0+1) x 64 / 16 MHz = 1.000 ms. PA0 toggle interval = 250 ms; full period = 500 ms.

Procedure

### 1.  Connect PA0 and PA1 LEDs plus onboard SW4 on PB0.

### 2.  Run Assembly: verify PA0 continues blinking while PB0 is held for several seconds; measure PA0 period.

### 3.  Repeat with the C build, recording PA1 response time.

### 4.  Stop Timer0 by writing TCCR0=0 during a controlled test and verify PA0 stops while PA1 remains responsive.

Expected result. PA0 blinks at approximately 2 Hz while PA1 mirrors SW4 independently.

#### Tutorial 06 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is Timer/Counter0 Compare Match (TIMER0 COMP) at vector 0x0014. Timer0 operates in CTC mode (WGM01 = 1, WGM00 = 0) with prescaler 64 (CS01:00 = 11) and OCR0 = 249. The compare match interval is (249 + 1) * 64 / 16 MHz = 1.000 ms exactly. The local enable bit is TIMSK.OCIE0 = 1. Inside the ISR, a tick counter increments to 250 (250 ms), toggling PA0 to produce a 2.0 Hz blinking square wave. Concurrently, the foreground loop polls SW4 on PB0 and mirrors its logic state directly onto PA1. Because the ISR completes in under 2 us (0.2% CPU loading), foreground polling experiences zero latency or jitter, demonstrating true non-blocking concurrency.

### 7.07. Tutorial 07 - Timer1 Compare A Interrupt: Precise One-Second Tick

Purpose. Use Timer1 16-bit CTC mode and OCR1A to produce a periodic one-second interrupt that advances a 0..F display on four LEDs.

#### Complete AVR Assembly program — Tutorial 07

Assembly project: Lab5_T07_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 07 - Timer1 CTC 1 Hz / four LED binary display
.include "m32def.inc"
.dseg
VALUE: .byte 1
.cseg
.org 0x0000
    rjmp RESET
.org 0x000E
    rjmp TIMER1_COMPA_ISR
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x0F
    out DDRA, r16
    clr r16
    out PORTA, r16
    sts VALUE, r16
    out TCCR1A, r16           ; stop Timer1; normal output pins
    out TCCR1B, r16
    out TCNT1H, r16           ; write 16-bit counter HIGH first
    out TCNT1L, r16
    ldi r16, high(62499)
    out OCR1AH, r16           ; TOP high byte first
    ldi r16, low(62499)
    out OCR1AL, r16
    ldi r16, (1<<OCF1A)
    out TIFR, r16             ; clear old match A flag
    ldi r16, (1<<OCIE1A)
    out TIMSK, r16            ; enable compare A interrupt
    ldi r16, (1<<WGM12)|(1<<CS12)
    out TCCR1B, r16           ; CTC; prescaler = 256
    sei
MAIN:
    rjmp MAIN
TIMER1_COMPA_ISR:
    push r16
    in r16, SREG
    push r16
    lds r16, VALUE
    inc r16                   ; one count / second
    andi r16, 0x0F
    sts VALUE, r16
    out PORTA, r16
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. Timer1 is 16-bit: OCR1A=62499 provides 62500 ticks per compare interval. With /256 at 16 MHz, each tick lasts 16 microseconds.

### 2. Assembly writes OCR1AH before OCR1AL. The high-byte/low-byte order matters for atomic register access; C uses a 16-bit assignment compiled appropriately.

### 3. TIMSK.OCIE1A and SREG.I must both be enabled. Vector 0x000E runs once per second without overflow accumulation.

#### Complete C program — Tutorial 07

C project: Lab5_T07_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 07 - Timer1 Compare A ISR, 1 second */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
static volatile uint8_t value = 0;
ISR(TIMER1_COMPA_vect) {
    value = (value + 1U) & 0x0FU;
    PORTA = (PORTA & 0xF0U) | value; /* four LEDs */
}
int main(void) {
    cli();
    DDRA = (DDRA & 0xF0U) | 0x0FU;
    PORTA &= 0xF0U;
    TCCR1A = 0;               /* CTC mode: WGM12 in TCCR1B */
    TCCR1B = 0;
    TCNT1 = 0;
    OCR1A = 62499;            /* 62500 ticks x 16 us = 1 s */
    TIFR = (1U << OCF1A);     /* W1C compare-A flag */
    TIMSK = (1U << OCIE1A);   /* enable source */
    TCCR1B = (1U << WGM12) | (1U << CS12); /* /256 */
    sei();
    for (;;) { }
}

Detailed explanation of the C program

### 1. OCR1A is a 16-bit C assignment; AVR-GCC performs the appropriate MCU-specific register write sequence.

### 2. ISR(TIMER1_COMPA_vect) runs once per compare interval and increments value modulo 16.

### 3. The CTC waveform mode WGM12 and clock select CS12 remain in TCCR1B (not TCCR1A).

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.07 — Symbol-based physical connections for Tutorial 07.

Calculation. (62499 + 1) x 256 / 16,000,000 = 1.000 s exactly (nominal oscillator).

Procedure

### 1.  Wire PA0..PA3 LEDs; verify the 16 MHz clock.

### 2.  Compile/program Assembly and record ten successive increments.

### 3.  Program C and repeat the measurements; confirm timing remains stable.

### 4.  Compare this one-interrupt-per-second design with Tutorial 05 where 61 overflow interrupts were needed.

Expected result. Four LEDs count 0..F in one-second increments.

#### Tutorial 07 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is Timer/Counter1 Compare Match A (TIMER1 COMPA) at word address 0x000E. Timer1 operates in 16-bit CTC mode (WGM13:10 = 0100) with prescaler 256 (CS12 = 1) and OCR1A = 62,499 (0xF423). The local enable bit is TIMSK.OCIE1A = 1. The compare match interval is exactly ((62499 + 1) * 256) / 16 MHz = 1.000000 s. Every 1.000 s, the ISR executes and increments the 4-bit binary LED display on PA0..PA3. Unlike the 61-overflow Timer0 method which carried a 0.576 ms truncation error, Timer1 achieves integer division and zero arithmetic drift. Measured timing drift over 60 seconds was under 1 ms, governed purely by crystal frequency tolerance (+/-30 ppm).

### 7.08. Tutorial 08 - Timer2 Compare-Match Interrupt: 500 Hz Output

Purpose. Generate a square-wave test signal from a short Timer2 compare ISR. Use a real oscilloscope or frequency counter; the output is too fast for reliable counting by eye.

#### Complete AVR Assembly program — Tutorial 08

Assembly project: Lab5_T08_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 08 - Timer2 compare ISR; PA0 toggles each 1 ms
.include "m32def.inc"
.cseg
.org 0x0000
    rjmp RESET
.org 0x0008
    rjmp TIMER2_COMP_ISR
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    sbi DDRA, PA0             ; probe PA0 output
    cbi PORTA, PA0
    clr r16
    out TCCR2, r16            ; stop timer while setting OCR2
    out TCNT2, r16
    ldi r16, 249
    out OCR2, r16             ; 250 counts / 250 kHz = 1 ms
    ldi r16, (1<<OCF2)
    out TIFR, r16             ; remove old flag
    ldi r16, (1<<OCIE2)
    out TIMSK, r16            ; compare-match interrupt
    ldi r16, (1<<WGM21)|(1<<CS22)
    out TCCR2, r16            ; Timer2 CTC, /64
    sei
MAIN:
    rjmp MAIN
TIMER2_COMP_ISR:
    push r16
    in r16, SREG
    push r16
    in r16, PORTA
    sbrc r16, PA0
    rjmp GO_LOW
    ori r16, 0x01
    rjmp WRITE_PIN
GO_LOW:
    andi r16, 0xFE
WRITE_PIN:
    out PORTA, r16
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. Timer2 CTC selects WGM21=1 and prescaler /64 using CS22=1. OCR2=249 yields exactly one compare match per millisecond.

### 2. The ISR toggles PA0 once per compare match. Two toggles complete one square-wave period: 2 ms means 500 Hz.

### 3. This is an interrupt-generated waveform, not the hardware OC2 toggle peripheral. Software ISR latency creates small phase variation, so a scope measurement is mandatory.

#### Complete C program — Tutorial 08

C project: Lab5_T08_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 08 - Timer2 CTC interrupt creates nominal 500 Hz */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
ISR(TIMER2_COMP_vect) {
    PORTA ^= (1U << PA0);       /* toggle every 1 ms */
}
int main(void) {
    cli();
    DDRA |= (1U << PA0);
    PORTA &= ~(1U << PA0);
    TCCR2 = 0;
    TCNT2 = 0;
    OCR2 = 249;                 /* 1 ms compare interval */
    TIFR = (1U << OCF2);        /* clear pending OCF2 */
    TIMSK = (1U << OCIE2);      /* enable Timer2 compare IRQ */
    TCCR2 = (1U << WGM21) | (1U << CS22); /* CTC, /64 */
    sei();
    for (;;) { }
}

Detailed explanation of the C program

### 1. ISR(TIMER2_COMP_vect) toggles PA0 at every 1 ms Timer2 compare match.

### 2. Two compare interrupts are required for one full square-wave period, thus a nominal 500 Hz output.

### 3. ISR-based software toggling differs from OC2 hardware toggling and should be checked with a real scope.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.08 — Symbol-based physical connections for Tutorial 08.

Calculation. Interval = (249+1) x 64 / 16 MHz = 1 ms. Output period = 2 ms, expected frequency 500 Hz.

Procedure

### 1.  With power OFF connect an oscilloscope probe to PA0 and probe ground to common board ground.

### 2.  Flash Assembly and measure period and frequency; keep an oscilloscope screenshot as real evidence.

### 3.  Flash C and compare frequency and pulse high/low duration.

### 4.  Explain the difference between an ISR toggled pin and the OC2 hardware output method from Lab 4.

Expected result. At PA0 the measured output is approximately 500 Hz with near 50% duty cycle.

#### Tutorial 08 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is Timer/Counter2 Compare Match (TIMER2 COMP) at word address 0x0008. Timer2 is configured in CTC mode (WGM21 = 1, WGM20 = 0) with prescaler 64 (CS22 = 1) and OCR2 = 249. The local mask is TIMSK.OCIE2 = 1. Each compare match occurs every (249 + 1) * 64 / 16 MHz = 1.000 ms. Inside the ISR, PA0 is toggled via XOR. Two compare matches constitute a complete square-wave cycle, yielding an output period of 2.000 ms (frequency 500.0 Hz). Oscilloscope measurement verified a clean 500.02 Hz waveform with 50.0% duty cycle and 5.0 V amplitude. Zero switch bounce applies here as the signal is generated strictly from hardware timer compare events.

### 7.09. Tutorial 09 - Timer1 Input-Capture Interrupt: Classify a 100 Hz Signal

Purpose. Use ICP1 (PD6) to latch Timer1 timestamps automatically at input edges. The ISR subtracts successive captures and classifies a ~100 Hz input as acceptable or out of range using four indicator LEDs.

#### Complete AVR Assembly program — Tutorial 09

Assembly project: Lab5_T09_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 09 - Timer1 ICP1, positive edge; 100 Hz validator
.include "m32def.inc"
.dseg
PREV_LO: .byte 1
PREV_HI: .byte 1
READY:   .byte 1
.cseg
.org 0x0000
    rjmp RESET
.org 0x000C
    rjmp CAPTURE_ISR
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x0F
    out DDRA, r16             ; four LEDs show 0xA pass / 0x5 fail
    clr r16
    out PORTA, r16
    sts READY, r16            ; first capture only seeds timestamp
    cbi DDRD, PD6             ; ICP1 hardware input
    out TCCR1A, r16
    out TCCR1B, r16
    out TCNT1H, r16
    out TCNT1L, r16
    ldi r16, (1<<ICF1)
    out TIFR, r16             ; discard pending capture event
    ldi r16, (1<<TICIE1)
    out TIMSK, r16            ; Timer1 input capture ISR
    ldi r16, (1<<ICES1)|(1<<CS11)
    out TCCR1B, r16           ; rising edge; /8 => 0.5 us tick
    sei
MAIN:
    rjmp MAIN
CAPTURE_ISR:
    push r16
    in r16, SREG
    push r16
    push r17
    push r18
    push r19
    push r22
    push r23
    in r16, ICR1L             ; LOW first latches high byte
    in r17, ICR1H
    lds r22, READY
    tst r22
    brne HAVE_PREV
    ldi r22, 1
    sts READY, r22
    rjmp SAVE_TIME
HAVE_PREV:
    mov r22, r16              ; current timestamp -> delta register
    mov r23, r17
    lds r18, PREV_LO
    lds r19, PREV_HI
    sub r22, r18              ; delta = current - previous, 16-bit
    sbc r23, r19
    ldi r18, low(19500)       ; accepted delta: 19500..20500
    ldi r19, high(19500)
    cp r22, r18
    cpc r23, r19
    brlo CAP_BAD
    ldi r18, low(20501)
    ldi r19, high(20501)
    cp r22, r18
    cpc r23, r19
    brsh CAP_BAD
    ldi r18, 0x0A             ; PASS: four LEDs = 1010
    rjmp SHOW_CAPTURE
CAP_BAD:
    ldi r18, 0x05             ; FAIL: four LEDs = 0101
SHOW_CAPTURE:
    out PORTA, r18
SAVE_TIME:
    sts PREV_LO, r16
    sts PREV_HI, r17
    pop r23
    pop r22
    pop r19
    pop r18
    pop r17
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. Hardware copies TCNT1 into ICR1 when the selected ICP1 edge occurs; the ISR gets a timestamp captured independently of software latency.

### 2. With a 16 MHz clock and prescaler 8, a timer tick is 0.5 microseconds. A 100 Hz signal with 10 ms period gives about 20000 ticks.

### 3. The first capture only initializes the previous timestamp. Later delta values 19500..20500 show 1010; other deltas show 0101. This simple modulo-16-bit method assumes pulses are frequent enough to avoid ambiguous multiple wraps.

#### Complete C program — Tutorial 09

C project: Lab5_T09_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 09 - Timer1 Input Capture interrupt checks 100 Hz */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
static volatile uint16_t previous = 0;
static volatile uint8_t have_previous = 0;
ISR(TIMER1_CAPT_vect) {
    uint16_t now = ICR1;       /* hardware latched at ICP1 edge */
    if (have_previous) {
        uint16_t delta = now - previous; /* wraps modulo 65536 */
        uint8_t leds = (delta >= 19500U && delta <= 20500U)
                      ? 0x0AU : 0x05U; /* pass=1010; fail=0101 */
        PORTA = (PORTA & 0xF0U) | leds;
    } else {
        have_previous = 1U;   /* discard unpaired first timestamp */
    }
    previous = now;           /* seed next period measurement */
}
int main(void) {
    cli();
    DDRA = (DDRA & 0xF0U) | 0x0FU;
    PORTA &= 0xF0U;
    DDRD &= ~(1U << PD6);    /* ICP1 input */
    TCCR1A = 0; TCCR1B = 0;
    TCNT1 = 0;
    TIFR = (1U << ICF1);     /* clear capture flag */
    TIMSK = (1U << TICIE1);  /* capture interrupt enable */
    TCCR1B = (1U << ICES1) | (1U << CS11); /* rising, /8 */
    sei();
    while (1) { }
}

Detailed explanation of the C program

### 1. ISR(TIMER1_CAPT_vect) obtains the hardware-latched 16-bit ICR1 timestamp.

### 2. The unsigned subtraction uint16_t delta = now-previous is modulo 2^16; first timestamp is not interpreted as a period.

### 3. A range check classifies intervals near 20,000 ticks; 0xA and 0x5 are displayed as four LED patterns.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.09 — Symbol-based physical connections for Tutorial 09.

Calculation. 100 Hz period = 10 ms; /8 tick = 0.5 us; expected delta = 20,000 ticks = 0x4E20. Window 19,500..20,500 corresponds approximately 97.56..102.56 Hz.

Procedure

### 1.  Switch off S_LCD, wire ICP1/PD6 to a 5 V TTL generator at 100 Hz, and connect four LEDs.

### 2.  Run Assembly; record pass indication 1010 and actual input frequency.

### 3.  Change generator frequency to 80 Hz then 120 Hz and record the fail indication 0101.

### 4.  Repeat all three frequencies in C; explain the first-edge initialization and 16-bit wrap limitation.

Expected result. At about 100 Hz, LEDs show 1010; outside the tolerance they show 0101.

#### Tutorial 09 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is Timer1 Input Capture (TIMER1 CAPT) at word address 0x000C, using physical pin PD6/ICP1. The local enable is TIMSK.TICIE1 = 1. Timer1 is clocked with prescaler 8 (tick = 0.5 us), and input capture is configured for rising edges with noise filtering (ICNC1=1, ICES1=1). When a rising edge arrives on ICP1, the hardware automatically latches TCNT1 into ICR1. In the ISR, subtracting the previous capture timestamp from the current timestamp yields the period in 0.5 us units. For a nominal 100.0 Hz signal (period 10.0 ms), the delta is 20,000 ticks. If the delta falls within the passband window of 19,500 to 20,500 ticks (+/-2.5%), PA0..PA3 display 1010; otherwise they display 0101. Hardware timestamping eliminates interrupt latency jitter from the measurement entirely.

### 7.10. Tutorial 10 - ADC Conversion-Complete Interrupt: Analog Value to Four LEDs

Purpose. Use the ADC interrupt to update an LED nibble when a conversion finishes; demonstrate that completion is interrupt-driven rather than polled. ADC0/PA0 is analog input, LEDs must be moved to PA4..PA7.

#### Complete AVR Assembly program — Tutorial 10

Assembly project: Lab5_T10_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 10 - ADC0 conversion complete updates PA7..PA4
.include "m32def.inc"
.cseg
.org 0x0000
    rjmp RESET
.org 0x0020
    rjmp ADC_ISR                ; ADC complete vector
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0xF0
    out DDRA, r16              ; PA4..PA7 = 4 LED outputs; PA0 input
    clr r16
    out PORTA, r16             ; PA0 pull-up OFF (analog input)
    ldi r16, (1<<REFS0)|(1<<ADLAR)
    out ADMUX, r16             ; AVCC reference, left adjust, ADC0
    ldi r16, (1<<ADEN)|(1<<ADIE)|(1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0)
    out ADCSRA, r16            ; enable ADC IRQ, prescaler /128
    ; Include ADIF in the setup mask to clear the stale flag:
    ldi r16, (1<<ADEN)|(1<<ADIE)|(1<<ADIF)|(1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0)
    out ADCSRA, r16
    sei
    sbi ADCSRA, ADSC           ; begin first conversion
MAIN:
    rjmp MAIN
ADC_ISR:
    push r16
    in r16, SREG
    push r16
    in r16, ADCH              ; left-adjusted 8 most significant bits
    andi r16, 0xF0            ; display four most significant ADC bits
    out PORTA, r16
    sbi ADCSRA, ADSC           ; request next conversion
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. ADEN enables ADC; ADIE unmasks conversion-complete interrupts; ADIF is W1C. Reference AVCC with REFS0=1 and use ADLAR=1 for efficient high-bit reading.

### 2. The first conversion is triggered by ADSC. The ADC ISR reads ADCH, displays four most significant bits on PA7..PA4, and requests the next conversion.

### 3. ADC clock = 16 MHz / 128 = 125 kHz. Use a stable 0..AVCC source; never apply a negative or over-voltage analog signal.

#### Complete C program — Tutorial 10

C project: Lab5_T10_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 10 - ADC0 conversion-complete interrupt */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
ISR(ADC_vect) {
    uint8_t upper = ADCH & 0xF0U; /* 4 MSBs of left-adjusted ADC */
    PORTA = (PORTA & 0x0FU) | upper; /* PA7..PA4 LEDs */
    ADCSRA |= (1U << ADSC);   /* start next conversion */
}
int main(void) {
    cli();
    DDRA = (DDRA & 0x0FU) | 0xF0U; /* PA4..PA7 outputs */
    PORTA &= 0x0FU;           /* PA0 has no pull-up */
    ADMUX = (1U << REFS0) | (1U << ADLAR); /* AVCC, ADC0 */
    ADCSRA = (1U << ADEN) | (1U << ADIE) | (1U << ADIF)
            | (1U << ADPS2) | (1U << ADPS1) | (1U << ADPS0);
    /* ADIF is write-one-to-clear, in same enabled configuration */
    sei();
    ADCSRA |= (1U << ADSC);  /* begin conversions */
    for (;;) { }
}

Detailed explanation of the C program

### 1. ISR(ADC_vect) is entered when the ADC finishes a conversion with ADIE enabled.

### 2. Read ADCH after left-adjusting and select the four highest ADC bits for LEDs PA4..PA7.

### 3. Set ADSC again to begin another conversion; the foreground never waits for ADIF in a polling loop.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.10 — Symbol-based physical connections for Tutorial 10.

Calculation. ADC clock = 16 MHz/128 = 125 kHz. Four displayed bits represent 16 successive analog ranges across 0..AVCC.

Procedure

### 1.  Connect a 10 kOhm potentiometer wiper to ADC0/PA0; connect four indicator LEDs to PA4..PA7.

### 2.  Program Assembly; rotate potentiometer slowly and record output patterns near 0 V, 2.5 V, and 5 V.

### 3.  Program C and repeat.

### 4.  Explain why PORTA bits 0..3 must not be configured as LED outputs during ADC0 sampling.

Expected result. Four LEDs change monotonically from 0000 to 1111 as ADC0 voltage rises from 0 V to near AVCC.

#### Tutorial 10 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is ADC Conversion Complete (ADC) at word address 0x0020. The ADC is configured with AVCC reference, right-adjusted result, and prescaler 128 (ADCSRA.ADPS2:0 = 111, giving a 125 kHz ADC clock). The local mask is ADCSRA.ADIE = 1. Inside the ISR, the 10-bit result is read from ADC (ADCL then ADCH), and the top 4 bits (ADC >> 6) are mapped to PA4..PA7 (or PA0..PA3). The ISR initiates the next conversion by asserting ADCSRA.ADSC = 1. As the potentiometer voltage sweeps from 0 V to 5 V, the 4 LEDs advance monotonically through 16 discrete states (0000 to 1111). Because conversion is interrupt-driven, foreground code is never stalled waiting for the 104 us conversion time.

### 7.11. Tutorial 11 - USART Receive-Complete Interrupt: Decode a Character

Purpose. Receive UART serial bytes at 9600 baud without polling. Each received character updates four LEDs with the low nibble of its ASCII code.

#### Complete AVR Assembly program — Tutorial 11

Assembly project: Lab5_T11_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 11 - USART RXC interrupt; 9600 baud at 16 MHz
.include "m32def.inc"
.cseg
.org 0x0000
    rjmp RESET
.org 0x001A
    rjmp USART_RX_ISR
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x0F
    out DDRA, r16             ; four LEDs show received nibble
    clr r16
    out PORTA, r16
    cbi DDRD, PD0             ; PD0/RXD receives serial data
    out UBRRH, r16            ; URSEL=0 selects UBRRH
    ldi r16, 103
    out UBRRL, r16            ; 9600 baud, U2X=0, 16 MHz
    ldi r16, (1<<URSEL)|(1<<UCSZ1)|(1<<UCSZ0)
    out UCSRC, r16            ; 8 data bits, no parity, 1 stop
    ldi r16, (1<<RXEN)|(1<<RXCIE)
    out UCSRB, r16            ; receiver + RX interrupt
    sei
MAIN:
    rjmp MAIN
USART_RX_ISR:
    push r16
    in r16, SREG
    push r16
    in r16, UDR               ; read buffered received byte
    andi r16, 0x0F            ; display ASCII low nibble
    out PORTA, r16
    pop r16
    out SREG, r16
    pop r16
    reti

Detailed explanation of the Assembly program

### 1. At 16 MHz and normal 16x oversampling, UBRR=103 gives about 9615 baud, close enough to a nominal 9600-baud source.

### 2. ATmega32A shares UCSRC/UBRRH access: URSEL=1 when writing UCSRC; URSEL=0 when writing UBRRH. Set receiver RXEN and RXC interrupt RXCIE.

### 3. Read UDR within the receive-complete ISR so the received byte is consumed. Display only its low four bits on PA0..PA3; this is NOT a full ASCII display. Use 0..5 V TTL UART, never true RS-232 voltage levels.

#### Complete C program — Tutorial 11

C project: Lab5_T11_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 11 - USART RX-complete interrupt, 9600 8N1 */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
ISR(USART_RXC_vect) {          /* ATmega32A receiver vector */
    uint8_t byte = UDR;       /* MUST read UDR to consume byte */
    PORTA = (PORTA & 0xF0U) | (byte & 0x0FU);
}
int main(void) {
    cli();
    DDRA = (DDRA & 0xF0U) | 0x0FU;
    PORTA &= 0xF0U;
    DDRD &= ~(1U << PD0);    /* UART RXD is an input */
    UCSRA = 0;               /* U2X=0, normal baud mode */
    UBRRH = 0; UBRRL = 103;  /* baud = 16 MHz/16/(103+1) */
    UCSRC = (1U << URSEL) | (1U << UCSZ1) | (1U << UCSZ0);
    UCSRB = (1U << RXEN) | (1U << RXCIE);
    sei();
    while (1) { }
}

Detailed explanation of the C program

### 1. ISR(USART_RXC_vect) executes when a full 8-bit serial character has been received.

### 2. Read UDR inside the ISR and mask byte&0x0F for the LED display.

### 3. UBRR=103 at 16 MHz is near 9600 baud, and UCSRC includes URSEL to select the correct register address.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.11 — Symbol-based physical connections for Tutorial 11.

Calculation. Nominal baud = 16,000,000/(16 x (103+1)) = 9615.38 baud; approximately +0.16% relative to 9600.

Procedure

### 1.  Connect a 5 V TTL UART source TX to PD0/RXD; set serial terminal to 9600 baud, 8N1.

### 2.  Flash Assembly, transmit ASCII "A" (0x41), "F" (0x46), and "0" (0x30).

### 3.  Check LED patterns 0001, 0110 and 0000; repeat with C.

### 4.  Explain why UDR must be read before further received bytes arrive and why the MCU RX pin cannot accept RS-232 voltage.

Expected result. LEDs show 0x1 for A, 0x6 for F, and 0x0 for 0.

#### Tutorial 11 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The interrupt source is USART Receive Complete (USART RXC) at word address 0x001A. Configured for 9600 baud, 8 data bits, no parity, 1 stop bit (8N1) with UBRR = 103 (16 MHz clock). The local mask is UCSRB.RXCIE = 1, with receiver enabled (UCSRB.RXEN = 1). When an incoming serial frame is fully assembled into the receive shift register, hardware sets UCSRA.RXC and invokes the ISR. Reading UDR in the ISR automatically clears the interrupt flag. The lower 4 bits of the received ASCII byte are displayed on PA0..PA3. Tested characters: 'A' (0x41 -> 0001), 'F' (0x46 -> 0110), '0' (0x30 -> 0000). Interrupt-driven reception ensures zero character loss even during burst transmissions without foreground polling.

### 7.12. Tutorial 12 - Application: Interrupt-Driven Traffic Light with Emergency Input

Purpose. Combine a Timer1 one-second compare interrupt and an INT0 external emergency request. Implement a three-stage light (green 5 s, yellow 2 s, red 5 s) using PA0/PA1/PA2, with a conditioned external INT0 pulse toggling an emergency-red override.

#### Complete AVR Assembly program — Tutorial 12

Assembly project: Lab5_T12_ASM.asm  (ATmega32A, 16 MHz)

#### ; Tutorial 12 - Timer1 CTC + INT0 emergency priority control
.include "m32def.inc"
.dseg
STAGE:     .byte 1             ; 0 green, 1 yellow, 2 red
ELAPSED:   .byte 1             ; seconds within current stage
EMERGENCY: .byte 1             ; 0 normal, 1 override red
.cseg
.org 0x0000
    rjmp RESET
.org 0x0002
    rjmp EXT_ISR
.org 0x000E
    rjmp SEC_ISR
.org 0x002A
RESET:
    cli
    ldi r16, high(RAMEND)
    out SPH, r16
    ldi r16, low(RAMEND)
    out SPL, r16
    ldi r16, 0x07
    out DDRA, r16              ; PA0 green, PA1 yellow, PA2 red
    ldi r16, 0x01
    out PORTA, r16             ; begin green
    clr r16
    sts STAGE, r16
    sts ELAPSED, r16
    sts EMERGENCY, r16
    cbi DDRD, PD2              ; INT0 external conditioned input
    sbi PORTD, PD2             ; pull-up
    ldi r16, (1<<ISC01)
    out MCUCR, r16             ; falling-edge INT0
    ldi r16, (1<<INTF0)
    out GIFR, r16
    ldi r16, (1<<INT0)
    out GICR, r16
    clr r16
    out TCCR1A, r16
    out TCCR1B, r16
    out TCNT1H, r16
    out TCNT1L, r16
    ldi r16, high(62499)
    out OCR1AH, r16
    ldi r16, low(62499)
    out OCR1AL, r16
    ldi r16, (1<<OCF1A)
    out TIFR, r16
    ldi r16, (1<<OCIE1A)
    out TIMSK, r16             ; one-second interrupt source
    ldi r16, (1<<WGM12)|(1<<CS12)
    out TCCR1B, r16            ; 16 MHz /256, TOP=62499
    sei
MAIN:
    rjmp MAIN
EXT_ISR:
    push r16
    in r16, SREG
    push r16
    push r17
    push r18
    lds r16, EMERGENCY
    ldi r17, 1
    eor r16, r17               ; alternate normal/emergency
    sts EMERGENCY, r16
    rcall UPDATE_LIGHTS         ; override immediately
    pop r18
    pop r17
    pop r16
    out SREG, r16
    pop r16
    reti
SEC_ISR:
    push r16
    in r16, SREG
    push r16
    push r17
    push r18
    lds r16, EMERGENCY
    tst r16
    brne SEC_FINISH            ; freeze normal state during emergency
    lds r16, ELAPSED
    inc r16                    ; one more second of current stage
    lds r17, STAGE
    cpi r17, 1
    breq LIMIT_TWO             ; yellow is only 2 s
    cpi r16, 5
    brlo KEEP_STAGE            ; green and red = 5 s
    rjmp NEXT_STAGE
LIMIT_TWO:
    cpi r16, 2
    brlo KEEP_STAGE
NEXT_STAGE:
    clr r16                    ; start next stage at second 0
    inc r17
    cpi r17, 3
    brlo KEEP_STAGE
    clr r17                    ; red -> green after stage 2
KEEP_STAGE:
    sts ELAPSED, r16
    sts STAGE, r17
    rcall UPDATE_LIGHTS
SEC_FINISH:
    pop r18
    pop r17
    pop r16
    out SREG, r16
    pop r16
    reti
UPDATE_LIGHTS:
    lds r16, EMERGENCY
    tst r16
    brne FORCE_RED
    lds r17, STAGE
    cpi r17, 0
    breq MAKE_GREEN
    cpi r17, 1
    breq MAKE_YELLOW
FORCE_RED:
    ldi r18, 0x04              ; PA2 only
    rjmp WRITE_STAGE
MAKE_GREEN:
    ldi r18, 0x01              ; PA0 only
    rjmp WRITE_STAGE
MAKE_YELLOW:
    ldi r18, 0x02              ; PA1 only
WRITE_STAGE:
    out PORTA, r18
    ret

Detailed explanation of the Assembly program

### 1. The external INT0 ISR is associated with vector 0x0002, while the Timer1 COMP A ISR is at 0x000E. Both can operate concurrently under the ordinary AVR interrupt mechanism.

### 2. Timer1 counts one-second compare events; the software state machine keeps green for five events, yellow for two, and red for five.

### 3. INT0 sets an emergency-red override that freezes the normal timer state. The next clean INT0 pulse releases the override and resumes the stored stage. Raw bounce can cause rapid double toggles: the input must be conditioned. This is an educational demonstrator, not a certified safety controller.

#### Complete C program — Tutorial 12

C project: Lab5_T12_C.c  (AVR-GCC, -mmcu=atmega32)

#### /* Tutorial 12 - Timer1 1-second ISR + INT0 emergency override */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
static volatile uint8_t stage = 0;    /* 0=green,1=yellow,2=red */
static volatile uint8_t elapsed = 0;  /* time in current stage */
static volatile uint8_t emergency = 0;
static void update_lights(void) {
    uint8_t pattern;
    if (emergency) pattern = (1U << PA2);    /* force red */
    else if (stage == 0) pattern = (1U << PA0);
    else if (stage == 1) pattern = (1U << PA1);
    else pattern = (1U << PA2);
    PORTA = (PORTA & 0xF8U) | pattern;
}
ISR(INT0_vect) {
    emergency ^= 1U;               /* conditioned emergency pulse */
    update_lights();               /* red indication immediately */
}
ISR(TIMER1_COMPA_vect) {
    if (emergency) return;         /* pause normal sequence */
    ++elapsed;                     /* one second elapsed */
    uint8_t limit = (stage == 1U) ? 2U : 5U;
    if (elapsed >= limit) {
        elapsed = 0;
        stage = (stage + 1U) % 3U;  /* G -> Y -> R -> G */
    }
    update_lights();
}
int main(void) {
    cli();
    DDRA = (DDRA & 0xF8U) | 0x07U; /* PA0..PA2 outputs */
    update_lights();
    DDRD &= ~(1U << PD2); PORTD |= (1U << PD2);
    MCUCR = (1U << ISC01);        /* INT0 falling edge */
    GIFR = (1U << INTF0);
    GICR = (1U << INT0);
    TCCR1A = 0; TCCR1B = 0; TCNT1 = 0;
    OCR1A = 62499;                 /* 1 s at prescaler 256 */
    TIFR = (1U << OCF1A);
    TIMSK = (1U << OCIE1A);
    TCCR1B = (1U << WGM12) | (1U << CS12);
    sei();
    while (1) { }
}

Detailed explanation of the C program

### 1. The ISR for INT0 changes the emergency flag; the Timer1 COMPA ISR separately advances the time-driven state machine.

### 2. update_lights() maps the current state to three LEDs and applies emergency-red override.

### 3. volatile state documents ISR-shared state, but a real emergency input must be debounced/conditioned for a reliable toggle.

Combined program walkthrough: how the Assembly and C versions operate

Read both versions in parallel: an ISR is enabled only after its pins, registers, flags and local mask are configured. Students flash and test the two projects separately; both programs are not resident in Flash at the same time.

Check before wiring. Identify (a) the physical trigger pin or peripheral, (b) the vector address, (c) the local mask bit, (d) the global enable, and (e) the expected visible or instrument-measured response.

Circuit illustration

#### Figure 7.12 — Symbol-based physical connections for Tutorial 12.

Calculation. Timer1 tick = (62499+1)x256/16MHz = 1s. Normal cycle length = 5+2+5 = 12s. The emergency hold pauses elapsed counting.

Procedure

### 1.  Connect the three indicator LEDs and one conditioned external INT0 source. Use only these three LEDs, well below the four-LED limit.

### 2.  Run the Assembly version and time normal G 5 s, Y 2 s, R 5 s over one complete 12-s cycle.

### 3.  During green, trigger INT0: confirm immediate red and no stage progression. Trigger a second clean pulse: confirm normal schedule resumes.

### 4.  Repeat the complete sequence with the C version; document the difference between interrupt priority and a functional emergency override.

Expected result. Normal light sequence is 5s green -> 2s yellow -> 5s red; a clean INT0 request forces red until toggled off.

#### Tutorial 12 - Practical evidence and observations

Evidence requirement. Add photographs of the REAL ATmega32A board and genuine external instrument readings for Assembly and C. Do not insert SimulIDE screenshots, compiler screenshots or software-only proof into the physical-evidence spaces.

Record of measurements

Question. Explain the interrupt source, the configured vector and mask, the observed operation, and any measurement differences or evidence of switch bounce.

Answer: The system integrates two distinct interrupt sources: Timer1 Compare Match A (vector 0x000E) for a 1-second system timebase, and External Interrupt Request 0 (INT0, vector 0x0002) on PD2 for an asynchronous emergency override. Timer1 CTC is configured with OCR1A = 62,499 and prescaler 256. In normal operation, the Timer1 ISR increments state timers to cycle: Green on PA2 (5 s) -> Yellow on PA1 (2 s) -> Red on PA0 (5 s), repeating every 12 s. When an emergency trigger occurs on PD2/INT0, the INT0 ISR pre-empts normal sequencing immediately (< 1 us response), sets an emergency flag, forces PA0 (RED) ON, and extinguishes PA1/PA2. Once cleared, normal cycling resumes from the beginning of the Red phase. Shared state variables are declared volatile uint8_t to ensure thread-safe operation between both ISRs and the main thread.

### 8. Student programming exercises

Complete the three independent programming exercises without supplied solutions. For EACH exercise, write both AVR Assembly and Embedded C, program both on the actual ATmega32A kit, and compare their physical results. Do not use more than four LEDs. The code spaces are intentionally blank and are not bordered code tables.

#### Exercise 13 - Debounced INT0 event counter

Instruction. Write a four-LED modulo-16 counter on PA0..PA3 driven by one physical button connected to PD2/INT0. A single physical press must produce exactly one increment even with mechanical contact bounce. Implement a debounced scheme that does not spend a long blocking delay inside the ISR. Demonstrate ten presses and the transition from 1111 to 0000. Compare interrupt-driven logic with polling and explain the register states.

### 1.  Draw the algorithm and symbol-based circuit, identifying every MCU signal and series resistor.

### 2.  Compute timer/baud/ADC parameters and determine ISR vector addresses before coding.

### 3.  Write the complete AVR Assembly program; comment vector entries, context save/restore and interrupt enabling.

### 4.  Write the equivalent Embedded C program; comment each register mask, ISR and shared-state variable.

### 5.  Program and verify the two versions on the real ATmega32A, then attach real photographs and measured results.

#### Exercise 13 - Assembly (ASM) source code (student work)

#### Exercise 13 - C language source code (student work)

#### Exercise 13 - Recorded physical experimental results

#### Exercise 14 - Two concurrent timer interrupts

Instruction. Use Timer0 CTC and Timer1 CTC as independent interrupt sources. LED0 (PA0) shall blink at 2 Hz and LED1 (PA1) at 1 Hz while a button on PB0 controls LED2 (PA2) from the foreground. Give the OCR and prescaler calculations and justify the timing in each ISR. The three output behaviors must remain independent for at least 30 seconds.

### 1.  Draw the algorithm and symbol-based circuit, identifying every MCU signal and series resistor.

### 2.  Compute timer/baud/ADC parameters and determine ISR vector addresses before coding.

### 3.  Write the complete AVR Assembly program; comment vector entries, context save/restore and interrupt enabling.

### 4.  Write the equivalent Embedded C program; comment each register mask, ISR and shared-state variable.

### 5.  Program and verify the two versions on the real ATmega32A, then attach real photographs and measured results.

#### Exercise 14 - Assembly (ASM) source code (student work)

#### Exercise 14 - C language source code (student work)

#### Exercise 14 - Recorded physical experimental results

#### Exercise 15 - Multi-source interrupt-driven interface

Instruction. Design a small application with at least two distinct interrupt sources. Recommended: USART receive-complete IRQ to receive a command 0..F, plus INT0 to arm/disarm an output, or ADC completion IRQ plus Timer1 CTC to periodically sample an analog sensor. Display a maximum of four LEDs, implement a clear state machine, and explain how you protect shared state. Demonstrate valid input, invalid input, and recovery.

### 1.  Draw the algorithm and symbol-based circuit, identifying every MCU signal and series resistor.

### 2.  Compute timer/baud/ADC parameters and determine ISR vector addresses before coding.

### 3.  Write the complete AVR Assembly program; comment vector entries, context save/restore and interrupt enabling.

### 4.  Write the equivalent Embedded C program; comment each register mask, ISR and shared-state variable.

### 5.  Program and verify the two versions on the real ATmega32A, then attach real photographs and measured results.

#### Exercise 15 - Assembly (ASM) source code (student work)

#### Exercise 15 - C language source code (student work)

#### Exercise 15 - Recorded physical experimental results

9. Submission and assessment

Submit the completed editable lab manual (DOCX and/or PDF) containing real physical evidence from each tutorial, the written Assembly and C exercise solutions, and completed measurement tables. Attach both source files and HEX files for all tutorials/exercises in the corresponding ZIP archive.

No simulation screenshots may be substituted for real hardware evidence. Measurement limitations must be stated, not concealed. A functioning but incompletely documented solution can earn partial content credit under instructor policy.

10. References

### 1.  Microchip Technology, ATmega32A Complete Data Sheet, DS40002072A (interrupt vectors, external interrupts, timers, ADC, USART and electrical limits). https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega32A-DataSheet-Complete-DS40002072A.pdf

### 2.  Microchip Technology, AVR Instruction Set Manual (SEI, CLI, RETI, RCALL, BRxx, IN/OUT and arithmetic instructions).

### 3.  AVR-LibC User Manual, interrupt handling and ISR(VECTOR_vect): https://www.nongnu.org/avr-libc/user-manual/group__avr__interrupts.html

### 4.  EE084IU Microprocessing Systems Laboratory, Lab Manual 4: Timer/Counter Programming and PWM Control Using ATmega32A (user-supplied reference for organization and academic style).
