#!/usr/bin/env python3
"""
Test for 100% parity between our implementation and Prusa's algorithm
"""

import math
from unittest.mock import Mock
from tmc2130_linearity import TMC2130LinearityCorrection

def prusa_calc_constant_torque_value(i, va, fac, tcorr, carry, prev_theoretical_value):
    """
    Exact replication of Prusa's tmc2130_calc_constant_torque_value function
    Lines 1065-1140 in tmc2130.cpp
    """
    # Constants (lines 1067-1069)
    SIN0 = 0
    AMP = 248  # Amplitude limit as per AN-026 recommendation
    TARGET_MAGNITUDE_SQUARED = float(AMP * AMP + SIN0 * SIN0)

    # Theoretical constant torque value at microstep position i (line 1072)
    if i < 128:
        # Phase 1 (positions 0-127): Power-corrected sine curve (lines 1074-1079)
        sin_val = math.sin(math.pi * float(i) / 512.0)
        theoretical_value = (AMP - SIN0) * pow(sin_val, fac) * tcorr + SIN0
    else:
        # Phase 2 (positions 128-255): Constant torque constraint solving (lines 1080-1093)
        mirror_i = 255 - i
        sin_val = math.sin(math.pi * float(mirror_i) / 512.0)
        mirror_theoretical = (AMP - SIN0) * pow(sin_val, fac) * tcorr + SIN0
        theoretical_value = math.sqrt(TARGET_MAGNITUDE_SQUARED - mirror_theoretical * mirror_theoretical)

    # Step 1: Apply carry mechanism and initial quantization (lines 1095-1098)
    adjusted_theoretical = theoretical_value - carry[0]
    candidate_value = int(adjusted_theoretical + 0.5)

    # Step 2: Slope-based delta limiting for TMC2130 compression (lines 1100-1123)
    slope = theoretical_value - prev_theoretical_value[0]
    min_delta = int(math.floor(slope))

    # Clamp to TMC2130 hardware delta limits [-1, 3] (lines 1109-1115)
    if min_delta < -1:
        min_delta = -1
    elif min_delta > 2:
        min_delta = 2

    # Enforce delta limits (lines 1117-1123)
    delta = candidate_value - va
    if delta < min_delta:
        candidate_value = va + min_delta
    elif delta > min_delta + 1:
        candidate_value = va + min_delta + 1

    # Step 3: Final amplitude clamping (lines 1125-1130)
    if candidate_value < SIN0:
        candidate_value = SIN0
    elif candidate_value > AMP:
        candidate_value = AMP

    # Step 4: Update carry for next iteration (lines 1132-1137)
    carry[0] = candidate_value - theoretical_value
    prev_theoretical_value[0] = theoretical_value

    return candidate_value

def generate_prusa_reference_wave(fac1000):
    """Generate reference wave table using exact Prusa algorithm"""
    # Exact Prusa factor calculation (lines 1155-1156)
    if fac1000:
        fac = float((fac1000 + 1000)) / 1000.0
    else:
        fac = 1.0

    # Pre-calculate tcorr (lines 1179-1185)
    SIN0 = 0
    AMP = 248
    MIDPOINT_VALUE = 175.362481734263781
    SIN_127_5 = 0.704934080375905
    tcorr = (MIDPOINT_VALUE - SIN0) / ((AMP - SIN0) * pow(SIN_127_5, fac))

    # Generate wave table
    wave_table = []
    va = 0
    carry = [0.0]
    prev_theoretical_value = [0.0]

    for i in range(256):
        vA = prusa_calc_constant_torque_value(i, va, fac, tcorr, carry, prev_theoretical_value)
        wave_table.append(vA)
        va = vA

    return wave_table

def prusa_compress_wave_table(wave_table):
    """
    Exact replication of Prusa's compression algorithm (lines 1190-1250)
    """
    # Initialize compression state (lines 1158-1168)
    vA = 0
    va = 0
    d0 = 0
    d1 = 1
    w = [1, 1, 1, 1]
    x = [255, 255, 255]
    s = 0
    b = 0
    dA = 0
    i = 0
    reg = 0

    mslut_registers = [0] * 8

    # Main compression loop (lines 1190-1248)
    while True:
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
            if dA < d0:
                b = 0
                if dA == -1:
                    d0, d1, w[s+1] = -1, 0, 0
                elif dA == 0:
                    d0, d1, w[s+1] = 0, 1, 1
                elif dA == 1:
                    d0, d1, w[s+1] = 1, 2, 2
                else:
                    b = -1
                
                if b >= 0:
                    x[s] = i
                    s += 1
                    
            elif dA > d1:
                b = 1
                if dA == 1:
                    d0, d1, w[s+1] = 0, 1, 1
                elif dA == 2:
                    d0, d1, w[s+1] = 1, 2, 2
                elif dA == 3:
                    d0, d1, w[s+1] = 2, 3, 3
                else:
                    b = -1
                
                if b >= 0:
                    x[s] = i
                    s += 1
        
        if b < 0:
            break
        if s > 3:
            break
        
        if b == 1:
            reg |= 0x80000000
        
        if (i & 31) == 31:
            mslut_registers[i >> 5] = reg
        else:
            reg >>= 1
        
        if i == 255:
            break
        i += 1

    return mslut_registers, w, x

