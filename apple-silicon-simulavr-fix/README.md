# Apple Silicon Simulavr Fix for Prind

This folder contains all the necessary files and scripts to run prind with simulavr on Apple Silicon Macs.

## Problem Solved

The original prind simulavr build fails on Apple Silicon (ARM64) with this error:
```
CMake Error at debian/CMakeLists.txt:7 (message):
  unknown system architecture: aarch64
```

## Solution

This fix patches the simulavr build process to handle the `aarch64` architecture by modifying the CMake configuration.

## Files Included

- `README.md` - This documentation
- `setup-apple-silicon-simulavr.sh` - Main setup script
- `Dockerfile.patched` - Fixed Dockerfile for Apple Silicon
- `docker-compose.override.yaml` - Webcam disabled for testing
- `printer-mk3s-simulavr.cfg` - MK3S+ configuration for simulavr testing
- `test-script.sh` - Script to test the setup

## Quick Start

1. **Run the setup script:**
   ```bash
   ./setup-apple-silicon-simulavr.sh
   ```

2. **Access the web interface:**
   Open http://localhost in your browser

3. **Test your MK3S+ configuration:**
   - Run `TEST_MK3S_SETTINGS` macro in the console
   - Test movements: `G28`, `G1 X100 Y100 F18000`
   - Test temperatures: `M104 S200`, `M140 S60`

## What the Setup Script Does

1. Backs up original files
2. Applies the Apple Silicon patch to the Dockerfile
3. Creates the MK3S+ simulavr configuration
4. Disables webcam service (not needed for testing)
5. Builds the simulavr image with the fix
6. Starts the complete stack (Klipper + Moonraker + Mainsail + simulavr)

## Manual Steps (if needed)

If you prefer to apply changes manually:

1. **Patch the Dockerfile:**
   ```bash
   cp docker/klipper/Dockerfile docker/klipper/Dockerfile.backup
   cp apple-silicon-simulavr-fix/Dockerfile.patched docker/klipper/Dockerfile
   ```

2. **Create the configuration:**
   ```bash
   cp apple-silicon-simulavr-fix/printer-mk3s-simulavr.cfg config/
   ```

3. **Update docker-compose override:**
   ```bash
   cp apple-silicon-simulavr-fix/docker-compose.override.yaml .
   ```

4. **Build and start:**
   ```bash
   docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml build --no-cache simulavr
   docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml up -d
   ```

## Testing Your Configuration

Once running, you can test your MK3S+ settings:

- **Extruder rotation distance**: 22.95981632
- **Pressure advance**: 0.052
- **Bed PID values**: Kp=126.13, Ki=4.3, Kd=924.76
- **Max velocity**: 300 mm/s
- **Max acceleration**: 4000 mm/s²

## Stopping the Stack

```bash
docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml down
```

## Troubleshooting

- **Build fails**: Make sure Docker has enough resources allocated
- **Can't access web interface**: Check that port 80 is not in use
- **Simulavr not connecting**: Check logs with `docker logs prind-simulavr-1`

## Technical Details

The fix modifies the simulavr CMakeLists.txt to replace the architecture error with a fallback to "amd64" package architecture, which works fine for the simulation purposes on Apple Silicon.
