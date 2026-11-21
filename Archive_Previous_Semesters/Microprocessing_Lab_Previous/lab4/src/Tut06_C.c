/* T06: Timer2 CTC hardware 500 Hz on OC2 (PD7) */
#define F_CPU 16000000UL
#include <avr/io.h>
int main(void) {
    DDRD |= (1 << PD7);       // enable hardware OC2 output
    PORTD &= ~(1 << PD7);
    TCCR2 = 0; TCNT2 = 0;   // stop before configuration
    ASSR = 0;               // synchronous Timer2 / CPU I/O clock
    OCR2 = 124;             // 16MHz/(2*128*(124+1))=500Hz
    TCCR2 = (1 << WGM21) | (1 << COM20) |
            (1 << CS22) | (1 << CS20); // CTC toggle, /128
    for (;;) { /* hardware runs without CPU intervention */ }
}