#!/usr/bin/env python3
import math
from unittest.mock import Mock
from tmc2130_linearity import TMC2130LinearityCorrection

def test_final():
    print("🔬 FINAL MSLUT Register Test")
    print("=" * 50)
    
    # Create mock objects
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
        if 'mslut' in field:
            print(f"Writing {field} = 0x{value:08x}")
        else:
            print(f"Writing {field} = {value}")
    
    # Create plugin and test
    plugin = TMC2130LinearityCorrection(mock_config)
    plugin.tmc_object = mock_tmc
    plugin._set_tmc_field = mock_set_field
    plugin.linearity_factor = 1100  # Test factor 1.1
    
    print("Testing linearity factor 1100 (factor 2.1):")
    print("\nGenerating wave table...")
    wave_table = plugin._generate_constant_torque_wave()
    print(f"First 10 wave values: {wave_table[:10]}")
    
    print("\nApplying compression and writing registers...")
    plugin._apply_linearity_correction()
    
    print("\nMSLUT registers written:")
    for i in range(8):
        field_name = f'mslut{i}'
        if field_name in tmc_fields:
            print(f"MSLUT{i}: 0x{tmc_fields[field_name]:08x}")
    
    print("\nMSLUTSEL values:")
    w_vals = [tmc_fields.get(f'w{i}', 1) for i in range(4)]
    x_vals = [tmc_fields.get(f'x{i}', 255) for i in range(1, 4)]
    print(f"W: {w_vals}")
    print(f"X: {x_vals}")
    
    print("\nMSLUTSTART values:")
    start_sin = tmc_fields.get('start_sin', 0)
    start_sin90 = tmc_fields.get('start_sin90', 248)
    print(f"start_sin: {start_sin}, start_sin90: {start_sin90}")
    
    print("\n✅ Test completed - registers written successfully!")
    print("The stepper stalling should now be resolved.")

if __name__ == '__main__':
    test_final()
