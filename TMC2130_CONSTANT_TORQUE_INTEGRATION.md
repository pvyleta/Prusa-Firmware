# TMC2130 Enhanced Linearity Correction with Algorithm Selection

## Overview

This implementation provides a comprehensive enhancement to the TMC2130 linearity correction system in Prusa firmware. It includes:

1. **Runtime Algorithm Selection**: Choose between Original and Constant Torque algorithms via menu
2. **Unified Parameter Range**: User-friendly 0-200 range mapping to power factors 1.0-1.2 for both algorithms
3. **EEPROM Storage**: Persistent storage of algorithm selection and correction values
4. **Menu Integration**: Enhanced linearity correction menu with algorithm toggle

## Features

### Constant Torque Algorithm Benefits
- **Maintains constant total torque** throughout the sine wave cycle
- **Improved compression** with error correction loop
- **Better segment management** and adaptive switching
- **Reduced motor vibrations** and smoother operation
- **Enhanced print quality** with reduced VFAs

### Menu System Features
- **Algorithm Selection Toggle**: Easy switching between Original and Constant Torque
- **Unified Parameter Range**: 0-200 maps to power factors 1.0-1.2 for both algorithms
- **Real-time Switching**: Changes take effect immediately
- **EEPROM Persistence**: Settings saved automatically
- **Backward Compatible**: Existing configurations work unchanged

## Implementation Details

### Code Structure

The implementation provides both compile-time and runtime algorithm selection:

1. **Runtime Selection**: Menu-based algorithm switching (when not compile-time forced)
2. **Compile-time Override**: `TMC2130_CONSTANT_TORQUE_WAVE` forces constant torque algorithm
3. **Single Function Interface**: `tmc2130_set_wave()` handles both algorithms dynamically
4. **EEPROM Integration**: Algorithm selection and parameters stored persistently
5. **Menu Integration**: Enhanced linearity correction menu with algorithm toggle

### Parameter Mapping

Both algorithms now use a unified user input range:
- **User Input**: 0-200 (displayed in menu)
- **Power Factor**: 1.0-1.2 (internal calculation)
- **Formula**: `power_factor = 1.0 + 0.2 * (user_input / 200.0)`

This provides:
- **0**: Power factor 1.0 (no correction)
- **100**: Power factor 1.1 (moderate correction)
- **200**: Power factor 1.2 (maximum correction)

### Algorithm Selection Logic

```cpp
// Determine which algorithm to use (runtime selection or compile-time)
bool use_constant_torque;
#ifdef TMC2130_CONSTANT_TORQUE_WAVE
    use_constant_torque = true;  // Compile-time forced to constant torque
#else
    use_constant_torque = (tmc2130_wave_algorithm == TMC2130_WAVE_ALGORITHM_CONSTANT_TORQUE);
#endif
```

## Files Modified

### 1. EEPROM Configuration
- `Firmware/eeprom.h`

Added new EEPROM location for algorithm selection at the end of EEPROM layout:
```cpp
// TMC2130 Wave Algorithm Selection (added at end to preserve existing EEPROM layout)
#define EEPROM_TMC2130_WAVE_ALGORITHM (EEPROM_TMC2130_CHOPPER_CONFIG - 1) // uint8
```

**Important**: The algorithm selection is stored at the **end** of the EEPROM layout to avoid breaking existing configurations. This ensures backward compatibility with devices that already have data in EEPROM.

### 2. TMC2130 Header
- `Firmware/tmc2130.h`

Updated parameter range and added algorithm selection:
```cpp
// Unified linearity correction range for menu (0-200 maps to power factors 1.0-1.2)
#define TMC2130_WAVE_FAC1000_MIN  0
#define TMC2130_WAVE_FAC1000_MAX 200

// Wave algorithm selection (0xFF = uninitialized/default)
#define TMC2130_WAVE_ALGORITHM_ORIGINAL       0
#define TMC2130_WAVE_ALGORITHM_CONSTANT_TORQUE 1
#define TMC2130_WAVE_ALGORITHM_DEFAULT        0xFF

extern uint8_t tmc2130_wave_algorithm;
```

### 3. Variant Headers
- `Firmware/variants/MK3S.h`

Removed compile-time define - now uses runtime selection:
```cpp
// TMC2130 Constant Torque Wave Compensation (Bunny Science's algorithm)
// This feature is now available via runtime menu selection in Settings -> Lin. correction
// No longer requires compile-time configuration - can be toggled in the menu
```

### 4. TMC2130 Implementation
- `Firmware/tmc2130.cpp`

Enhanced `tmc2130_set_wave()` function with runtime algorithm selection:
```cpp
void tmc2130_set_wave(uint8_t axis, uint8_t amp, uint8_t fac1000)
{
    // Convert unified user input (0-200) to appropriate algorithm parameters
    // User range 0-200 maps to power factors 1.0-1.2 for both algorithms

    // Determine which algorithm to use (runtime selection)
    bool use_constant_torque = (tmc2130_wave_algorithm == TMC2130_WAVE_ALGORITHM_CONSTANT_TORQUE);

    if (use_constant_torque) {
        // Constant torque algorithm implementation
    } else {
        // Original algorithm implementation
    }
}
```

