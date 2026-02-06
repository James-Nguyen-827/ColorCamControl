"""
Sim Code to practice getting camera setting values:

Exposure: Digital/Analog Gain
AWB: Red/Blue Gains
Shutterspeed

Things to do:
-Change Metering Mode, view values above. Are they consistent?
-Get a consistent black image, get the above values.

Collect the above data in a CSV file?
Headers: Filename, digital gain, analog gain, red gain, blue gain, shutter speed



"""

import csv
import os
import random
import time

from datetime import datetime
from picamera2 import Picamera2

# Preview Resolution
VID_WIDTH = 640
VID_HEIGHT = 480
VID_RES = (VID_WIDTH, VID_HEIGHT)

# Image Capture Resolution
# Take a Picture, 12MP: 4056x3040
PIC_WIDTH = 4056
PIC_HEIGHT = 3040
PIC_RES = (PIC_WIDTH, PIC_HEIGHT)

# Save CSV Headers
HEADERS = ["file_name", "iso", "analog_gain", "digital_gain", "red_gain", "blue_gain", "shutter_speed (microseconds)"]

# Change this folder for your system
SAVE_CSV_FOLDER = r'/home/pi/Projects/3dprinter_sampling/Test Pictures/7-21-2022'
# SAVE_CSV_FILE gets updated by init_csv_file() (is temporary solution)
SAVE_CSV_FILE = ''

SAVE_IMAGE_FOLDER = r'/home/pi/Projects/3dprinter_sampling/Test Pictures/7-21-2022'


def get_unique_id():
    current_time = datetime.now()
    unique_id = current_time.strftime("%Y-%m-%d_%H%M%S")
    # print(f"unique_id: {unique_id}")
    return unique_id


def gen_cam_data(image_file_name, camera):
    
    # picamera2 version - get metadata from capture
    # Capture metadata to get current camera settings
    metadata = camera.capture_metadata()
    
    # ISO value (sensitivity)
    iso_value = metadata.get("AnalogueGain", 0) * 100  # Approximate ISO from analogue gain
    
    # Get Analog and Digital Gains from metadata
    analog_gain = float(metadata.get("AnalogueGain", 1.0))
    digital_gain = float(metadata.get("DigitalGain", 1.0))
    
    # Get AWB Gains, red and blue
    colour_gains = metadata.get("ColourGains", (1.0, 1.0))
    red_gain = float(colour_gains[0])
    blue_gain = float(colour_gains[1])
    
    # Get Shutterspeed (exposure time in microseconds)
    shutter_speed = metadata.get("ExposureTime", 0)  # Already in microseconds
    
    data_row = [image_file_name, iso_value, analog_gain, digital_gain, red_gain, blue_gain, shutter_speed]

    return data_row


def init_csv_file():

    global SAVE_CSV_FILE

    csv_file_name = f"cam_values_{get_unique_id()}.csv"

    SAVE_CSV_FILE = csv_file_name

    full_path = os.path.join(SAVE_CSV_FOLDER, csv_file_name)

    f = open(full_path, 'w', newline="")
    writer = csv.writer(f)
    writer.writerow(HEADERS)
    f.close()


def append_to_csv_file(data_row):

    full_path = os.path.join(SAVE_CSV_FOLDER, SAVE_CSV_FILE)

    # Append to existing CSV File
    f = open(full_path, 'a', newline="")

    writer = csv.writer(f)

    writer.writerow(data_row)

    f.close()
    print(f"File Updated: {full_path}")


def setup_camera():
    camera = Picamera2()
    # Configure preview with video resolution
    preview_config = camera.create_preview_configuration(main={"size": (VID_WIDTH, VID_HEIGHT)})
    camera.configure(preview_config)
    camera.start()
    
    # Set Exposure mode (picamera2 uses different controls)
    # camera.set_controls({"ExposureMode": "fireworks"})  # Not directly supported
    
    # Set AWB Mode
    # camera.set_controls({"AwbMode": 2})  # 2 = tungsten
    
    # Wait for digital gain values to settle
    pre_value = -1
    cur_value = -1
    # Wait for digital gain values to settle, then break out of loop
    while pre_value != cur_value:
        pre_value = cur_value
        # Get current metadata
        metadata = camera.capture_metadata()
        cur_value = float(metadata.get("DigitalGain", 1.0))
        
        print(f"cur_value: {cur_value}")
        time.sleep(0.5)
    
    return camera



