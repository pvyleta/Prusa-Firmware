#!/bin/bash

# Apple Silicon Simulavr Fix for Prind
# This script sets up prind with simulavr support on Apple Silicon Macs

set -e  # Exit on any error

echo "🍎 Setting up Apple Silicon Simulavr Fix for Prind..."
echo "=================================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRIND_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 Script directory: $SCRIPT_DIR"
echo "📁 Prind directory: $PRIND_DIR"

# Change to prind directory
cd "$PRIND_DIR"

echo ""
echo "🔧 Step 1: Backing up original files..."
# Backup original files if they exist
if [ -f "docker/klipper/Dockerfile" ]; then
    cp docker/klipper/Dockerfile docker/klipper/Dockerfile.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backed up original Dockerfile"
fi

if [ -f "docker-compose.override.yaml" ]; then
    cp docker-compose.override.yaml docker-compose.override.yaml.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backed up original docker-compose.override.yaml"
fi

echo ""
echo "🔧 Step 2: Applying Apple Silicon patch to Dockerfile..."
# Apply the patched Dockerfile
cp "$SCRIPT_DIR/Dockerfile.patched" docker/klipper/Dockerfile
echo "✅ Applied Apple Silicon patch to Dockerfile"

echo ""
echo "🔧 Step 3: Setting up configuration files..."
# Copy the MK3S+ simulavr configuration
cp "$SCRIPT_DIR/printer-mk3s-simulavr.cfg" config/
echo "✅ Created MK3S+ simulavr configuration"

# Copy the docker-compose override (webcam disabled)
cp "$SCRIPT_DIR/docker-compose.override.yaml" .
echo "✅ Updated docker-compose override (webcam disabled)"

echo ""
echo "🔧 Step 4: Stopping any existing containers..."
# Stop any existing containers
docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml down 2>/dev/null || true
echo "✅ Stopped existing containers"

echo ""
echo "🔧 Step 5: Building simulavr with Apple Silicon fix..."
echo "⏳ This may take several minutes..."
# Build the simulavr image with the fix
docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml build --no-cache simulavr

if [ $? -eq 0 ]; then
    echo "✅ Successfully built simulavr with Apple Silicon fix!"
else
    echo "❌ Failed to build simulavr. Check the error messages above."
    exit 1
fi

echo ""
echo "🔧 Step 6: Starting the complete stack..."
# Start the stack
docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml up -d

if [ $? -eq 0 ]; then
    echo "✅ Successfully started the stack!"
else
    echo "❌ Failed to start the stack. Check the error messages above."
    exit 1
fi

echo ""
echo "🔧 Step 7: Waiting for services to start..."
sleep 10

echo ""
echo "🔧 Step 8: Checking service status..."
# Check if simulavr is running
if docker ps | grep -q "prind-simulavr-1"; then
    echo "✅ Simulavr is running"
else
    echo "⚠️  Simulavr may not be running properly"
fi

# Check if klipper is running
if docker ps | grep -q "prind-klipper-1"; then
    echo "✅ Klipper is running"
else
    echo "⚠️  Klipper may not be running properly"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "🌐 Web Interface: http://localhost"
echo ""
echo "🧪 Test Commands:"
echo "   - TEST_MK3S_SETTINGS  (displays your calibrated values)"
echo "   - G28                 (home all axes)"
echo "   - G1 X100 Y100 F18000 (test movement)"
echo "   - M104 S200           (test temperature)"
echo ""
echo "📊 Your MK3S+ Settings Being Tested:"
echo "   - Extruder rotation distance: 22.95981632"
echo "   - Pressure advance: 0.052"
echo "   - Bed PID: Kp=126.13, Ki=4.3, Kd=924.76"
echo "   - Max velocity: 300 mm/s"
echo "   - Max acceleration: 4000 mm/s²"
echo ""
echo "🛑 To stop: docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml down"
echo ""
echo "📋 Check logs if needed:"
echo "   - docker logs prind-simulavr-1"
echo "   - docker logs prind-klipper-1"
echo ""

# Try to open the browser
if command -v open >/dev/null 2>&1; then
    echo "🌐 Opening web interface..."
    open http://localhost
elif command -v xdg-open >/dev/null 2>&1; then
    echo "🌐 Opening web interface..."
    xdg-open http://localhost
else
    echo "🌐 Please open http://localhost in your browser"
fi

echo "✨ Apple Silicon Simulavr setup is complete!"