def test_100_percent_parity():
    """Test for 100% parity with Prusa algorithm"""
    print("🎯 TESTING FOR 100% PARITY WITH PRUSA ALGORITHM")
    print("=" * 60)
    
    # Test different linearity factors
    for fac1000 in [1000, 1050, 1100, 1150, 1200]:
        print(f"\n--- Testing linearity factor {fac1000} ---")
        
        # Generate Prusa reference
        prusa_wave = generate_prusa_reference_wave(fac1000)
        prusa_mslut, prusa_w, prusa_x = prusa_compress_wave_table(prusa_wave)
        
        # Generate our implementation
        mock_printer = Mock()
        mock_config = Mock()
        mock_gcode = Mock()
        mock_tmc = Mock()
        
        mock_config.get_name.return_value = "stepper_x"
        mock_config.getfloat.return_value = 1.0
        mock_printer.lookup_object.side_effect = lambda name: {
            'gcode': mock_gcode,
            'tmc2130 stepper_x': mock_tmc
        }.get(name, Mock())
        
        # Track TMC field writes
        tmc_fields = {}
        def mock_set_field(field, value):
            tmc_fields[field] = value
        
        # Create plugin and test
        plugin = TMC2130LinearityCorrection(mock_config)
        plugin.tmc_object = mock_tmc
        plugin._set_tmc_field = mock_set_field
        plugin.linearity_factor = fac1000
        
        # Generate wave table
        our_wave = plugin._generate_constant_torque_wave()
        
        # Compare wave tables
        wave_matches = sum(1 for p, o in zip(prusa_wave, our_wave) if p == o)
        wave_parity = wave_matches / 256 * 100
        
        print(f"Wave table parity: {wave_matches}/256 ({wave_parity:.1f}%)")
        
        if wave_parity == 100.0:
            print("✅ PERFECT wave table match!")
            
            # Test compression
            plugin._apply_linearity_correction()
            
            # Extract our MSLUT values
            our_mslut = []
            for i in range(8):
                our_mslut.append(tmc_fields.get(f'mslut{i}', 0))
            
            our_w = [tmc_fields.get(f'w{i}', 1) for i in range(4)]
            our_x = [tmc_fields.get(f'x{i}', 255) for i in range(1, 4)]
            
            # Compare MSLUT registers
            mslut_matches = sum(1 for p, o in zip(prusa_mslut, our_mslut) if p == o)
            mslut_parity = mslut_matches / 8 * 100
            
            print(f"MSLUT register parity: {mslut_matches}/8 ({mslut_parity:.1f}%)")
            
            # Compare MSLUTSEL
            w_match = prusa_w == our_w
            x_match = prusa_x == our_x
            
            print(f"MSLUTSEL W parity: {'100%' if w_match else '0%'}")
            print(f"MSLUTSEL X parity: {'100%' if x_match else '0%'}")
            
            # Overall parity
            total_parity = (wave_parity + mslut_parity + (100 if w_match else 0) + (100 if x_match else 0)) / 4
            print(f"OVERALL PARITY: {total_parity:.1f}%")
            
            if total_parity == 100.0:
                print("🎉 PERFECT 100% PARITY ACHIEVED!")
            else:
                print("❌ Not 100% parity - showing differences:")
                if not w_match:
                    print(f"  W difference: Prusa={prusa_w}, Ours={our_w}")
                if not x_match:
                    print(f"  X difference: Prusa={prusa_x}, Ours={our_x}")
                for i in range(8):
                    if prusa_mslut[i] != our_mslut[i]:
                        print(f"  MSLUT{i}: Prusa=0x{prusa_mslut[i]:08x}, Ours=0x{our_mslut[i]:08x}")
        else:
            print("❌ Wave table mismatch - showing first 20 differences:")
            diff_count = 0
            for i in range(256):
                if prusa_wave[i] != our_wave[i] and diff_count < 20:
                    print(f"  Index {i}: Prusa={prusa_wave[i]}, Ours={our_wave[i]}")
                    diff_count += 1

if __name__ == '__main__':
    test_100_percent_parity()
