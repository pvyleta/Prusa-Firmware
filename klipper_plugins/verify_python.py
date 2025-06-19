#!/usr/bin/env python3
import math
from unittest.mock import Mock
from tmc2130_linearity import TMC2130LinearityCorrection

def verify_python_implementation():
    print("PYTHON IMPLEMENTATION VERIFICATION")
    print("==================================")
    
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
            print(f"{field.upper()} = 0x{value:08x}")
        elif field.startswith('start_'):
            if field == 'start_sin':
                print(f"MSLUTSTART: start_sin={value}", end="")
            elif field == 'start_sin90':
                print(f", start_sin90={value}")
    
    plugin = TMC2130LinearityCorrection(mock_config)
    plugin.tmc_object = mock_tmc
    plugin._set_tmc_field = mock_set_field
    plugin.linearity_factor = 1100
    
    print("=== PYTHON tmc2130_linearity_correction ===")
    print(f"linearity_factor = {plugin.linearity_factor}")
    
    fac1000 = plugin.linearity_factor
    if fac1000:
        fac = float((fac1000 + 1000)) / 1000.0
    else:
        fac = 1.0
    print(f"Calculated fac = {fac}")
    
    SIN0 = 0
    AMP = 248
    MIDPOINT_VALUE = 175.362481734263781
    SIN_127_5 = 0.704934080375905
    tcorr = (MIDPOINT_VALUE - SIN0) / ((AMP - SIN0) * pow(SIN_127_5, fac))
    print(f"Calculated tcorr = {tcorr}")
    
    print("\nWave table values:")
    wave_table = plugin._generate_constant_torque_wave()
    
    for i in range(256):
        if i < 20 or i > 235:
            print(f"wave[{i:3d}] = {wave_table[i]:3d}")
        elif i == 20:
            print("... (wave values 20-235 omitted) ...")
    
    print("")
    
    plugin._apply_linearity_correction()
    
    w_values = []
    x_values = []
    for field, value in register_writes:
        if field.startswith('w'):
            w_values.append((field, value))
        elif field.startswith('x'):
            x_values.append((field, value))
    
    w_values.sort()
    x_values.sort()
    
    w_str = ", ".join([f"{field}={value}" for field, value in w_values])
    x_str = ", ".join([f"{field}={value}" for field, value in x_values])
    print(f"MSLUTSEL: {x_str}, {w_str}")
    
    print("=== END PYTHON ===")
    
    return register_writes, wave_table

if __name__ == '__main__':
    verify_python_implementation()
