/* LAB 8.3 — Timer0 compare-match interrupt, 1 Hz LED */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

ISR(TIMER0_COMP_vect)
{
    static uint16_t milliseconds = 0; // retains value between ISRs
    if (++milliseconds >= 500) {
        milliseconds = 0;
        PORTA ^= (1 << PA0);        // ISR controls LED
    }
}

int main(void)
{
    DDRA |= (1 << PA0);
    PORTA &= ~(1 << PA0);
    TCCR0 = 0;                      // stop before setup
    TCNT0 = 0;
    OCR0 = 249;
    TIFR = (1 << OCF0);             // clear pending flag
    TIMSK |= (1 << OCIE0);          // local interrupt enable
    TCCR0 = (1 << WGM01) | (1 << CS01) | (1 << CS00);
    sei();                           // global interrupt enable
    while (1) { /* other tasks could run here */ }
}