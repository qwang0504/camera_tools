import cv2 
import time
from numpy.typing import NDArray
from camera_tools.camera import Camera
from camera_tools.frame import BaseFrame

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
        pass

    def set_framerate(self, exp_time: float) -> None:
        pass

    def set_gain(self, exp_time: float) -> None:
        pass

    def set_ROI(self, left: int, bottom: int, height: int, width: int) -> None:
        pass