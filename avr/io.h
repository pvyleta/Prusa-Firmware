/*
 * Mock AVR IO header for testing on non-AVR systems
 */
#ifndef AVR_IO_H
#define AVR_IO_H

// Mock AVR IO definitions
#define PROGMEM
#define pgm_read_byte(addr) (*(const unsigned char *)(addr))
#define pgm_read_word(addr) (*(const unsigned short *)(addr))

#endif // AVR_IO_H
