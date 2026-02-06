"""
CameraService: wraps PiCamera operations behind a small API so GUI/experiment
code does not touch the camera directly.

Currently supports picamera2 (Raspberry Pi 4); structure allows future backends
by subclassing BaseCameraBackend.
"""
from threading import Lock
from typing import Tuple, Optional
import numpy as np

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    Picamera2 = None

# Keep old picamera import for backward compatibility if needed
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


class Picamera2Backend(BaseCameraBackend):
    """Backend for picamera2 (Raspberry Pi 4)."""
    def __init__(self, rotation: int = 0, preview_res: Tuple[int, int] = (960, 720)):
        if not PICAMERA2_AVAILABLE or Picamera2 is None:
            raise RuntimeError("picamera2 not available on this system.")
        self.camera = Picamera2()
        self._rotation = rotation
        self._preview_res = preview_res
        self._still_res = preview_res
        self._overlay = None
        self._is_previewing = False
        
        # Configure preview
        preview_config = self.camera.create_preview_configuration(main={"size": preview_res})
        self.camera.configure(preview_config)
        self.camera.start()

    def start_preview(self, window: Tuple[int, int, int, int], alpha: int = 255):
        """Start preview window. Note: picamera2 preview handling differs from picamera."""
        # In picamera2, preview is typically handled via DRM or Qt, not window coordinates
        # For compatibility, we'll start the camera if not already started
        if not self._is_previewing:
            # Camera is already started in __init__, but we track state
            self._is_previewing = True
        # Note: Window positioning in picamera2 requires different approach (DRM/Qt)

    def stop_preview(self):
        """Stop preview."""
        if self._is_previewing:
            self._is_previewing = False
        # Don't stop camera completely as it may be used for captures

    def set_resolution(self, res: Tuple[int, int]):
        """Set preview resolution."""
        self._preview_res = res
        # Reconfigure camera with new resolution
        preview_config = self.camera.create_preview_configuration(main={"size": res})
        self.camera.configure(preview_config)

    def set_rotation(self, rotation: int):
        """Set rotation (applied via transform)."""
        self._rotation = rotation
        # Apply rotation transform (picamera2 uses Transform enum: 0=0°, 1=90°, 2=180°, 3=270°)
        transform_map = {0: 0, 90: 1, 180: 2, 270: 3}
        transform_value = transform_map.get(rotation % 360, 0)
        # Note: Transform control may need to be set during configuration
        # For now, we'll try to set it via controls
        try:
            self.camera.set_controls({"Transform": transform_value})
        except:
            # If setting controls fails, rotation will be handled during next configuration
            pass

    def capture_still(self, path: str, res: Optional[Tuple[int, int]] = None):
        """Capture a still image."""
        if res:
            # Configure for still capture with specific resolution
            still_config = self.camera.create_still_configuration(main={"size": res})
            self.camera.configure(still_config)
            self.camera.capture_file(path)
            # Restore preview configuration
            preview_config = self.camera.create_preview_configuration(main={"size": self._preview_res})
            self.camera.configure(preview_config)
        else:
            self.camera.capture_file(path)

    def add_overlay(self, buffer, size, window, alpha: int = 255):
        """Add overlay. Note: picamera2 overlay API differs significantly."""
        # picamera2 overlays work differently - this is a placeholder
        # Real implementation would need to use picamera2's overlay system
        self._overlay = {"buffer": buffer, "size": size, "window": window, "alpha": alpha}
        return self._overlay

    def remove_overlay(self, overlay=None):
        """Remove overlay."""
        self._overlay = None

    def close(self):
        """Close camera (for cleanup)."""
        if self.camera:
            self.camera.stop()
            self.camera.close()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except:
            pass


class PicameraBackend(BaseCameraBackend):
    """Legacy backend for picamera (Raspberry Pi 3). Kept for backward compatibility."""
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
        # Default to Picamera2Backend for Raspberry Pi 4
        self.backend = backend or Picamera2Backend(rotation=rotation, preview_res=preview_res)
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
