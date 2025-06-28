; Test G-code for MK3S+ configuration validation
; This tests basic movements and your calibrated settings

; Start G-code
G21 ; Set units to millimeters
G90 ; Use absolute coordinates
M83 ; Use relative distances for extrusion

; Home all axes
G28

; Heat bed and nozzle (will be simulated)
M140 S60 ; Set bed temperature
M104 S200 ; Set nozzle temperature
M190 S60 ; Wait for bed temperature
M109 S200 ; Wait for nozzle temperature

; Move to start position
G1 X10 Y10 Z0.3 F3000

; Test your pressure advance setting
G1 E5 F300 ; Prime extruder
G1 X50 Y10 E2 F1500 ; Line 1 - tests your rotation_distance
G1 X50 Y50 E2 F1500 ; Line 2
G1 X10 Y50 E2 F1500 ; Line 3
G1 X10 Y10 E2 F1500 ; Line 4

; Test max velocity and acceleration
G1 Z10 F600
G1 X100 Y100 F18000 ; Test max velocity (300mm/s = 18000mm/min)

; Test acceleration limits
G1 X200 Y100 F18000
G1 X100 Y100 F18000
G1 X200 Y100 F18000

; End G-code
G1 Z50 F600
G1 X0 Y200 F3000
M104 S0 ; Turn off nozzle heater
M140 S0 ; Turn off bed heater
M84 ; Disable steppers

; Test complete
