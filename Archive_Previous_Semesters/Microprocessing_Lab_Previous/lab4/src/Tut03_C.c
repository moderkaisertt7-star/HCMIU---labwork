/* LAB 8.2 — Timer0 CTC polling, ATmega32 @ 16 MHz */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <stdint.h>

int main(void)
{
    uint16_t ms = 0;
    DDRA |= (1 << PA0);
    PORTA &= ~(1 << PA0);
    TCCR0 = 0;                   // stop timer before setup
    TCNT0 = 0;
    OCR0 = 249;                  // 250 ticks x 4 us = 1 ms
    TIFR = (1 << OCF0);          // W1C: clear compare flag
    TCCR0 = (1 << WGM01) | (1 << CS01) | (1 << CS00);

    while (1) {
        while (!(TIFR & (1 << OCF0))) { /* wait for 1 ms */ }
        TIFR = (1 << OCF0);       // clear compare-match flag
        if (++ms >= 500) {       // 500 ms elapsed
            ms = 0;
            PORTA ^= (1 << PA0); // LED toggle
        }
    }
}