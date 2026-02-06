# Quick Start Guide - ColorCamControl

## Fast Setup (5 minutes)

### 1. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Enable camera
sudo raspi-config  # Interface Options → Camera → Enable

# Install system dependencies
sudo apt install -y python3-pip python3-venv libcamera-dev libcap-dev \
    libatlas-base-dev ffmpeg libopenjp2-7 libkms++-dev libfmt-dev libdrm-dev
```

### 2. Create Virtual Environment
```bash
cd ~/Projects/ColorCamControl  # or your project directory
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Printer
Edit `connection_settings.yaml` - set your printer's device path and baudrate.

### 5. Run Application
```bash
python3 3dprinter_sampler_gui_fly2.py
```

## Common Commands

```bash
# Activate venv
source venv/bin/activate

# Deactivate venv
deactivate

# Test camera
libcamera-hello --timeout 5000

# Check serial devices
ls -l /dev/ttyUSB* /dev/ttyACM*

# Add user to dialout group (for serial access)
sudo usermod -a -G dialout $USER
# Then log out and back in
```

## Troubleshooting

**Camera not working?**
- Check: `libcamera-hello --list-cameras`
- Enable in raspi-config if needed

**Serial port permission denied?**
- Add user to dialout: `sudo usermod -a -G dialout $USER`
- Log out and back in

**picamera2 import error?**
- Ensure venv was created with `--system-site-packages`
- Or install manually: `pip install rpi-libcamera rpi-kms picamera2`

For detailed instructions, see `SOP_SETUP_AND_RUN.md`
