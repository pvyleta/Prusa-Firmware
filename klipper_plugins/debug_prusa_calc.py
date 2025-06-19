#!/usr/bin/env python3
import math

# Exact constants from Prusa
SIN0 = 0
AMP = 248
MIDPOINT_VALUE = 175.362481734263781
SIN_127_5 = 0.704934080375905

def debug_prusa_calculation():
    print("🔍 Debugging Prusa Wave Calculation")
    print("=" * 50)
    
    fac1000 = 1100
    fac = (fac1000 + 1000) / 1000.0  # Should be 2.1
    print(f"Factor: {fac}")
    
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
    
    # Check what happens at position 127
    i = 127
    sin_val = math.sin(math.pi * i / 512.0)
    theoretical_value = (AMP - SIN0) * pow(sin_val, fac) * tcorr + SIN0
    vA = int(theoretical_value + 0.5)
    print(f"\nPosition 127: sin_val={sin_val:.6f}, theoretical={theoretical_value:.6f}, vA={vA}")
    
    # Check the midpoint constraint
    print(f"Expected midpoint: {MIDPOINT_VALUE}")
    print(f"Actual midpoint: {vA}")

if __name__ == '__main__':
    debug_prusa_calculation()