def set_exposure_mode(camera):
    
    # picamera2 version - set exposure controls differently
    
    # Turn Exposure mode back on so camera can adjust to new light
    # camera.set_controls({"ExposureMode": 0})  # 0 = normal
    # camera.set_controls({"AwbMode": 0})  # 0 = auto
    
    # Set exposure mode (fireworks equivalent - long exposure)
    # Note: picamera2 doesn't have exact 'fireworks' mode, use manual exposure
    # camera.set_controls({"ExposureMode": 1})  # Manual mode
    
    # Set AWB Mode (tungsten)
    camera.set_controls({"AwbMode": 2})  # 2 = tungsten
    
    # Set ISO (AnalogueGain) - picamera2 uses AnalogueGain directly
    # camera.set_controls({"AnalogueGain": 1.0})  # Set to 1.0 for auto
    
    # Wait for Automatic Gain Control to settle
    # time.sleep(2)
    pre_value = -1
    cur_value = -1
    # Wait for digital gain values to settle, then break out of loop
    while pre_value != cur_value:
        pre_value = cur_value
        # Get current metadata
        metadata = camera.capture_metadata()
        cur_value = float(metadata.get("DigitalGain", 1.0))
        
        print(f"digital_gain: {cur_value}")
        time.sleep(0.5)
    
    # Now fix the values
    
    # Exposure Mode - set manual exposure
    # Set shutter speed (exposure time in microseconds)
    camera.set_controls({"ExposureTime": 30901})  # 30901 microseconds
    camera.set_controls({"ExposureMode": 1})  # Manual exposure mode
    
    # Get and lock AWB gains
    metadata = camera.capture_metadata()
    colour_gains = metadata.get("ColourGains", (1.0, 1.0))
    camera.set_controls({"ColourGains": colour_gains})
    camera.set_controls({"AwbMode": 0})  # 0 = auto, but gains are locked
    # Must let camera sleep so exposure mode can settle on certain values, else black screen happens
    # time.sleep(settle_time)
    


def get_picture(camera):
    
    image_file_name = f"image_{get_unique_id()}.jpg"
    image_full_path = os.path.join(SAVE_IMAGE_FOLDER, image_file_name)
    
    # Configure for still capture with high resolution
    still_config = camera.create_still_configuration(main={"size": PIC_RES})
    camera.configure(still_config)
    
    # time.sleep(2)
    
    # New way to sleep
    # seconds_to_wait = 2
    # sleep2(seconds_to_wait)
    
    camera.capture_file(image_full_path)
    #time.sleep(2)
    
    datarow = gen_cam_data(image_file_name, camera)
    
    # Restore preview configuration
    preview_config = camera.create_preview_configuration(main={"size": (VID_WIDTH, VID_HEIGHT)})
    camera.configure(preview_config)
    
    print(f"Picture Saved: {image_full_path}")
    return datarow
    

def sleep2(seconds_to_wait):
    
    start = time.monotonic()
    elapsed_time = 0
    # for i in range(10):
    while elapsed_time < seconds_to_wait:
        # print(i)
        current_time = time.monotonic()
        elapsed_time = current_time - start
        # print(f"elapsed_time: {elapsed_time}")
    print(f"Waited {elapsed_time} seconds")
    pass


def main():
    # seconds_to_wait = 2
    # sleep2(seconds_to_wait)
    
    init_csv_file()
    # image_file_name = f"image_{get_unique_id()}.jpg"
    
    camera = setup_camera()
    set_exposure_mode(camera)
    
    # gen_cam_data(image_file_name, camera)
    # data_row = get_picture(camera)
    
    # data_row = gen_cam_data(image_file_name, camera)
    
    # print(f"data_row:\n {data_row}")
    # append_to_csv_file(data_row)

    for i in range(100):
        data_row = get_picture(camera)
        append_to_csv_file(data_row)
    
    camera.stop()
    camera.close()

    pass


if __name__ == "__main__":
    main()
