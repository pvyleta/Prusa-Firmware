# Quick Install Guide

## Prerequisites
- Apple Silicon Mac (M1, M2, M3, etc.)
- Docker Desktop installed and running
- Git (to clone prind)

## Installation Steps

### 1. Clone prind (if you haven't already)
```bash
git clone https://github.com/mkuf/prind
cd prind
```

### 2. Copy this fix package
Copy the entire `apple-silicon-simulavr-fix` folder to your prind directory.

### 3. Run the setup
```bash
./apple-silicon-simulavr-fix/setup-apple-silicon-simulavr.sh
```

### 4. Access the interface
Open http://localhost in your browser

## That's it! 🎉

The script will:
- ✅ Backup your original files
- ✅ Apply the Apple Silicon fix
- ✅ Build simulavr with the patch
- ✅ Start all services
- ✅ Open the web interface

## Test Your MK3S+ Configuration

Once running, try these commands in the Mainsail console:
```gcode
TEST_MK3S_SETTINGS    # Shows your calibrated values
G28                   # Home all axes  
G1 X100 Y100 F18000   # Test movement
M104 S200             # Test temperature
```

## Stop the Services
```bash
docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml down
```

## Troubleshooting

**Build fails?**
- Ensure Docker has enough resources (4GB+ RAM recommended)
- Check that port 80 is not in use

**Web interface not accessible?**
- Wait 30 seconds after startup
- Check `docker ps` to see if containers are running

**Need help?**
- Run `./apple-silicon-simulavr-fix/test-script.sh` for diagnostics
- Check logs: `docker logs prind-simulavr-1`
