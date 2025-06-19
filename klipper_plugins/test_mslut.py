#!/usr/bin/env python3
import math

# Constants
SIN0 = 0
AMPLITUDE = 248
MIDPOINT_VALUE = 175.362481734263781
SIN_127_5 = 0.704934080375905

def prusa_calc_constant_torque_value(i, fac, tcorr):
    if i < 128:
        sin_val = math.sin(math.pi * i / 512.0)
        theoretical_value = (AMPLITUDE - SIN0) * pow(sin_val, fac) * tcorr + SIN0
        return int(theoretical_value + 0.5)
    else:
        mirror_i = 255 - i
        sin_val = math.sin(math.pi * mirror_i / 512.0)
        mirror_theoretical = (AMPLITUDE - SIN0) * pow(sin_val, fac) * tcorr + SIN0
        theoretical_value = math.sqrt(AMPLITUDE * AMPLITUDE + SIN0 * SIN0 - mirror_theoretical * mirror_theoretical)
        return int(theoretical_value + 0.5)

def generate_prusa_wave_table(fac1000):
    fac = (fac1000 + 1000) / 1000.0 if fac1000 else 1.0
    tcorr = MIDPOINT_VALUE / ((AMPLITUDE - SIN0) * pow(SIN_127_5, fac))
    
    wave_table = []
    for i in range(256):
        value = prusa_calc_constant_torque_value(i, fac, tcorr)
        wave_table.append(value)
    
    return wave_table

def prusa_compress_wave_table(wave_table):
    # Prusa compression algorithm
    va = 0
    d0 = 0
    d1 = 1
    w = [1, 1, 1, 1]
    x = [255, 255, 255]
    s = 0
    
    mslut_registers = [0] * 8
    reg = 0
    
    print("Prusa compression simulation:")
    print("i\tvA\tdA\tb\treg_after_shift")
    
    for i in range(min(32, len(wave_table))):  # Show first 32 for debugging
        if (i & 0x1f) == 0:
            reg = 0
        
        vA = wave_table[i]
        dA = vA - va
        va = vA
        
        b = -1
        if dA == d0:
            b = 0
        elif dA == d1:
            b = 1
        else:
            if s < 3:
                if dA < d0:
                    d1 = d0
                    d0 = dA
                    b = 0
                elif dA > d1:
                    d0 = d1
                    d1 = dA
                    b = 1
                else:
                    b = 0 if abs(dA - d0) <= abs(dA - d1) else 1
                
                w[s] = 1 if b == 1 else 0
                if s < 2:
                    x[s] = i
                s += 1
            else:
                b = 0 if abs(dA - d0) <= abs(dA - d1) else 1
        
        if b == 1:
            reg |= 0x80000000
        
        print(f"{i}\t{vA}\t{dA}\t{b}\t0x{reg:08x}")
        
        if (i & 31) == 31:
            mslut_registers[i >> 5] = reg
        else:
            reg >>= 1
    
    return mslut_registers, w, x

# Test
print("🔬 MSLUT Register Compression Test")
print("=" * 50)

wave_table = generate_prusa_wave_table(1100)
print(f"First 10 wave values: {wave_table[:10]}")

mslut_regs, w_vals, x_vals = prusa_compress_wave_table(wave_table)
print(f"\nFirst MSLUT register: 0x{mslut_regs[0]:08x}")
print(f"W values: {w_vals}")
print(f"X values: {x_vals}")
