#!/usr/bin/env python3
import math
from unittest.mock import Mock
from tmc2130_linearity import TMC2130LinearityCorrection

def test_fixed_factor():
    print("=== TESTING FIXED FACTOR CALCULATION ===")
    
    mock_printer = Mock()
    mock_config = Mock()
    mock_gcode = Mock()
    mock_tmc = Mock()
    
    mock_config.get_name.return_value = "stepper_x"
    mock_config.getfloat.return_value = 1.05  # This should give factor 1.05, not 2.05
    mock_printer.lookup_object.side_effect = lambda name: {
        'gcode': mock_gcode,
        'tmc2130 stepper_x': mock_tmc
    }.get(name, Mock())
    
    register_writes = []
    
    def mock_set_field(field, value):
        register_writes.append((field, value))
        if field.startswith('mslut'):
            print(f"TMC2130 stepper_x: {field}=0x{value:08x}")
        elif field.startswith('start_'):
            if field == 'start_sin':
                print(f"TMC2130 stepper_x: MSLUTSTART start_sin={value}", end="")
            elif field == 'start_sin90':
                print(f", start_sin90={value}")
    
    plugin = TMC2130LinearityCorrection(mock_config)
    plugin.tmc_object = mock_tmc
    plugin._set_tmc_field = mock_set_field
    
    print(f"Config linearity_factor: 1.05")
    print(f"Internal linearity_factor: {plugin.linearity_factor}")
    print(f"Calculated factor: {plugin.linearity_factor / 1000.0}")
    
    # Generate wave table and show sample values
    wave_table = plugin._generate_constant_torque_wave()
    sample_indices = [0, 32, 64, 96, 127, 128, 160, 192, 224, 255]
    sample_values = [wave_table[i] for i in sample_indices]
    print(f"Sample wave values: {sample_values}")
    
    # Apply linearity correction
    plugin._apply_linearity_correction()
    
    # Print MSLUTSEL values
    w_values = []
    x_values = []
    for field, value in register_writes:
        if field.startswith('w'):
            w_values.append((field, value))
        elif field.startswith('x'):
            x_values.append((field, value))
    
    w_values.sort()
    x_values.sort()
    
    w_list = [value for field, value in w_values]
    x_list = [value for field, value in x_values]
    print(f"TMC2130 stepper_x: MSLUTSEL w={w_list} x={x_list}")
    
    return sample_values, register_writes

if __name__ == '__main__':
    sample_values, register_writes = test_fixed_factor()
    
    print("\n=== COMPARISON WITH EXPECTED VALUES ===")
    # These should match the values from your test_all_factors_python.py for fac1000=50
    expected_sample_values = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]  # Approximate expected for factor 1.05
    expected_mslut0 = 0x5552a526  # From your test output
    
    print(f"Sample values: {sample_values}")
    print(f"Should be similar to factor 1.05 values, not factor 2.05 values")
    
    # Extract first MSLUT value
    our_mslut0 = None
    for field, value in register_writes:
        if field == 'mslut0':
            our_mslut0 = value
            break
    
    print(f"MSLUT0: 0x{our_mslut0:08x}")
    print(f"Expected MSLUT0: 0x{expected_mslut0:08x}")
    print(f"MSLUT0 matches: {our_mslut0 == expected_mslut0}")
