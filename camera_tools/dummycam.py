from camera_tools.camera import Camera
from camera_tools.frame import BaseFrame, Frame
import time
import numpy as np
from numpy.typing import NDArray, ArrayLike

class ZeroCam(Camera):
    """
    Provides an empty image. This is just for testing
    """

    def __init__(self, shape: ArrayLike, dtype: np.dtype, **kwargs):
        super().__init__(**kwargs)
        self.img_count: int = 0
        self.timestamp: float = time.monotonic()
        self.shape = shape 
        self.dtype = dtype

    def start_acquisition(self) -> None:
        pass

    def stop_acquisition(self) -> None:
        pass

    def get_frame(self) -> Frame:

        self.img_count += 1
        self.timestamp = time.monotonic()
        img = np.zeros(self.shape, dtype=self.dtype)
        frame = BaseFrame(self.img_count, self.timestamp, img)
        return frame
    
    def set_exposure(self, exp_time: float) -> None:
        pass

    def set_framerate(self, exp_time: float) -> None:
        pass

    def set_gain(self, exp_time: float) -> None:
        pass

    def set_ROI(self, left: int, bottom: int, height: int, width: int) -> None:
        pass
    
class RandomCam(Camera):
    """
    Provides a random image. This is just for testing
    """

    def __init__(self, shape: ArrayLike, dtype: np.dtype, **kwargs):

        super().__init__(**kwargs)
        
        self.img_count: int = 0
        self.timestamp: float = time.monotonic()
        self.shape = shape 
        self.dtype = dtype

    def get_frame(self) -> Frame:

        self.img_count += 1
        self.timestamp = time.monotonic()

        if np.issubdtype(self.dtype, np.integer):
            type_inf = np.iinfo(self.dtype)
            min_val = 0
            max_val = type_inf.max
            img = np.random.randint(min_val, max_val, self.shape, dtype=self.dtype)
        
        elif np.issubdtype(self.dtype, np.floating):
            img = np.random.uniform(0.0, 1.0, self.shape).astype(self.dtype)
        
        else:
            raise TypeError
        
        frame = BaseFrame(self.img_count, self.timestamp, img)
        return frame

    def start_acquisition(self) -> None:
        pass

    def stop_acquisition(self) -> None:
        pass

    def set_exposure(self, exp_time: float) -> None:
        pass

    def set_framerate(self, exp_time: float) -> None:
        pass

    def set_gain(self, exp_time: float) -> None:
        pass

    def set_ROI(self, left: int, bottom: int, height: int, width: int) -> None:
        pass