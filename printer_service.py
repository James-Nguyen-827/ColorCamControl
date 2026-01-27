"""
PrinterService: lightweight wrapper around a serial-connected 3D printer.
Provides basic G-code send and home commands behind a simple API.
"""
import serial
import time

from utils import sleep_with_stop


class PrinterService:
    def __init__(self, device_path: str, baudrate: int, timeout: float, reboot_wait: float = 5):
        self.device_path = device_path
        self.baudrate = baudrate
        self.timeout = timeout
        self.reboot_wait = reboot_wait
        self.printer = serial.Serial(device_path, baudrate=baudrate, timeout=timeout)

    def home(self):
        self.run_gcode("G28")
        time.sleep(self.reboot_wait)

    def run_gcode(self, gcode: str):
        cmd = (gcode + "\n").encode("utf-8")
        self.printer.write(cmd)

    def run_path(self, gcode_list, dwell_seconds: float, stop_event):
        for g in gcode_list:
            if stop_event.is_set():
                break
            self.run_gcode(g)
            sleep_with_stop(dwell_seconds, stop_event)

    def close(self):
        self.printer.close()
