# Deprecated Dependencies on Raspberry Pi 4

This document lists deprecated dependencies and compatibility issues found in the codebase for Raspberry Pi 4.

## Fixed Issues

### 1. ✅ pyserial Deprecated Methods (FIXED)

**Issue**: The following pyserial methods are deprecated in pyserial 3.0+:
- `.isOpen()` → Should use `.is_open` property
- `.inWaiting()` → Should use `.in_waiting` property

**Files Updated**:
- `printer_connection.py` - Fixed all instances
- `3dprinter_connection.py` - Fixed `.isOpen()` usage
- `3dprinter_start_experiment.py` - Fixed `.isOpen()` usage

**Status**: ✅ All deprecated pyserial methods have been replaced with modern equivalents.

### 2. ✅ picamera → picamera2 Migration (COMPLETED)

**Issue**: The original `picamera` library is deprecated on Raspberry Pi 4. picamera2 is the official replacement.

**Status**: ✅ Migration completed. All camera code now uses picamera2.

## Potential Compatibility Notes

### 3. ⚠️ Xlib Dependency

**Location**: `3dprinter_sampler_gui_fly2.py` uses `from Xlib.display import Display`

**Status**: 
- Xlib should work fine on Raspberry Pi OS (which uses X11 by default)
- **Potential Issue**: If Raspberry Pi OS switches to Wayland in the future, Xlib will not work
- **Recommendation**: Monitor for Wayland migration. If needed, consider alternatives like:
  - Using picamera2's DRM preview (doesn't require X11)
  - Using window management libraries that support both X11 and Wayland

**Current Action**: No changes needed, but be aware of potential future compatibility issues.

### 4. ✅ YAML Loading (CORRECT)

**Status**: The codebase correctly uses `yaml.load(file, Loader=yaml.FullLoader)` which is the modern, safe way to load YAML files. This is NOT deprecated.

### 5. ✅ Other Dependencies

The following dependencies are current and should work fine on Raspberry Pi 4:
- **FreeSimpleGUI** - Active fork of PySimpleGUI, compatible with Pi 4
- **OpenCV (cv2)** - Fully supported on Pi 4
- **pandas** - Fully supported on Pi 4
- **parse library** - Still maintained, compatible with Pi 4
- **pyserial** - Fully supported (deprecated methods have been fixed)

## Summary

All critical deprecated dependencies have been addressed:
1. ✅ picamera → picamera2 migration completed
2. ✅ pyserial deprecated methods fixed
3. ⚠️ Xlib dependency noted for future monitoring

The codebase should now be fully compatible with Raspberry Pi 4.
