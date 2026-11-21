/* LAB 8.5 — Count rising pulses on T0 (PB0) */
#define F_CPU 16000000UL
#include <avr/io.h>

int main(void)
{
    DDRA = 0x0F;                   // four binary-display LEDs
    PORTA = 0x00;
    DDRB &= ~(1 << PB0);           // T0 input
    PORTB &= ~(1 << PB0);          // no pull-up: driven clock
    TCCR0 = 0;                     // stop before setup
    TCNT0 = 0;
    TCCR0 = (1 << CS02) | (1 << CS01) | (1 << CS00);
                                    // external T0 RISING edges
    while (1) {
        PORTA = TCNT0 & 0x0F;      // visible nibble repeats 0...15
    }
}