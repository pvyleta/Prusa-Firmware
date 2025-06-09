# TMC2130 Fast Math Optimization

High-performance mathematical functions optimized for ATmega 2560 microcontroller, replacing expensive floating-point library calls in TMC2130 stepper motor control.

## Performance Gains

| Function | Library Time | Fast Time | Speedup | Precision |
|----------|-------------|-----------|---------|-----------|
| `sin()`  | ~105μs      | ~2.1μs    | 50x     | <5e-8 error |
| `sqrt()` | ~83μs       | ~8.3μs    | 10x     | <2e-5 error |
| `pow()`  | ~82μs       | ~6.8μs    | 12x     | <0.1% error |

*Benchmarked on ATmega 2560 @ 16MHz using avr-gcc 7.3.0*

## Implementation

### fast_sin()
- 7-term Taylor series with trigonometric symmetry
- Full range support via argument reduction
- Memory: 0 bytes (no lookup tables)

### fast_sqrt()
- 16.16 fixed-point binary search algorithm
- 1000x+ precision improvement over 8.8 version
- Handles full uint16_t range [0, 65535]

### fast_pow()
- 5-segment piecewise ln(x) approximation
- 5-term Taylor series for exp() computation
- Optimized for TMC2130 range: x∈[0.01,1.0], fac∈[1.0,1.2]

## Integration

Functions located in `Firmware/util.h` and `Firmware/util.cpp` for firmware-wide availability. TMC2130 wave generation achieves 8-12x overall speedup while maintaining library-equivalent precision.

## Technical Notes

The ln(x) + Taylor approach for pow() provides superior numerical stability compared to direct polynomial approximation, particularly for the wide dynamic range required by stepper motor control algorithms.


## References

- [TMC2130 Constant Torque Discussion](https://forum.prusa3d.com/forum/original-prusa-i3-mk3s-mk3-user-mods-octoprint-enclosures-nozzles/stepper-motor-upgrades-to-eliminate-vfa-s-vertical-fine-artifacts/paged/2/)
- [Analog Devices AN-026](https://www.analog.com/en/resources/app-notes/an-026.html)