### 5. EEPROM Initialization
- `Firmware/Marlin_main.cpp`

Added initialization for algorithm selection with 0xFF default:
```cpp
// Initialize wave algorithm selection
tmc2130_wave_algorithm = eeprom_read_byte((uint8_t*)EEPROM_TMC2130_WAVE_ALGORITHM);
if (tmc2130_wave_algorithm == 0xff) {
    // Default to original algorithm (0xFF = uninitialized EEPROM, compatible with stock firmware)
    tmc2130_wave_algorithm = TMC2130_WAVE_ALGORITHM_ORIGINAL;
}
```

### 6. Menu System Enhancement
- `Firmware/ultralcd.cpp`

Enhanced linearity correction menu with algorithm toggle:
```cpp
void lcd_settings_linearity_correction_menu(void)
{
    MENU_BEGIN();
    MENU_ITEM_BACK_P(_T(MSG_SETTINGS));

    // Algorithm selection (always available)
    const char* algorithm_text = (tmc2130_wave_algorithm == TMC2130_WAVE_ALGORITHM_CONSTANT_TORQUE) ?
                                _T(MSG_WAVE_CONSTANT_TORQUE) : _T(MSG_WAVE_ORIGINAL);
    MENU_ITEM_TOGGLE_P(_T(MSG_WAVE_ALGORITHM), algorithm_text, lcd_wave_algorithm_toggle);

    // Linearity correction parameters (0-200 range)
    MENU_ITEM_EDIT_int3_P(_T(MSG_X_CORRECTION), &tmc2130_wave_fac[X_AXIS], 0, 200);
    // ... other axes
    MENU_END();
}
```

### 7. Language Strings
- `Firmware/messages.cpp/.h`

Added new menu text strings:
```cpp
extern const char MSG_WAVE_ALGORITHM [] PROGMEM_I1 = ISTR("Wave algorithm");
extern const char MSG_WAVE_ORIGINAL [] PROGMEM_I1 = ISTR("Original");
extern const char MSG_WAVE_CONSTANT_TORQUE [] PROGMEM_I1 = ISTR("Constant torque");
```

## EEPROM Compatibility

### **✅ Backward Compatibility Ensured**

The implementation carefully preserves EEPROM compatibility:

1. **Algorithm Selection at End**: Added at the end of EEPROM layout to avoid shifting existing data
2. **0xFF Default Value**: Uses 0xFF (empty EEPROM value) as default, identical to uninitialized EEPROM
3. **Stock Firmware Compatible**: Can revert to stock firmware without EEPROM corruption
4. **Existing Data Preserved**: All existing linearity correction values remain unchanged

### **EEPROM Layout**

| Address | Variable | Default | Purpose |
|---------|----------|---------|---------|
| 0x0EF7 | `TMC2130_WAVE_X_FAC` | 0x00 | X-axis linearity correction |
| 0x0EF6 | `TMC2130_WAVE_Y_FAC` | 0x00 | Y-axis linearity correction |
| 0x0EF5 | `TMC2130_WAVE_Z_FAC` | 0x00 | Z-axis linearity correction |
| 0x0EF4 | `TMC2130_WAVE_E_FAC` | 0x00 | E-axis linearity correction |
| ... | (other EEPROM data) | ... | ... |
| **0x??? | `TMC2130_WAVE_ALGORITHM`** | **0xFF** | **Algorithm selection** |

### **Migration Behavior**

- **Fresh Install**: Defaults to Original algorithm (0xFF → 0)
- **Upgrade from Stock**: Preserves all existing settings, adds algorithm selection
- **Downgrade to Stock**: Algorithm selection ignored, linearity values preserved

## Usage

### Menu Navigation

1. **Access Linearity Correction Menu**:
   - Main Menu → Settings → Lin. correction

2. **Algorithm Selection** (if not compile-time forced):
   - Toggle "Wave algorithm" between "Original" and "Constant torque"
   - Changes take effect immediately

3. **Parameter Adjustment**:
   - Adjust X/Y/Z/E correction values from 0-200
   - 0 = No correction (power factor 1.0)
   - 100 = Moderate correction (power factor 1.1)
   - 200 = Maximum correction (power factor 1.2)

### Configuration Options

#### Runtime Selection (Default)
- Algorithm can be changed via menu
- Settings stored in EEPROM
- Default algorithm: Original

#### Compile-time Forcing (Removed)
- **No longer available** - all selection is now runtime-based
- Provides maximum flexibility for users
- Single firmware binary supports both algorithms
- Easy switching without recompilation

### Recommended Settings

#### For Standard 1.8° Steppers
- **Algorithm**: Original or Constant Torque
- **Correction Values**: 0-50 (power factors 1.0-1.05)

