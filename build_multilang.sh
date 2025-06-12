#!/bin/bash

# Build script for Prusa Firmware multilang builds
# This script sets up the Python environment and builds the firmware

set -e

echo "Setting up Python environment for Prusa Firmware build..."

# Create virtual environment if it doesn't exist
if [ ! -d "lang_env" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv lang_env
fi

# Activate virtual environment and install requirements
echo "Installing Python dependencies..."
source lang_env/bin/activate
pip install -r lang/requirements.txt

# Configure CMake with the virtual environment Python
echo "Configuring CMake..."
cd build
cmake .. -DPython3_EXECUTABLE=$(pwd)/../lang_env/bin/python3

# Build the requested target
TARGET=${1:-MK3S_MULTILANG}
echo "Building target: $TARGET"
cmake --build . --target $TARGET

echo "Build completed successfully!"
echo "Output files:"
ls -la *MULTILANG*.hex 2>/dev/null || echo "No MULTILANG hex files found"
