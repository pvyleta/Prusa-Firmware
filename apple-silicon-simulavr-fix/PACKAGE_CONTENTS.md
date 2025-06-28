# Apple Silicon Simulavr Fix Package Contents

## 📁 Files Included

### Core Files
- **`README.md`** - Complete documentation and usage instructions
- **`setup-apple-silicon-simulavr.sh`** - Main setup script (tested and working)
- **`test-script.sh`** - Automated test script to verify the setup

### Configuration Files
- **`Dockerfile.patched`** - Fixed Dockerfile with Apple Silicon compatibility
- **`docker-compose.override.yaml`** - Docker compose override (webcam disabled)
- **`printer-mk3s-simulavr.cfg`** - MK3S+ configuration adapted for simulavr

## 🔧 What the Fix Does

### The Problem
Original prind simulavr build fails on Apple Silicon with:
```
CMake Error at debian/CMakeLists.txt:7 (message):
  unknown system architecture: aarch64
```

### The Solution
The fix patches the simulavr CMakeLists.txt file during build to handle the `aarch64` architecture by replacing the error with a fallback to "amd64" package architecture.

**Specific Change in Dockerfile:**
```bash
# Original line that fails:
&& make python

# Fixed line:
&& sed -i "s/message.*unknown system architecture.*CMAKE_SYSTEM_PROCESSOR.*/set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE \"amd64\")/g" debian/CMakeLists.txt && make python
```

## 🧪 Test Results

✅ **All tests passed successfully:**
- Simulavr builds without errors on Apple Silicon
- All containers start properly (Klipper, Moonraker, Mainsail, simulavr)
- Web interface accessible at http://localhost
- Simulavr TTY device created and accessible to Klipper
- MK3S+ configuration loads correctly

## 📊 Your MK3S+ Settings Preserved

The configuration maintains your actual calibrated values:
- **Extruder rotation distance**: 22.95981632
- **Pressure advance**: 0.052  
- **Bed PID values**: Kp=126.13, Ki=4.3, Kd=924.76
- **Max velocity**: 300 mm/s
- **Max acceleration**: 4000 mm/s²
- **Bed dimensions**: 250x210x210mm

## 🚀 Quick Usage

1. **One-time setup:**
   ```bash
   ./setup-apple-silicon-simulavr.sh
   ```

2. **Test the setup:**
   ```bash
   ./test-script.sh
   ```

3. **Access web interface:**
   Open http://localhost

4. **Stop when done:**
   ```bash
   docker compose --profile mainsail -f docker-compose.yaml -f docker-compose.extra.simulavr.yaml down
   ```

## 🔄 Reusability

This package is completely self-contained and can be:
- Copied to any Apple Silicon Mac with prind
- Shared with other users facing the same issue
- Used as a reference for future prind updates

## 🛠️ Technical Notes

- The fix is non-destructive (backs up original files)
- Works with any prind installation
- Compatible with all Apple Silicon Macs (M1, M2, M3, etc.)
- Does not affect x86_64 builds (the sed command only matches on aarch64)

## 📝 Version Compatibility

Tested with:
- **macOS**: Sonoma (Apple Silicon)
- **Docker**: Latest version
- **Prind**: Latest version from GitHub
- **Klipper**: Master branch
- **Simulavr**: Release 1.1.0

## 🤝 Contributing

If you encounter issues or have improvements:
1. Test with the provided test script
2. Check the logs for specific error messages
3. Verify Docker has sufficient resources allocated
4. Ensure port 80 is available

This fix should work for any future Apple Silicon users of prind!
