import cv2 
from typing import Protocol, Tuple
import time
from numpy.typing import NDArray

class FrameIndex(int):
    pass

class FrameTimestamp(float):
    pass


class Camera(Protocol):
    def start_acquisition(self) -> None:
        ...
    
    def stop_acquisition(self) -> None:
        ...

    def fetch(self) -> Tuple[FrameIndex, FrameTimestamp, NDArray]:
        ...


class OpenCV_Webcam(Camera):

    def __init__(self, *args, **kwargs) -> None:
        
        super().__init__(*args, **kwargs)
        self.camera = None 
        self.index = 0
        self.time_start = time.time()

    def start_acquisition(self) -> None:
        self.camera = cv2.VideoCapture(0)
        self.index = 0
        self.time_start = time.time()

    def stop_acquisition(self) -> None:
        self.camera.release() 
    
    def fetch(self) -> Tuple[FrameIndex, FrameTimestamp, NDArray]:
        ret, frame = self.camera.read()
        self.index += 1
        timestamp = time.time() - self.time_start
        return (FrameIndex(self.index), FrameTimestamp(timestamp), frame)
    
