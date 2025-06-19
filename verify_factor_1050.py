#!/usr/bin/env python3
import math
from unittest.mock import Mock
from tmc2130_linearity import TMC2130LinearityCorrection

def test_factor_1050():
    print("=== PYTHON VERIFICATION FOR FACTOR 1050 ===")
    
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
    plugin.linearity_factor = 1050
    
    # Calculate factor using our method
    fac1000 = plugin.linearity_factor
    if fac1000:
        fac = float((fac1000 + 1000)) / 1000.0
    else:
        fac = 1.0
    print(f"linearity_factor={fac1000} → factor={fac}")
    
    # Calculate tcorr using our method
    SIN0 = 0
    AMP = 248
    MIDPOINT_VALUE = 175.362481734263781
    SIN_127_5 = 0.704934080375905
    tcorr = (MIDPOINT_VALUE - SIN0) / ((AMP - SIN0) * pow(SIN_127_5, fac))
    print(f"Calculated tcorr = {tcorr}")
    
    # Generate wave table and show sample values
    wave_table = plugin._generate_constant_torque_wave()
    sample_indices = [0, 32, 64, 96, 127, 128, 160, 192, 224, 255]
    sample_values = [wave_table[i] for i in sample_indices]
    print(f"Sample wave values: {sample_values}")
    
    # Apply linearity correction (this will trigger register writes)
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
    sample_values, register_writes = test_factor_1050()
    
    print("\n=== COMPARISON WITH YOUR KLIPPER OUTPUT ===")
    your_sample_values = [0, 12, 50, 108, 174, 177, 224, 243, 248, 248]
    your_mslut_values = [0xdb528840, 0xa921fffe, 0xfbfbdb6a, 0x08420400, 0x104ab781, 0x4aaadbbf, 0x01008222, 0x00000000]
    your_w = [1, 2, 3, 2]
    your_x = [48, 95, 134]
    
    print(f"Your Klipper sample values: {your_sample_values}")
    print(f"Our calculated sample values: {sample_values}")
    print(f"Sample values match: {sample_values == your_sample_values}")
    
    # Extract our MSLUT values
    our_mslut_values = []
    for field, value in register_writes:
        if field.startswith('mslut'):
            our_mslut_values.append(value)
    
    print(f"\nYour Klipper MSLUT values: {[hex(v) for v in your_mslut_values]}")
    print(f"Our calculated MSLUT values: {[hex(v) for v in our_mslut_values]}")
    print(f"MSLUT values match: {our_mslut_values == your_mslut_values}")
    
    # Extract our w and x values
    our_w = [value for field, value in register_writes if field.startswith('w')]
    our_x = [value for field, value in register_writes if field.startswith('x')]
    our_w.sort()
    our_x.sort()
    
    print(f"\nYour Klipper w values: {your_w}")
    print(f"Our calculated w values: {our_w}")
    print(f"W values match: {our_w == your_w}")
    
    print(f"\nYour Klipper x values: {your_x}")
    print(f"Our calculated x values: {our_x}")
    print(f"X values match: {our_x == your_x}")
