/* LAB 8.1 — Timer0 overflow polling, ATmega32 @ 16 MHz */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <stdint.h>

int main(void)
{
    uint8_t overflows = 0;
    DDRA |= (1 << PA0);         // PA0 is the LED output
    PORTA &= ~(1 << PA0);       // start with LED OFF
    TCCR0 = 0;                 // stop Timer0 while configuring
    TCNT0 = 0;                 // count from zero
    TIFR = (1 << TOV0);        // clear pending flag: write ONE
    TCCR0 = (1 << CS02) | (1 << CS00);  // prescaler = 1024

    while (1) {
        while (!(TIFR & (1 << TOV0))) { /* wait for overflow */ }
        TIFR = (1 << TOV0);     // acknowledge overflow event
        if (++overflows >= 31) {
            overflows = 0;
            PORTA ^= (1 << PA0);  // approximately every 508 ms
        }
    }
}