/*
 * Mock AVR interrupt header for testing on non-AVR systems
 */
#ifndef AVR_INTERRUPT_H
#define AVR_INTERRUPT_H

// Mock AVR interrupt functions
#define cli() do {} while(0)
#define sei() do {} while(0)

#endif // AVR_INTERRUPT_H
