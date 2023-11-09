import cv2 
import time
from numpy.typing import NDArray
from camera_tools.camera import Camera
from camera_tools.frame import BaseFrame
from typing import Optional

# NOTE another option on linux is to use v4l2-ctl to change camera settings 
  
class OpenCV_Webcam(Camera):

    def __init__(self, *args, **kwargs) -> None:
        
        super().__init__(*args, **kwargs)

        self.camera = None 
        self.index = 0
        self.time_start = time.monotonic()

    def start_acquisition(self) -> None:
        self.camera = cv2.VideoCapture(0)
        self.index = 0
        self.time_start = time.monotonic()

    def stop_acquisition(self) -> None:
        self.camera.release() 
    
    def get_frame(self) -> BaseFrame:
        ret, frame = self.camera.read()
        self.index += 1
        timestamp = time.monotonic() - self.time_start
        return BaseFrame(self.index, timestamp, frame)
    
    def set_exposure(self, exp_time: float) -> None:
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_EXPOSURE, exp_time)

    def set_framerate(self, fps: float) -> None:
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_FPS, fps)

    def set_gain(self, gain: float) -> None:
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_GAIN, gain)
        
    def get_exposure(self) -> Optional[float]:
        if self.camera is not None:
            return self.camera.get(cv2.CAP_PROP_EXPOSURE)

    def get_framerate(self) -> Optional[float]:
        if self.camera is not None:
            return self.camera.get(cv2.CAP_PROP_FPS)

    def get_gain(self) -> Optional[float]:
        if self.camera is not None:
            return self.camera.get(cv2.CAP_PROP_GAIN)

    def set_ROI(self, left: int, bottom: int, height: int, width: int) -> None:
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)