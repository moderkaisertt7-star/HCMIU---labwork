/* T09: Timer0 Fast PWM, button selects brightness */
#define F_CPU 16000000UL
#include <avr/io.h>
int main(void) {
    DDRB |= (1 << PB3);       // OC0 hardware PWM output
    DDRB &= ~(1 << PB1);      // pushbutton input
    PORTB |= (1 << PB1);     // internal pull-up
    TCCR0 = 0; TCNT0 = 0;
    OCR0 = 64;               // 25% (approximately)
    TCCR0 = (1 << WGM00) | (1 << WGM01) | (1 << COM01) |
            (1 << CS01) | (1 << CS00); // Fast PWM, /64
    while (1) {
        OCR0 = (PINB & (1 << PB1)) ? 64 : 192;
        // released=25%, pressed=75%; PWM driven by hardware
    }
}