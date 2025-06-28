#!/bin/bash

# Test script for Apple Silicon Simulavr Fix
# This script tests the setup by running it from scratch

set -e  # Exit on any error

echo "🧪 Testing Apple Silicon Simulavr Fix..."
echo "========================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRIND_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 Script directory: $SCRIPT_DIR"
echo "📁 Prind directory: $PRIND_DIR"

# Change to prind directory
cd "$PRIND_DIR"

echo ""
echo "🧹 Step 1: Cleaning up any existing setup..."
# Stop and remove any existing containers
docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml down 2>/dev/null || true

# Remove simulavr image to force rebuild
docker rmi simulavr:latest 2>/dev/null || true
echo "✅ Cleaned up existing setup"

echo ""
echo "🔄 Step 2: Restoring original files..."
# Restore original Dockerfile if backup exists
if [ -f "docker/klipper/Dockerfile.bak" ]; then
    cp docker/klipper/Dockerfile.bak docker/klipper/Dockerfile
    echo "✅ Restored original Dockerfile"
fi

echo ""
echo "🚀 Step 3: Running the setup script..."
# Run the setup script
chmod +x "$SCRIPT_DIR/setup-apple-silicon-simulavr.sh"
"$SCRIPT_DIR/setup-apple-silicon-simulavr.sh"

echo ""
echo "🔍 Step 4: Verifying the setup..."
sleep 15  # Give services time to fully start

# Check if all containers are running
echo "📊 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep prind || echo "No prind containers found"

echo ""
echo "🔍 Step 5: Testing simulavr connection..."
# Check simulavr logs for successful startup
if docker logs prind-simulavr-1 2>/dev/null | grep -q "Starting AVR simulation"; then
    echo "✅ Simulavr is running and simulating AVR"
else
    echo "❌ Simulavr may not be working properly"
    echo "Simulavr logs:"
    docker logs prind-simulavr-1 2>/dev/null | tail -10 || echo "Could not get simulavr logs"
fi

echo ""
echo "🔍 Step 6: Testing web interface..."
# Test if web interface is accessible
if curl -s http://localhost >/dev/null 2>&1; then
    echo "✅ Web interface is accessible at http://localhost"
else
    echo "❌ Web interface is not accessible"
fi

echo ""
echo "🔍 Step 7: Testing Klipper connection..."
# Check if Klipper is connected to simulavr
sleep 5
if docker exec prind-klipper-1 ls /opt/printer_data/run/simulavr.tty 2>/dev/null; then
    echo "✅ Simulavr TTY device exists"
else
    echo "❌ Simulavr TTY device not found"
fi

echo ""
echo "📋 Test Results Summary:"
echo "========================"

# Final status check
SIMULAVR_RUNNING=$(docker ps | grep -c "prind-simulavr-1" || echo "0")
KLIPPER_RUNNING=$(docker ps | grep -c "prind-klipper-1" || echo "0")
MOONRAKER_RUNNING=$(docker ps | grep -c "prind-moonraker-1" || echo "0")
MAINSAIL_RUNNING=$(docker ps | grep -c "prind-mainsail-1" || echo "0")

echo "Simulavr:  $([ "$SIMULAVR_RUNNING" -eq 1 ] && echo "✅ Running" || echo "❌ Not running")"
echo "Klipper:   $([ "$KLIPPER_RUNNING" -eq 1 ] && echo "✅ Running" || echo "❌ Not running")"
echo "Moonraker: $([ "$MOONRAKER_RUNNING" -eq 1 ] && echo "✅ Running" || echo "❌ Not running")"
echo "Mainsail:  $([ "$MAINSAIL_RUNNING" -eq 1 ] && echo "✅ Running" || echo "❌ Not running")"

echo ""
if [ "$SIMULAVR_RUNNING" -eq 1 ] && [ "$KLIPPER_RUNNING" -eq 1 ] && [ "$MOONRAKER_RUNNING" -eq 1 ] && [ "$MAINSAIL_RUNNING" -eq 1 ]; then
    echo "🎉 TEST PASSED: All services are running!"
    echo ""
    echo "🌐 Open http://localhost to access the interface"
    echo "🧪 Try these test commands in the Mainsail console:"
    echo "   TEST_MK3S_SETTINGS"
    echo "   G28"
    echo "   G1 X100 Y100 F18000"
else
    echo "❌ TEST FAILED: Some services are not running properly"
    echo ""
    echo "🔍 Check logs with:"
    echo "   docker logs prind-simulavr-1"
    echo "   docker logs prind-klipper-1"
    echo "   docker logs prind-moonraker-1"
fi

echo ""
echo "🛑 To stop all services:"
echo "   docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml down"
