/* LAB 8.7 — Timer1 fast PWM on OC1A/PD5, timer0 pacing */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <stdint.h>

static void wait_ms(uint16_t n)
{
    while (n--) {
        while (!(TIFR & (1 << OCF0))) { /* 1-ms tick */ }
        TIFR = (1 << OCF0);            // clear by writing 1
    }
}

int main(void)
{
    DDRD |= (1 << PD5);               // PD5 / OC1A output
    TCCR1A = 0;
    TCCR1B = 0;
    TCNT1 = 0;
    OCR1A = 64;
    TCCR1A = (1 << COM1A1) | (1 << WGM10);
    TCCR1B = (1 << WGM12) | (1 << CS11) | (1 << CS10);
                                      // Fast PWM 8-bit, /64
    TCCR0 = 0;
    TCNT0 = 0;
    OCR0 = 249;
    TIFR = (1 << OCF0);
    TCCR0 = (1 << WGM01) | (1 << CS01) | (1 << CS00);

    while (1) {
        OCR1A = 64;  wait_ms(2000);   // about 25% duty
        OCR1A = 128; wait_ms(2000);   // about 50% duty
        OCR1A = 192; wait_ms(2000);   // about 75% duty
    }
}