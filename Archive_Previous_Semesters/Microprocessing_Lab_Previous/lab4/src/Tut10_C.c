/* T10: Timer1 ICP1 period measurement (100Hz detector) */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <stdint.h>
int main(void) {
    DDRA |= (1 << PA0) | (1 << PA1); // green / red status
    PORTA &= ~((1 << PA0) | (1 << PA1));
    DDRD &= ~(1 << PD6);           // ICP1 input
    TCCR1A = 0; TCCR1B = 0;
    TCNT1 = 0;
    TIFR = (1 << ICF1);            // clear pending capture flag
    TCCR1B = (1 << ICES1) | (1 << CS11); // rising capture; /8
    uint16_t previous = 0;
    uint8_t first = 1;
    for (;;) {
        while (!(TIFR & (1 << ICF1))) { }
        uint16_t now = ICR1;       // hardware latched timestamp
        TIFR = (1 << ICF1);        // W1C capture flag
        if (first) { previous = now; first = 0; continue; }
        uint16_t delta = (uint16_t)(now - previous); // modulo 2^16
        previous = now;
        if (delta >= 19000 && delta <= 21000)
            PORTA = (PORTA & ~0x03) | (1 << PA0);
        else
            PORTA = (PORTA & ~0x03) | (1 << PA1);
    }
}