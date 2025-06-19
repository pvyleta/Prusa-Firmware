#include <iostream>
#include <iomanip>
#include <cmath>
#include <cstdint>

#define TMC2130_WAVE_FAC1000_MIN 100
#define TMC2130_WAVE_FAC1000_MAX 1200
#define TMC2130_WAVE_ALGORITHM_CONSTANT_TORQUE 1
#define EEPROM_TMC2130_WAVE_ALGORITHM 0x1234

uint8_t mock_eeprom_algorithm = TMC2130_WAVE_ALGORITHM_CONSTANT_TORQUE;

uint8_t eeprom_read_byte(uint8_t* addr) {
    return mock_eeprom_algorithm;
}

void tmc2130_wr_MSLUTSTART(uint8_t axis, uint8_t start_sin, uint8_t start_sin90) {
    std::cout << "MSLUTSTART: start_sin=" << (int)start_sin << ", start_sin90=" << (int)start_sin90 << std::endl;
}

void tmc2130_wr_MSLUT(uint8_t axis, uint8_t address, uint32_t data) {
    std::cout << "MSLUT" << (int)address << " = 0x" << std::hex << std::setw(8) << std::setfill('0') << data << std::dec << std::endl;
}

void tmc2130_wr_MSLUTSEL(uint8_t axis, uint8_t x1, uint8_t x2, uint8_t x3, uint8_t w0, uint8_t w1, uint8_t w2, uint8_t w3) {
    std::cout << "MSLUTSEL: x1=" << (int)x1 << ", x2=" << (int)x2 << ", x3=" << (int)x3 
              << ", w0=" << (int)w0 << ", w1=" << (int)w1 << ", w2=" << (int)w2 << ", w3=" << (int)w3 << std::endl;
}

uint8_t tmc2130_calc_constant_torque_value(uint8_t i, uint8_t va, float fac, float tcorr,
                                          float& carry, float& prev_theoretical_value) {
    constexpr uint8_t SIN0 = 0;
    constexpr uint8_t AMP = 248;
    constexpr float TARGET_MAGNITUDE_SQUARED = (float)AMP * AMP + (float)SIN0 * SIN0;

    float theoretical_value;

    if (i < 128) {
        float sin_val = sin(M_PI * (float)i / 512.0f);
        theoretical_value = (AMP - SIN0) * pow(sin_val, fac) * tcorr + SIN0;
    } else {
        uint8_t mirror_i = 255 - i;
        float sin_val = sin(M_PI * (float)mirror_i / 512.0f);
        float mirror_theoretical = (AMP - SIN0) * pow(sin_val, fac) * tcorr + SIN0;
        theoretical_value = sqrt(TARGET_MAGNITUDE_SQUARED - mirror_theoretical * mirror_theoretical);
    }

    float adjusted_theoretical = theoretical_value - carry;
    uint8_t candidate_value = (uint8_t)(adjusted_theoretical + 0.5);

    float slope = theoretical_value - prev_theoretical_value;
    int8_t min_delta = (int8_t)floor(slope);

    if (min_delta < -1) {
        min_delta = -1;
    } else if (min_delta > 2) {
        min_delta = 2;
    }

    int8_t delta = candidate_value - va;
    if (delta < min_delta) {
        candidate_value = va + min_delta;
    } else if (delta > min_delta + 1) {
        candidate_value = va + min_delta + 1;
    }

    if (candidate_value < SIN0) {
        candidate_value = SIN0;
    } else if (candidate_value > AMP) {
        candidate_value = AMP;
    }

    carry = candidate_value - theoretical_value;
    prev_theoretical_value = theoretical_value;

    return candidate_value;
}

