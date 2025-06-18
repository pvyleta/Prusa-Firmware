import math

# Prusa constants
PRUSA_SIN0 = 0
PRUSA_AMP = 248
PRUSA_MIDPOINT_VALUE = 175.362481734263781
PRUSA_SIN_127_5 = 0.704934080375905

def prusa_calc(i, fac, tcorr):
    if i < 128:
        sin_val = math.sin(math.pi * i / 512.0)
        return int((PRUSA_AMP - PRUSA_SIN0) * pow(sin_val, fac) * tcorr + PRUSA_SIN0 + 0.5)
    else:
        mirror_i = 255 - i
        sin_val = math.sin(math.pi * mirror_i / 512.0)
        mirror_val = (PRUSA_AMP - PRUSA_SIN0) * pow(sin_val, fac) * tcorr + PRUSA_SIN0
        return int(math.sqrt(PRUSA_AMP * PRUSA_AMP + PRUSA_SIN0 * PRUSA_SIN0 - mirror_val * mirror_val) + 0.5)

# Test factor 1.1
fac = 1.1
tcorr = PRUSA_MIDPOINT_VALUE / ((PRUSA_AMP - PRUSA_SIN0) * pow(PRUSA_SIN_127_5, fac))

print("Prusa algorithm values for factor 1.1:")
print("Index\tValue")
for i in [0, 32, 64, 96, 127, 128, 160, 192, 224, 255]:
    val = prusa_calc(i, fac, tcorr)
    print(f"{i}\t{val}")

print(f"\nTcorr: {tcorr}")
print(f"Midpoint (127): {prusa_calc(127, fac, tcorr)}")
