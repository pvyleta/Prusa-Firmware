#!/usr/bin/env python3

"""
Test script for TMC2130 Linearity Correction Plugin

This script performs basic validation of the plugin functionality
without requiring a full Klipper installation.
"""

import sys
import os
import unittest
import unittest.mock
from unittest.mock import Mock, MagicMock

# Add the current directory to the path so we can import the plugin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the Klipper modules that our plugin depends on
sys.modules['logging'] = Mock()

class TestTMC2130LinearityCorrection(unittest.TestCase):
    """Test cases for the TMC2130 linearity correction plugin"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import the plugin after mocking dependencies
        from tmc2130_linearity import TMC2130LinearityCorrection

        # Create mock objects
        self.mock_printer = Mock()
        self.mock_config = Mock()
        self.mock_gcode = Mock()

        # Configure mock config
        self.mock_config.get_printer.return_value = self.mock_printer
        self.mock_config.get_name.return_value = "tmc2130_linearity stepper_x"
        self.mock_config.has_section.return_value = True
        self.mock_config.getfloat.side_effect = self._mock_getfloat

        # Configure mock printer
        self.mock_printer.lookup_object.return_value = self.mock_gcode
        self.mock_printer.register_event_handler = Mock()

        # Store the class for testing
        self.TMC2130LinearityCorrection = TMC2130LinearityCorrection
    
    def _mock_getfloat(self, key, default=None, minval=None, maxval=None):
        """Mock getfloat method with default values"""
        defaults = {
            'linearity_factor': 1.0
        }
        return defaults.get(key, default)
    
    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly"""
        plugin = self.TMC2130LinearityCorrection(self.mock_config)

        # Check that basic attributes are set
        self.assertEqual(plugin.name, "stepper_x")
        self.assertEqual(plugin.tmc_section_name, "tmc2130 stepper_x")
        self.assertEqual(plugin.linearity_factor, 1000)
    
    def test_linearity_factor_limits(self):
        """Test linearity factor validation"""
        # Test minimum value (1.0 -> 1000 internally)
        self.mock_config.getfloat.side_effect = lambda key, default=None, minval=None, maxval=None: 1.0 if key == 'linearity_factor' else self._mock_getfloat(key, default, minval, maxval)
        plugin = self.TMC2130LinearityCorrection(self.mock_config)
        self.assertEqual(plugin.linearity_factor, 1000)

        # Test maximum value (1.2 -> 1200 internally)
        self.mock_config.getfloat.side_effect = lambda key, default=None, minval=None, maxval=None: 1.2 if key == 'linearity_factor' else self._mock_getfloat(key, default, minval, maxval)
        plugin = self.TMC2130LinearityCorrection(self.mock_config)
        self.assertEqual(plugin.linearity_factor, 1200)

    def test_missing_tmc_section(self):
        """Test error when TMC2130 section is missing"""
        self.mock_config.has_section.return_value = False

        with self.assertRaises(Exception):
            self.TMC2130LinearityCorrection(self.mock_config)
    
    def test_event_handler_registration(self):
        """Test that event handlers are registered"""
        plugin = self.TMC2130LinearityCorrection(self.mock_config)
        
        # Check that event handlers were registered
        self.mock_printer.register_event_handler.assert_any_call("klippy:connect", plugin.handle_connect)
        self.mock_printer.register_event_handler.assert_any_call("klippy:ready", plugin.handle_ready)
    
    def test_gcode_command_registration(self):
        """Test that G-code commands are registered"""
        plugin = self.TMC2130LinearityCorrection(self.mock_config)

        # Check that both Prusa-style G-code commands were registered
        expected_calls = [
            unittest.mock.call(
                "TMC_SET_WAVE_X",
                plugin.cmd_TMC_SET_WAVE,
                desc="Set TMC2130 linearity correction for stepper_x"
            ),
            unittest.mock.call(
                "TMC_SET_STEP_X",
                plugin.cmd_TMC_SET_STEP,
                desc="Move TMC2130 to specific microstep position for stepper_x"
            )
        ]
        self.mock_gcode.register_command.assert_has_calls(expected_calls, any_order=True)

class TestPluginConstants(unittest.TestCase):
    """Test plugin constants and defaults"""

    def test_constants(self):
        """Test that constants are defined correctly"""
        from tmc2130_linearity import (
            AMPLITUDE,
            SIN0,
            MIN_LINEARITY_FACTOR,
            MAX_LINEARITY_FACTOR,
            AXIS_MAPPING
        )

        self.assertEqual(AMPLITUDE, 248)
        self.assertEqual(SIN0, 0)
        self.assertEqual(MIN_LINEARITY_FACTOR, 1000)
        self.assertEqual(MAX_LINEARITY_FACTOR, 1200)
        self.assertEqual(AXIS_MAPPING['stepper_x'], 'X')
        self.assertEqual(AXIS_MAPPING['extruder'], 'E')

def run_tests():
    """Run all tests"""
    print("Running TMC2130 Linearity Correction Plugin Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTMC2130LinearityCorrection))
    suite.addTests(loader.loadTestsFromTestCase(TestPluginConstants))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("All tests passed!")
        return 0
    else:
        print(f"Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