// Fixed to use uint16_t for fac1000 parameter
void tmc2130_set_wave(uint8_t axis, uint8_t amp, uint16_t fac1000) {
    std::cout << "=== PRUSA C++ tmc2130_set_wave ===" << std::endl;
    std::cout << "axis=" << (int)axis << ", amp=" << (int)amp << ", fac1000=" << (int)fac1000 << std::endl;
    
    if (fac1000 < TMC2130_WAVE_FAC1000_MIN) fac1000 = 0;
    if (fac1000 > TMC2130_WAVE_FAC1000_MAX) fac1000 = TMC2130_WAVE_FAC1000_MAX;
    float fac = 1;
    if (fac1000) fac = ((float)((uint16_t)fac1000 + 1000) / 1000);
    
    std::cout << "Calculated fac = " << fac << std::endl;
    
    uint8_t vA = 0;
    uint8_t va = 0;
    int8_t d0 = 0;
    int8_t d1 = 1;
    uint8_t w[4] = {1,1,1,1};
    uint8_t x[3] = {255,255,255};
    uint8_t s = 0;
    int8_t b;
    int8_t dA;
    uint8_t i = 0;
    uint32_t reg = 0;

    float carry = 0.0;
    float prev_theoretical_value = 0.0;
    float tcorr = 1.0;

    uint8_t algorithm = eeprom_read_byte((uint8_t*)EEPROM_TMC2130_WAVE_ALGORITHM);
    bool use_constant_torque = (algorithm == TMC2130_WAVE_ALGORITHM_CONSTANT_TORQUE);

    if (use_constant_torque) {
        constexpr uint8_t SIN0 = 0;
        constexpr uint8_t AMP = 248;
        constexpr float MIDPOINT_VALUE = 175.362481734263781f;
        constexpr float SIN_127_5 = 0.704934080375905f;

        tcorr = (MIDPOINT_VALUE - SIN0) / ((AMP - SIN0) * pow(SIN_127_5, fac));
        std::cout << "Calculated tcorr = " << tcorr << std::endl;
        tmc2130_wr_MSLUTSTART(axis, SIN0, AMP);
    } else {
        tmc2130_wr_MSLUTSTART(axis, 0, amp);
    }

    std::cout << "\nWave table values:" << std::endl;
    
    do {
        if ((i & 0x1f) == 0)
            reg = 0;

        if (use_constant_torque) {
            vA = tmc2130_calc_constant_torque_value(i, va, fac, tcorr, carry, prev_theoretical_value);
        } else {
            if (fac == 1)
                vA = (uint8_t)((amp+1) * sin((2*M_PI*i + M_PI)/1024) + 0.5) - 1;
            else
                vA = (uint8_t)(amp * pow(sin(2*M_PI*i/1024), fac) + 0.5);
        }

        if (i < 20 || i > 235) {
            std::cout << "wave[" << std::setw(3) << (int)i << "] = " << std::setw(3) << (int)vA << std::endl;
        } else if (i == 20) {
            std::cout << "... (wave values 20-235 omitted) ..." << std::endl;
        }

        dA = vA - va;
        va = vA;
        b = -1;
        if (dA == d0) b = 0;
        else if (dA == d1) b = 1;
        else {
            if (dA < d0) {
                b = 0;
                switch (dA) {
                case -1: d0 = -1; d1 = 0; w[s+1] = 0; break;
                case  0: d0 =  0; d1 = 1; w[s+1] = 1; break;
                case  1: d0 =  1; d1 = 2; w[s+1] = 2; break;
                default: b = -1; break;
                }
                if (b >= 0) { x[s] = i; s++; }
            }
            else if (dA > d1) {
                b = 1;
                switch (dA) {
                case  1: d0 =  0; d1 = 1; w[s+1] = 1; break;
                case  2: d0 =  1; d1 = 2; w[s+1] = 2; break;
                case  3: d0 =  2; d1 = 3; w[s+1] = 3; break;
                default: b = -1; break;
                }
                if (b >= 0) { x[s] = i; s++; }
            }
        }
        if (b < 0) break;
        if (s > 3) break;
        
        if (b == 1) reg |= 0x80000000;
        if ((i & 31) == 31)
            tmc2130_wr_MSLUT(axis, (uint8_t)(i >> 5), reg);
        else
            reg >>= 1;
    } while (i++ != 255);
    
    tmc2130_wr_MSLUTSEL(axis, x[0], x[1], x[2], w[0], w[1], w[2], w[3]);
    std::cout << "=== END PRUSA C++ ===" << std::endl;
}

int main() {
    std::cout << "PRUSA FIRMWARE C++ VERIFICATION (FIXED)" << std::endl;
    std::cout << "=======================================" << std::endl;
    
    tmc2130_set_wave(0, 248, 1100);
    
    return 0;
}