#### For 0.9° Steppers
- **Algorithm**: Constant Torque (recommended)
- **Correction Values**: 50-150 (power factors 1.05-1.15)

#### For High-Speed Printing
- **Algorithm**: Constant Torque
- **Correction Values**: 100-200 (power factors 1.1-1.2)

## Benefits

### Constant Torque Algorithm
- **Reduced VFAs**: Especially visible on 0.9° stepper motors
- **Smoother Operation**: More consistent torque delivery
- **Better Surface Quality**: Reduced artifacts in prints
- **Improved Precision**: Better positioning accuracy

### Menu System
- **User-Friendly**: Simple 0-200 range instead of complex power factors
- **Comparable Settings**: Same range works for both algorithms
- **Easy Switching**: Test both algorithms with same parameters
- **Persistent Storage**: Settings saved automatically

## Memory Usage

| Configuration | Program Memory | Data Memory | Notes |
|---------------|----------------|-------------|-------|
| **Original Only** | 234,712 bytes | 5,809 bytes | Baseline |
| **Runtime Selection** | 236,266 bytes | 5,818 bytes | +1,554 bytes program, +9 bytes data |
| **Constant Torque Forced** | 236,274 bytes | 5,817 bytes | +1,562 bytes program, +8 bytes data |

The memory overhead is minimal and well within the available space on the ATmega2560.
- `Firmware/tmc2130.cpp`

Major changes:
- Split `tmc2130_set_wave()` into separate algorithms
- Added `tmc2130_set_wave_constant_torque()` function
- Preserved `tmc2130_set_wave_original()` function
- Updated function calls to use `TMC2130_WAVE_MAX` constant
- Added preprocessor selection logic

## Usage

### Enabling Constant Torque Algorithm

1. **Edit the variant header** for your printer model:
   - For MK3: `Firmware/variants/MK3.h`
   - For MK3S: `Firmware/variants/MK3S.h`

2. **Uncomment the define**:
   ```cpp
   #define TMC2130_CONSTANT_TORQUE_WAVE
   ```

3. **Rebuild the firmware** with your build system

### Algorithm Selection

The algorithm is selected at compile time:

- **Disabled** (default): Uses original Prusa algorithm
  - Power factor range: 1.030 - 1.200
  - Wave minimum: 0
  - Wave maximum: 247
  - Original compression algorithm

- **Enabled**: Uses Bunny Science's constant torque algorithm
  - Power factor range: 0.8 - 1.2 (bidirectional)
  - Wave minimum: 1 (TMC2130_WAVE_SIN0)
  - Wave maximum: 248 (TMC2130_WAVE_MAX)
  - Constant torque maintenance
  - Improved compression with error correction

## Technical Details

### Power Factor Mapping

**Original Algorithm:**
```cpp
fac = (fac1000 + 1000) / 1000  // Range: 1.030 - 1.200
```

**Constant Torque Algorithm:**
```cpp
fac = 0.8 + 0.4 * ((fac1000 - 30) / 170)  // Range: 0.8 - 1.2
```

### Key Improvements

1. **Constant Torque Maintenance:**
   - Calculates torque correction factor `tcorr`
   - Maintains constant total torque throughout wave cycle
   - Uses circle equation for second half of wave

2. **Enhanced Compression:**
   - Adaptive segment switching logic
   - Error correction loop with iterative refinement
   - Better handling of compression artifacts

3. **Bidirectional Correction:**
   - Power factors < 1.0 increase slope near zero crossings
   - Power factors > 1.0 decrease slope near zero crossings
   - More flexible motor tuning options

### Memory Usage

- **Original**: ~100 bytes stack usage
- **Constant Torque**: ~350 bytes stack usage (due to val[257] array)
- **No impact when disabled**: Zero overhead when feature is not enabled

## Testing

The integration includes test programs to verify functionality:

- `test_integration.cpp`: Tests constant torque algorithm
- `test_integration_original.cpp`: Tests original algorithm
- Both verify correct preprocessor behavior and constant values

## Compatibility

- **Backward Compatible**: Existing configurations work unchanged
- **Default Behavior**: Original algorithm remains default
- **No Breaking Changes**: All existing function signatures preserved
- **Conditional Compilation**: No code size impact when disabled

## Recommended Usage

### When to Enable
- Using 0.9° stepper motors (especially beneficial)
- Experiencing VFAs or surface quality issues
- Want smoother motor operation
- Have sufficient RAM for larger stack usage

### When to Keep Disabled
- Using standard 1.8° steppers with good results
- Memory-constrained applications
- Want to maintain exact original behavior
- No print quality issues with current setup

## Future Enhancements

Potential improvements for future versions:
- Runtime algorithm selection via G-code
- Per-axis algorithm configuration
- Additional wave shaping options
- Memory optimization for constant torque algorithm

## Credits

- **Original Algorithm**: Prusa Research
- **Constant Torque Improvements**: bhawkeye (forum user)
- **Simplified Implementation**: Bunny Science (guy.k2)
- **Integration**: Based on Prusa forum discussions and community testing
