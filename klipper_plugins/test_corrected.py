import math

# Constants
SIN0 = 0
AMPLITUDE = 248
MIDPOINT_VALUE = 175.362481734263781
SIN_127_5 = 0.704934080375905

def generate_corrected_wave(linearity_factor):
    wave_table = [0] * 256
    factor = linearity_factor / 1000.0
    
    # Calculate tcorr
    tcorr = MIDPOINT_VALUE / ((AMPLITUDE - SIN0) * pow(SIN_127_5, factor))
    TARGET_MAGNITUDE_SQUARED = AMPLITUDE * AMPLITUDE + SIN0 * SIN0
    
    for i in range(256):
        if i < 128:
            sin_val = math.sin(math.pi * i / 512.0)
            theoretical_value = (AMPLITUDE - SIN0) * pow(sin_val, factor) * tcorr + SIN0
            wave_table[i] = int(theoretical_value + 0.5)
        else:
            mirror_i = 255 - i
            sin_val = math.sin(math.pi * mirror_i / 512.0)
            mirror_theoretical = (AMPLITUDE - SIN0) * pow(sin_val, factor) * tcorr + SIN0
            theoretical_value = math.sqrt(TARGET_MAGNITUDE_SQUARED - mirror_theoretical * mirror_theoretical)
            wave_table[i] = int(theoretical_value + 0.5)
    
    return wave_table

# Test corrected algorithm
print("Corrected algorithm values for factor 1.1:")
corrected_table = generate_corrected_wave(1100)
print("Index\tValue")
for i in [0, 32, 64, 96, 127, 128, 160, 192, 224, 255]:
    print(f"{i}\t{corrected_table[i]}")
