/* LAB 8.4 — Hardware-generated 1 Hz square wave on PD5/OC1A */
#define F_CPU 16000000UL
#include <avr/io.h>

int main(void)
{
    DDRD |= (1 << PD5);           // PD5 must be OUTPUT
    PORTD &= ~(1 << PD5);         // initial state LOW
    TCCR1A = 0;                  // stop/change mode safely
    TCCR1B = 0;
    TCNT1 = 0;
    OCR1A = 31249;               // 31250 x (256/16MHz)=0.5 s
    TCCR1A = (1 << COM1A0);     // toggle OC1A each compare
    TCCR1B = (1 << WGM12) | (1 << CS12); // CTC, /256
    while (1) { /* hardware runs with no polling */ }
}