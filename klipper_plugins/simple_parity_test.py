#!/usr/bin/env python3
import math
from unittest.mock import Mock
from tmc2130_linearity import TMC2130LinearityCorrection

def prusa_calc_constant_torque_value(i, va, fac, tcorr, carry, prev_theoretical_value):
    """Exact Prusa algorithm"""
    SIN0 = 0
    AMP = 248
    TARGET_MAGNITUDE_SQUARED = float(AMP * AMP + SIN0 * SIN0)

    if i < 128:
        sin_val = math.sin(math.pi * float(i) / 512.0)
        theoretical_value = (AMP - SIN0) * pow(sin_val, fac) * tcorr + SIN0
    else:
        mirror_i = 255 - i
        sin_val = math.sin(math.pi * float(mirror_i) / 512.0)
        mirror_theoretical = (AMP - SIN0) * pow(sin_val, fac) * tcorr + SIN0
        theoretical_value = math.sqrt(TARGET_MAGNITUDE_SQUARED - mirror_theoretical * mirror_theoretical)

    adjusted_theoretical = theoretical_value - carry[0]
    candidate_value = int(adjusted_theoretical + 0.5)

    slope = theoretical_value - prev_theoretical_value[0]
    min_delta = int(math.floor(slope))

    if min_delta < -1:
        min_delta = -1
    elif min_delta > 2:
        min_delta = 2

    delta = candidate_value - va
    if delta < min_delta:
        candidate_value = va + min_delta
    elif delta > min_delta + 1:
        candidate_value = va + min_delta + 1

    if candidate_value < SIN0:
        candidate_value = SIN0
    elif candidate_value > AMP:
        candidate_value = AMP

    carry[0] = candidate_value - theoretical_value
    prev_theoretical_value[0] = theoretical_value

    return candidate_value

def generate_prusa_reference_wave(fac1000):
    """Generate reference wave table using exact Prusa algorithm"""
    if fac1000:
        fac = float((fac1000 + 1000)) / 1000.0
    else:
        fac = 1.0

    SIN0 = 0
    AMP = 248
    MIDPOINT_VALUE = 175.362481734263781
    SIN_127_5 = 0.704934080375905
    tcorr = (MIDPOINT_VALUE - SIN0) / ((AMP - SIN0) * pow(SIN_127_5, fac))

    wave_table = []
    va = 0
    carry = [0.0]
    prev_theoretical_value = [0.0]

    for i in range(256):
        vA = prusa_calc_constant_torque_value(i, va, fac, tcorr, carry, prev_theoretical_value)
        wave_table.append(vA)
        va = vA

    return wave_table

def test_wave_parity():
    """Test wave table generation parity"""
    print("🎯 TESTING WAVE TABLE PARITY")
    print("=" * 40)
    
    for fac1000 in [1100]:  # Test factor 1.1
        print(f"\nTesting linearity factor {fac1000}:")
        
        # Generate Prusa reference
        prusa_wave = generate_prusa_reference_wave(fac1000)
        
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
        
        plugin = TMC2130LinearityCorrection(mock_config)
        plugin.tmc_object = mock_tmc
        plugin.linearity_factor = fac1000
        
        # Generate our wave table
        our_wave = plugin._generate_constant_torque_wave()
        
        # Compare
        wave_matches = sum(1 for p, o in zip(prusa_wave, our_wave) if p == o)
        wave_parity = wave_matches / 256 * 100
        
        print(f"Wave table parity: {wave_matches}/256 ({wave_parity:.1f}%)")
        
        if wave_parity == 100.0:
            print("🎉 PERFECT 100% WAVE TABLE PARITY!")
        else:
            print("❌ Wave table differences (first 20):")
            diff_count = 0
            for i in range(256):
                if prusa_wave[i] != our_wave[i] and diff_count < 20:
                    print(f"  Index {i}: Prusa={prusa_wave[i]}, Ours={our_wave[i]}")
                    diff_count += 1
        
        # Show sample values
        print(f"\nFirst 10 values:")
        print(f"Prusa: {prusa_wave[:10]}")
        print(f"Ours:  {our_wave[:10]}")
        
        print(f"\nLast 10 values:")
        print(f"Prusa: {prusa_wave[-10:]}")
        print(f"Ours:  {our_wave[-10:]}")

if __name__ == '__main__':
    test_wave_parity()
