"""
CameraService: wraps PiCamera operations behind a small API so GUI/experiment
code does not touch the camera directly.

Currently supports picamera; structure allows future backends (e.g. picamera2,
mono camera) by subclassing BaseCameraBackend.
"""
from threading import Lock
from typing import Tuple, Optional

try:
    from picamera import PiCamera
except ImportError:
    PiCamera = None


class BaseCameraBackend:
    def start_preview(self, window: Tuple[int, int, int, int], alpha: int = 255):
        raise NotImplementedError

    def stop_preview(self):
        raise NotImplementedError

    def set_resolution(self, res: Tuple[int, int]):
        raise NotImplementedError

    def set_rotation(self, rotation: int):
        raise NotImplementedError

    def capture_still(self, path: str, res: Optional[Tuple[int, int]] = None):
        raise NotImplementedError

    def add_overlay(self, buffer, size, window, alpha: int = 255):
        raise NotImplementedError

    def remove_overlay(self, overlay):
        raise NotImplementedError


class PicameraBackend(BaseCameraBackend):
    def __init__(self, rotation: int = 0, preview_res: Tuple[int, int] = (960, 720)):
        if PiCamera is None:
            raise RuntimeError("picamera not available on this system.")
        self.camera = PiCamera()
        self.camera.rotation = rotation
        self.camera.resolution = preview_res
        self._overlay = None

    def start_preview(self, window: Tuple[int, int, int, int], alpha: int = 255):
        self.camera.start_preview(alpha=alpha, fullscreen=False, window=window)

    def stop_preview(self):
        self.camera.stop_preview()

    def set_resolution(self, res: Tuple[int, int]):
        self.camera.resolution = res

    def set_rotation(self, rotation: int):
        self.camera.rotation = rotation

    def capture_still(self, path: str, res: Optional[Tuple[int, int]] = None):
        original_res = self.camera.resolution
        if res:
            self.camera.resolution = res
        self.camera.capture(path)
        if res:
            self.camera.resolution = original_res

    def add_overlay(self, buffer, size, window, alpha: int = 255):
        # Only implement when overlays are used; placeholder for future work.
        if self._overlay:
            self.remove_overlay(self._overlay)
        self._overlay = self.camera.add_overlay(
            buffer,
            size=size,
            fullscreen=False,
            window=window,
            alpha=alpha,
        )
        return self._overlay

    def remove_overlay(self, overlay=None):
        ov = overlay or self._overlay
        if ov:
            self.camera.remove_overlay(ov)
        self._overlay = None


class CameraService:
    """
    Thread-safe facade for camera operations.
    """

    def __init__(self, backend: Optional[BaseCameraBackend] = None, rotation: int = 0, preview_res=(960, 720)):
        self.backend = backend or PicameraBackend(rotation=rotation, preview_res=preview_res)
        self.lock = Lock()

    def start_preview(self, window: Tuple[int, int, int, int], alpha: int = 255):
        with self.lock:
            self.backend.start_preview(window, alpha)

    def stop_preview(self):
        with self.lock:
            self.backend.stop_preview()

    def set_resolution(self, res: Tuple[int, int]):
        with self.lock:
            self.backend.set_resolution(res)

    def set_rotation(self, rotation: int):
        with self.lock:
            self.backend.set_rotation(rotation)

    def capture_still(self, path: str, res: Optional[Tuple[int, int]] = None):
        with self.lock:
            self.backend.capture_still(path, res=res)

    def add_overlay(self, buffer, size, window, alpha: int = 255):
        with self.lock:
            return self.backend.add_overlay(buffer, size, window, alpha)

    def remove_overlay(self, overlay=None):
        with self.lock:
            self.backend.remove_overlay(overlay)
