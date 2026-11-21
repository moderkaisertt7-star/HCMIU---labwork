/* T12: Timer1 CTC traffic light / ATmega32A at 16 MHz */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <stdint.h>

int main(void)
{
    DDRA |= (1<<PA0)|(1<<PA1)|(1<<PA2);
    PORTA &= ~0x07;
    TCCR1A = 0;
    TCCR1B = 0;               // stop Timer1 before configuration
    TCNT1 = 0;
    OCR1A = 62499;            // 1 s = 62500 * 256 / 16 MHz
    TIFR = (1<<OCF1A);        // acknowledge pending compare

    uint8_t state = 0;        // 0=GREEN, 1=YELLOW, 2=RED
    uint8_t remaining = 3;
    PORTA = (PORTA & ~0x07) | (1<<PA2); // GREEN at t=0
    TCCR1B = (1<<WGM12)|(1<<CS12);     // CTC, prescaler 256

    for (;;) {
        while (!(TIFR & (1<<OCF1A))) { } // wait full 1 s
        TIFR = (1<<OCF1A);               // W1C
        if (--remaining != 0) continue;
        if (state == 0) {
            state = 1; remaining = 1;
            PORTA = (PORTA & ~0x07) | (1<<PA1); // YELLOW
        } else if (state == 1) {
            state = 2; remaining = 3;
            PORTA = (PORTA & ~0x07) | (1<<PA0); // RED
        } else {
            state = 0; remaining = 3;
            PORTA = (PORTA & ~0x07) | (1<<PA2); // GREEN
        }
    }
}