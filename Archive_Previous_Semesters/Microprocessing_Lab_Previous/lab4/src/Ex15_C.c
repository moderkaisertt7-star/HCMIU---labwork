/*
 * Exercise 15: Timer1 8-Bit Fast PWM Brightness Controller on OC1A / PD5
 * Target MCU: ATmega32A
 * Clock Frequency: 16.0 MHz External Crystal
 * Description:
 *   - Timer1 in 8-bit Fast PWM mode (Mode 5: WGM12=1, WGM10=1, TOP=0x00FF)
 *   - Prescaler N = 64 (CS11=1, CS10=1)
 *   - Carrier Frequency: f_PWM = 16 MHz / (64 * 256) = 976.5625 Hz (~976.56 Hz)
 *   - Output pin: PD5 / OC1A (Non-inverting: COM1A1=1, COM1A0=0)
 *   - Pushbutton on PB2 (active LOW with internal pull-up)
 *   - 4 selectable duty cycles:
 *       Level 0: ~10% (OCR1A = 26)
 *       Level 1: ~35% (OCR1A = 89)
 *       Level 2: ~65% (OCR1A = 166)
 *       Level 3: ~90% (OCR1A = 230)
 *   - Pressing PB2 cycles: 10% -> 35% -> 65% -> 90% -> 10%
 */

#define F_CPU 16000000UL
#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

// Duty cycle lookup table (OCR1A compare values for 8-bit Fast PWM)
// TOP = 255. Non-inverting duty = (OCR1A + 1) / 256
static const uint8_t duty_table[4] = {
    26,   // Level 0: 26/255  ~ 10.2%
    89,   // Level 1: 89/255  ~ 34.9%
    166,  // Level 2: 166/255 ~ 65.1%
    230   // Level 3: 230/255 ~ 90.2%
};

int main(void)
{
    // 1. Configure PD5 (OC1A) as output for PWM signal
    DDRD |= (1 << PD5);
    PORTD &= ~(1 << PD5);

    // 2. Configure PB2 as button input with internal pull-up
    DDRB &= ~(1 << PB2);
    PORTB |= (1 << PB2);

    uint8_t mode = 0; // Current duty cycle setting (0..3)

    // 3. Set initial duty cycle (Level 0: ~10%)
    OCR1A = duty_table[mode];

    // 4. Configure Timer1:
    //    - 8-bit Fast PWM (Mode 5: WGM13=0, WGM12=1, WGM11=0, WGM10=1)
    //    - Non-inverting mode on OC1A (COM1A1=1, COM1A0=0)
    //    - Prescaler N = 64 (CS12=0, CS11=1, CS10=1)
    TCCR1A = (1 << COM1A1) | (1 << WGM10);
    TCCR1B = (1 << WGM12) | (1 << CS11) | (1 << CS10);

    while (1) {
        // 5. Poll pushbutton on PB2 (active LOW)
        if (!(PINB & (1 << PB2))) {
            _delay_ms(25); // Debounce delay
            if (!(PINB & (1 << PB2))) {
                // Advance setting
                mode = (mode + 1) % 4;
                OCR1A = duty_table[mode];

                // Wait for button release to prevent multiple triggers
                while (!(PINB & (1 << PB2))) {
                    // Wait
                }
                _delay_ms(25); // Debounce release
            }
        }
    }

    return 0;
}
