# Standard Operating Procedure (SOP)
## Setting Up and Running ColorCamControl on Raspberry Pi 4

**Version:** 1.0  
**Date:** 2025  
**Target Platform:** Raspberry Pi 4 running Raspberry Pi OS (Bookworm or later)

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial System Setup](#initial-system-setup)
3. [Virtual Environment Setup](#virtual-environment-setup)
4. [Installing Dependencies](#installing-dependencies)
5. [Hardware Configuration](#hardware-configuration)
6. [Software Configuration](#software-configuration)
7. [Running the Application](#running-the-application)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements
- Raspberry Pi 4 (4GB RAM minimum recommended)
- Raspberry Pi Camera Module (compatible with picamera2)
- 3D Printer connected via USB (serial connection)
- MicroSD card (32GB+ recommended)
- Power supply (official Raspberry Pi 4 power supply recommended)
- Monitor, keyboard, and mouse (for initial setup)

### Software Requirements
- Raspberry Pi OS (Bookworm or later) - Desktop version recommended
- Python 3.9 or later
- Internet connection for package installation

---

## Initial System Setup

### Step 1: Install Raspberry Pi OS

1. Download Raspberry Pi Imager from [raspberrypi.com](https://www.raspberrypi.com/software/)
2. Flash Raspberry Pi OS (Desktop) to your microSD card
3. Boot your Raspberry Pi 4
4. Complete the initial setup wizard

### Step 2: Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

### Step 3: Enable Camera Interface

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options** → **Camera** → **Enable**

Reboot after enabling:
```bash
sudo reboot
```

### Step 4: Install System Dependencies for picamera2

```bash
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    libcamera-dev \
    libcamera-apps \
    libcap-dev \
    libatlas-base-dev \
    ffmpeg \
    libopenjp2-7 \
    libkms++-dev \
    libfmt-dev \
    libdrm-dev
```

**Note:** `libcamera-apps` provides the camera test commands. On current Raspberry Pi OS the command is `rpicam-hello`; on older releases it may be `libcamera-hello`. If you get "command not found" when testing, install: `sudo apt install libcamera-apps`

---

## Virtual Environment Setup

### Step 1: Navigate to Project Directory

```bash
cd ~
mkdir -p Projects
cd Projects
```

### Step 2: Clone or Copy Project Files

If using git:
```bash
git clone <repository-url> ColorCamControl
cd ColorCamControl
```

Or copy your project files to `~/Projects/ColorCamControl/`

### Step 3: Create Virtual Environment

**Recommended Approach (using system-site-packages):**

```bash
python3 -m venv --system-site-packages venv
```

This allows the virtual environment to access system-installed packages like picamera2, which is the recommended method according to Raspberry Pi forums.

**Alternative Approach (isolated venv - not recommended):**

If you need an isolated environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel
pip install rpi-libcamera rpi-kms picamera2
```

### Step 4: Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

## Installing Dependencies

### Step 1: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FreeSimpleGUI (GUI framework)
- opencv-python-headless (computer vision; headless avoids Qt conflict with picamera2 preview)
- numpy (numerical computing)
- pyserial (serial communication)
- PyYAML (configuration files)
- parse (string parsing)
- python-xlib (window management)
- pandas (data processing)
- Pillow (image processing)

### Step 3: Use OpenCV headless (fix Qt / camera preview conflict)

If you have or had `opencv-python` installed, use the headless build so the camera preview works without Qt errors:

```bash
pip uninstall opencv-python -y
pip install opencv-python-headless
```

If you install from `requirements.txt` only, you will get `opencv-python-headless` by default. Run the commands above if you see: *"Could not load the Qt platform plugin xcb"* when starting the camera preview.

### Step 4: Verify picamera2 Installation

```bash
python3 -c "from picamera2 import Picamera2; print('picamera2 is available')"
```

If you get an error, ensure you used `--system-site-packages` when creating the venv, or install picamera2 manually as shown in the alternative approach above.

---

## Hardware Configuration

### Step 1: Connect Camera Module

1. Power off the Raspberry Pi
2. Connect the camera module to the CSI port
3. Ensure the ribbon cable is inserted correctly (contacts facing away from the Ethernet port)
4. Power on the Raspberry Pi

### Step 2: Connect 3D Printer

1. Connect your 3D Printer via USB cable
2. Identify the device path:
   ```bash
   ls -l /dev/ttyUSB* /dev/ttyACM*
   ```
   
   Common device paths:
   - `/dev/ttyUSB0` - USB-to-serial adapters
   - `/dev/ttyACM0` - USB CDC devices (some printers)

3. Add your user to the dialout group (if needed):
   ```bash
   sudo usermod -a -G dialout $USER
   ```
   Log out and back in for this to take effect.

### Step 3: Test Camera

**If you get "command not found"**, install the camera apps package first:
```bash
sudo apt install libcamera-apps
```

Then run (use `rpicam-hello` on current Raspberry Pi OS; older releases may use `libcamera-hello`):
```bash
rpicam-hello --list-cameras
rpicam-hello --timeout 5000
```

If the camera works, you should see a preview window (or camera info from the first command).

---

## Software Configuration

### Step 1: Configure Printer Settings

Edit `connection_settings.yaml` to match your 3D printer:

```yaml
FlyCamV2:
    Creality:
      name: Ender 3
      device_path: /dev/ttyUSB0  # Change to your device path
      baudrate: 115200            # Change to your printer's baudrate
      timeout_time: 1
      reboot_wait_time: 8
      camera_rotation: 180        # Adjust as needed (0, 90, 180, 270)
      max:
        x: 220                    # Your printer's max X dimension (mm)
        y: 220                    # Your printer's max Y dimension (mm)
        z: 220                    # Your printer's max Z dimension (mm)
        speed: 70                 # Max travel speed (mm/sec)
```

### Step 2: Configure Project Settings

Edit `settings.py` if needed:

```python
PROJECT = "FlyCamV2"  # Must match a key in connection_settings.yaml
```

### Step 3: Set Permissions (if needed)

If you encounter permission errors:

```bash
sudo chmod 666 /dev/ttyUSB0  # Replace with your device path
```

Or better, add a udev rule:

```bash
sudo nano /etc/udev/rules.d/99-3dprinter.rules
```

Add:
```
SUBSYSTEM=="tty", ATTRS{idVendor}=="YOUR_VENDOR_ID", MODE="0666"
```

Find vendor ID:
```bash
lsusb
```

---

## Running the Application

### Step 1: Activate Virtual Environment

```bash
cd ~/Projects/ColorCamControl
source venv/bin/activate
```

### Step 2: Run the Main GUI Application

**Primary GUI (recommended):**
```bash
python3 3dprinter_sampler_gui_fly2.py
```

**Alternative GUI:**
```bash
python3 3dprinter_sampler_gui.py
```

**Camera Settings Tab (standalone):**
```bash
python3 camera_tab.py
```

### Step 3: Using the Application

1. **Start Experiment Tab:**
   - Click "Open CSV" to load a location file
   - Select experiment mode (Picture/Video/Preview)
   - Click "Start Experiment"

2. **Movement Tab:**
   - Use relative movement controls to position the printer
   - Use "Get Current Location" to verify position

3. **Camera Tab:**
   - Adjust camera rotation
   - Set image capture resolution
   - Choose save folder

### Step 4: Deactivate Virtual Environment (when done)

```bash
deactivate
```

---

## Troubleshooting

### Camera Issues

**Problem:** `rpicam-hello` or `libcamera-hello`: command not found
```bash
# Install the libcamera-apps package (provides rpicam-hello / libcamera-hello)
sudo apt install libcamera-apps
```

**Problem:** Camera not detected
```bash
# Install libcamera-apps if you haven't, then check camera connection
sudo apt install libcamera-apps
rpicam-hello --list-cameras

# Check if camera is enabled
sudo raspi-config  # Interface Options → Camera
```

**Problem:** picamera2 import error in venv
- Ensure you used `--system-site-packages` when creating venv
- Or install picamera2 manually: `pip install rpi-libcamera rpi-kms picamera2`

### Serial Port Issues

**Problem:** Permission denied on `/dev/ttyUSB0`
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

**Problem:** Device not found
```bash
# List all serial devices
ls -l /dev/tty*

# Check if device is connected
dmesg | tail
```

### GUI Issues

**Problem:** Xlib errors (window management)
- Ensure you're running on Raspberry Pi OS Desktop (X11)
- Xlib doesn't work with Wayland (if Pi OS switches to Wayland in future)

**Problem:** FreeSimpleGUI not displaying correctly
```bash
# Reinstall FreeSimpleGUI
pip install --upgrade FreeSimpleGUI
```

### Python Version Issues

**Problem:** Python version too old
```bash
python3 --version  # Should be 3.9+
# If not, update Raspberry Pi OS
sudo apt update && sudo apt upgrade
```

### Dependency Installation Issues

**Problem:** pip install fails
```bash
# Upgrade pip
pip install --upgrade pip

# Install build dependencies
sudo apt install python3-dev build-essential
```

### Preview Window Issues

**Note:** picamera2 preview handling differs from picamera1. Window positioning may not work exactly as before. Preview windows in picamera2 typically use DRM or Qt rendering, not X11 window coordinates.

**Problem:** *"Could not load the Qt platform plugin xcb"* or *"This application failed to start because no Qt platform plugin could be initialized"* when starting the camera preview.

Use the OpenCV headless package so Qt from OpenCV does not conflict with picamera2:

```bash
pip uninstall opencv-python -y
pip install opencv-python-headless
```

Then run the application again. The main GUI uses FreeSimpleGUI and picamera2 for the camera; it does not need OpenCV’s GUI (e.g. `cv2.imshow`).

---

## Quick Start Checklist

- [ ] Raspberry Pi OS installed and updated
- [ ] Camera interface enabled via raspi-config
- [ ] System dependencies installed
- [ ] Virtual environment created with `--system-site-packages`
- [ ] Virtual environment activated
- [ ] Python dependencies installed from requirements.txt
- [ ] picamera2 verified working
- [ ] 3D printer connected and device path identified
- [ ] connection_settings.yaml configured for your printer
- [ ] User added to dialout group (if needed)
- [ ] Application runs successfully

---

## Additional Resources

- [picamera2 Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Raspberry Pi Camera Forum](https://forums.raspberrypi.com/viewforum.php?f=43)
- [picamera2 in Virtual Environments](https://forums.raspberrypi.com/viewtopic.php?t=361758)
- [FreeSimpleGUI Documentation](https://github.com/PySimpleGUI/PySimpleGUI)

---

## Support

For issues specific to this codebase, check:
- `DEPRECATED_DEPENDENCIES.md` - Information about deprecated dependencies
- Project documentation files
- Code comments in source files

---

**Last Updated:** 2025  
**Maintained By:** [Your Name/Team]
