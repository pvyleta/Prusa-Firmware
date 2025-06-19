#!/usr/bin/env python3
import math
from unittest.mock import Mock

# Import our implementation
from tmc2130_linearity import TMC2130LinearityCorrection

# Constants
SIN0 = 0
AMPLITUDE = 248
MIDPOINT_VALUE = 175.362481734263781
SIN_127_5 = 0.704934080375905

def generate_prusa_wave_table(fac1000):
    fac = (fac1000 + 1000) / 1000.0 if fac1000 else 1.0
    tcorr = MIDPOINT_VALUE / ((AMPLITUDE - SIN0) * pow(SIN_127_5, fac))
    
    wave_table = []
    for i in range(256):
        if i < 128:
            sin_val = math.sin(math.pi * i / 512.0)
            theoretical_value = (AMPLITUDE - SIN0) * pow(sin_val, fac) * tcorr + SIN0
            value = int(theoretical_value + 0.5)
        else:
            mirror_i = 255 - i
            sin_val = math.sin(math.pi * mirror_i / 512.0)
            mirror_theoretical = (AMPLITUDE - SIN0) * pow(sin_val, fac) * tcorr + SIN0
            theoretical_value = math.sqrt(AMPLITUDE * AMPLITUDE + SIN0 * SIN0 - mirror_theoretical * mirror_theoretical)
            value = int(theoretical_value + 0.5)
        wave_table.append(value)
    
    return wave_table

def test_our_implementation():
    print("🔬 Testing Our TMC2130 Implementation")
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
        print(f"Setting {field} = 0x{value:08x}" if isinstance(value, int) and value > 255 else f"Setting {field} = {value}")
    
    # Create plugin instance
    plugin = TMC2130LinearityCorrection(mock_config)
    plugin.tmc_object = mock_tmc
    plugin._set_tmc_field = mock_set_field
    
    # Test factor 1.1
    print("\nTesting factor 1.1:")
    plugin.linearity_factor = 1100
    
    # Generate wave table
    our_wave_table = plugin._generate_constant_torque_wave()
    prusa_wave_table = generate_prusa_wave_table(1100)
    
    print(f"Our wave table (first 10): {our_wave_table[:10]}")
    print(f"Prusa wave table (first 10): {prusa_wave_table[:10]}")
    
    wave_matches = sum(1 for a, b in zip(our_wave_table, prusa_wave_table) if a == b)
    print(f"Wave table matches: {wave_matches}/256")
    
    if wave_matches == 256:
        print("✅ Wave tables match perfectly!")
        
        # Now test compression
        print("\nTesting compression:")
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
        
    else:
        print("❌ Wave tables don't match - compression test skipped")
        
        # Show differences
        print("\nFirst 20 differences:")
        for i in range(20):
            if our_wave_table[i] != prusa_wave_table[i]:
                print(f"  Index {i}: Our={our_wave_table[i]}, Prusa={prusa_wave_table[i]}")

if __name__ == '__main__':
    test_our_implementation()
