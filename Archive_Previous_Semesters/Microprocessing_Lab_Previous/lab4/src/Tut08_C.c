/* T08: 16-bit Timer1 external counter, four-LED nibble display */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <stdint.h>
int main(void)
{
    DDRA = (DDRA & 0xF0) | 0x0F; // PA0..PA3 LED outputs
    PORTA &= 0xF0;
    DDRB &= ~((1<<PB1)|(1<<PB2)|(1<<PB3));
    PORTB &= ~(1<<PB1);          // PB1/T1: generator driven
    PORTB |= (1<<PB2)|(1<<PB3);  // PB2, PB3 button pull-ups
    TCCR1A = 0;
    TCCR1B = 0;
    TCNT1 = 0;
    TCCR1B = (1<<CS12)|(1<<CS11)|(1<<CS10); // rising T1
    for (;;) {
        uint16_t count = TCNT1;
        uint8_t buttons = PINB;
        uint8_t selector = ((buttons & (1<<PB2)) ? 0 : 1) |
                           ((buttons & (1<<PB3)) ? 0 : 2);
        uint8_t nibble = (count >> (4*selector)) & 0x0F;
        PORTA = (PORTA & 0xF0) | nibble;
    }
}