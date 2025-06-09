/*
 * Mock util/delay.h for testing on non-AVR systems
 */
#ifndef UTIL_DELAY_H
#define UTIL_DELAY_H

// Mock delay functions
#define _delay_ms(ms) do {} while(0)
#define _delay_us(us) do {} while(0)

#endif // UTIL_DELAY_H
