/*
 * Exercise 14: Timer1 External Event Counter with 4-LED Nibble Selection & Reset
 * Target MCU: ATmega32A
 * Clock Frequency: 16.0 MHz External Crystal
 * Description:
 *   - PB1/T1 receives external rising-edge clock pulses (CS12:0 = 111)
 *   - PA0..PA3 display one selected 4-bit nibble of the 16-bit TCNT1 counter
 *   - PB2 and PB3 are active-LOW inputs with pull-ups to select the active nibble:
 *       PB3=1, PB2=1 -> Nibble 0 (bits 3..0)
 *       PB3=1, PB2=0 -> Nibble 1 (bits 7..4)
 *       PB3=0, PB2=1 -> Nibble 2 (bits 11..8)
 *       PB3=0, PB2=0 -> Nibble 3 (bits 15..12)
 *   - PB4 is active-LOW button with pull-up to reset TCNT1 to 0 (software reset)
 *     with 20 ms debouncing.
 */

#define F_CPU 16000000UL
#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

int main(void)
{
    // 1. Configure PA0..PA3 as Outputs for 4-bit nibble display
    DDRA = (DDRA & 0xF0) | 0x0F;
    PORTA &= 0xF0; // Clear display (LEDs OFF)

    // 2. Configure Port B pins:
    //    PB1 (T1)  : Input, no pull-up (driven by external pulse generator)
    //    PB2, PB3  : Input with pull-up (nibble select switches)
    //    PB4       : Input with pull-up (software counter reset button)
    DDRB &= ~((1 << PB1) | (1 << PB2) | (1 << PB3) | (1 << PB4));
    PORTB &= ~(1 << PB1);                                    // PB1: floating/driven
    PORTB |= (1 << PB2) | (1 << PB3) | (1 << PB4);           // PB2, PB3, PB4 pull-ups ON

    // 3. Configure Timer1 as 16-bit normal counter on T1 rising edge
    TCCR1A = 0; // Normal mode (WGM11:10 = 0)
    TCNT1 = 0;  // Reset counter value

    // Clock Select: External clock source on T1 pin, clock on rising edge
    // CS12 = 1, CS11 = 1, CS10 = 1
    TCCR1B = (1 << CS12) | (1 << CS11) | (1 << CS10);

    while (1) {
        // 4. Check PB4 (Software Reset Button)
        if (!(PINB & (1 << PB4))) { // Button pressed (active LOW)
            _delay_ms(20);           // Debounce
            if (!(PINB & (1 << PB4))) {
                TCNT1 = 0;           // Clear 16-bit counter
                while (!(PINB & (1 << PB4))) {
                    // Wait for release
                }
                _delay_ms(20);       // Debounce release
            }
        }

        // 5. Read 16-bit Timer1 counter atomically/safely
        uint16_t current_count = TCNT1;

        // 6. Read PB2 and PB3 switch inputs
        //    PB2 is bit 2, PB3 is bit 3
        uint8_t pb2 = (PINB & (1 << PB2)) ? 1 : 0;
        uint8_t pb3 = (PINB & (1 << PB3)) ? 1 : 0;

        uint8_t nibble_val = 0;
        if (pb3 && pb2) {
            // Both released -> Nibble 0 (bits 3..0)
            nibble_val = (uint8_t)(current_count & 0x0F);
        } else if (pb3 && !pb2) {
            // PB2 pressed -> Nibble 1 (bits 7..4)
            nibble_val = (uint8_t)((current_count >> 4) & 0x0F);
        } else if (!pb3 && pb2) {
            // PB3 pressed -> Nibble 2 (bits 11..8)
            nibble_val = (uint8_t)((current_count >> 8) & 0x0F);
        } else {
            // Both pressed -> Nibble 3 (bits 15..12)
            nibble_val = (uint8_t)((current_count >> 12) & 0x0F);
        }

        // 7. Output to PA0..PA3 preserving PA4..PA7
        PORTA = (PORTA & 0xF0) | (nibble_val & 0x0F);
    }

    return 0;
}
