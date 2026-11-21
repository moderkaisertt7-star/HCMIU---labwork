/* T02: 4-LED binary counter with Timer0 overflow polling */
#define F_CPU 16000000UL
#include <avr/io.h>
#include <stdint.h>
int main(void) {
    uint8_t value = 0;
    DDRA = 0x0F; PORTA = 0;
    TCCR0 = 0; TCNT0 = 0;
    TIFR = (1 << TOV0);                // W1C overflow flag
    TCCR0 = (1 << CS02) | (1 << CS00); // normal, /1024
    for (;;) {
        for (uint8_t i = 0; i < 61; ++i) {
            while (!(TIFR & (1 << TOV0))) { }
            TIFR = (1 << TOV0);
        }
        PORTA = (++value) & 0x0F;    // only PA3...PA0
    }
}