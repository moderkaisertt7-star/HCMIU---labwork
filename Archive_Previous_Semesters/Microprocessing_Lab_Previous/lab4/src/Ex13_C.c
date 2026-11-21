/*
 * Exercise 13: Timer0 CTC 4-Bit Counter with 250 ms Tick (Interrupt-Driven)
 * Target MCU: ATmega32A
 * Clock Frequency: 16.0 MHz External Crystal
 * Description:
 *   - Timer0 configured in CTC mode (WGM01=1, WGM00=0)
 *   - Prescaler N = 64 (CS01=1, CS00=1)
 *   - OCR0 = 249 => Interval = (249 + 1) * 64 / 16 MHz = 1.0 ms
 *   - TIMER0_COMP_vect ISR fires every 1 ms, counting up to 250 ms
 *   - Increments a 4-bit binary counter (0..15) displayed on PA0..PA3
 *   - Complete 4-bit cycle duration: 16 * 250 ms = 4.000 s
 */

#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

// Volatile variables modified inside ISR
static volatile uint8_t count_4bit = 0;
static volatile uint16_t ms_ticks = 0;

// Timer0 Output Compare Match ISR (called every 1 ms)
ISR(TIMER0_COMP_vect)
{
    if (++ms_ticks >= 250) {
        ms_ticks = 0;
        count_4bit = (count_4bit + 1) & 0x0F; // 0..15 wrap-around
        // Update PA0..PA3 while preserving PA4..PA7
        PORTA = (PORTA & 0xF0) | count_4bit;
    }
}

int main(void)
{
    // 1. Configure PA0..PA3 as Outputs for 4-bit LED display
    DDRA = (DDRA & 0xF0) | 0x0F;
    PORTA &= 0xF0; // Clear lower nibble (LEDs OFF)

    // 2. Configure Timer0 in CTC Mode (WGM01=1, WGM00=0)
    //    Stop timer during configuration
    TCCR0 = 0;
    TCNT0 = 0;

    // 3. Set OCR0 for 1 ms interval at 16 MHz with N=64
    //    Interval = (OCR0 + 1) * N / F_CPU = 250 * 64 / 16,000,000 = 1.0 ms
    OCR0 = 249;

    // 4. Clear pending compare flag (W1C)
    TIFR = (1 << OCF0);

    // 5. Enable Timer0 Output Compare Match Interrupt
    TIMSK |= (1 << OCIE0);

    // 6. Enable Global Interrupts
    sei();

    // 7. Start Timer0 with Prescaler = 64 (CS01=1, CS00=1)
    TCCR0 = (1 << WGM01) | (1 << CS01) | (1 << CS00);

    // Main loop: CPU is idle, timing is completely interrupt-driven
    while (1) {
        // Sleep or background tasks can be placed here
    }

    return 0;
}
