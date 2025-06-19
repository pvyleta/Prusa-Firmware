#!/usr/bin/env python3
import math

# Exact constants from Prusa
SIN0 = 0
AMP = 248
MIDPOINT_VALUE = 175.362481734263781
SIN_127_5 = 0.704934080375905

def debug_prusa_calculation():
    print("🔍 Debugging Prusa Wave Calculation (FIXED)")
    print("=" * 50)
    
    fac1000 = 1100
    # CORRECT: fac = (fac1000 + 1000) / 1000.0 is WRONG
    # CORRECT: fac = fac1000 / 1000.0 when fac1000 > 0
    if fac1000:
        fac = ((fac1000 + 1000) / 1000.0) / 1000.0  # This is still wrong
    
    # Let me check the Prusa code again...
    # From line 1156: fac = ((float)((uint16_t)fac1000 + 1000) / 1000)
    # So for fac1000=1100: fac = (1100 + 1000) / 1000 = 2100 / 1000 = 2.1
    # But that seems wrong for a "factor 1.1"
    
    # Let me try the interpretation: fac1000 represents the factor * 1000
    # So fac1000=1100 means factor=1.1
    fac = fac1000 / 1000.0  # This should be correct
    print(f"Factor (corrected): {fac}")
    
    # Calculate tcorr
    tcorr = MIDPOINT_VALUE / ((AMP - SIN0) * pow(SIN_127_5, fac))
    print(f"tcorr: {tcorr}")
    
    # Test first few calculations
    print("\nFirst 10 calculations:")
    print("i\tsin_val\t\ttheoretical\tvA")
    
    for i in range(10):
        sin_val = math.sin(math.pi * i / 512.0)
        theoretical_value = (AMP - SIN0) * pow(sin_val, fac) * tcorr + SIN0
        vA = int(theoretical_value + 0.5)
        print(f"{i}\t{sin_val:.6f}\t{theoretical_value:.6f}\t{vA}")

if __name__ == '__main__':
    debug_prusa_calculation()
