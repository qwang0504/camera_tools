import cv2 
import time
from numpy.typing import NDArray
from camera_tools.camera import Camera
from typing import Optional, Tuple
import numpy as np

# NOTE this is just a hack, OpenCV webacm control is very superficial 
# The right solution is probably to use v4l2
#   sudo apt install v4l-utils
#   v4l2-ctl -d /dev/video0 --list-formats-ext
#   v4l2-ctl -d /dev/video0 --list-ctrls-menus

class OpenCV_Webcam(Camera):

    def __init__(self, cam_id: int = 0, *args, **kwargs) -> None:
        
        super().__init__(*args, **kwargs)

        self.camera_id = cam_id
        self.camera = cv2.VideoCapture(self.camera_id) 
        self.index = 0
        self.time_start = time.monotonic()

    def start_acquisition(self) -> None:
        self.camera.release()
        self.camera = cv2.VideoCapture(self.camera_id)
        self.index = 0
        self.time_start = time.monotonic()

    def stop_acquisition(self) -> None:
        self.camera.release() 
    
    def get_frame(self) -> NDArray:
        ret, frame = self.camera.read()
        self.index += 1
        timestamp = time.monotonic() - self.time_start
        frame = np.array(
            (self.index, timestamp, frame),
            dtype = np.dtype([
                ('index', int),
                ('timestamp', np.float32),
                ('image', frame.dtype, frame.shape)
            ])
        )
        return frame
    
    def exposure_available(self) -> bool:
        return False
    
    def set_exposure(self, exp_time: float) -> None:
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_EXPOSURE, exp_time)
 
    def get_exposure(self) -> Optional[float]:
        if self.camera is not None:
            return self.camera.get(cv2.CAP_PROP_EXPOSURE)

    def get_exposure_range(self) -> Optional[Tuple[float,float]]:
        pass

    def get_exposure_increment(self) -> Optional[float]:
        pass

    def framerate_available(self) -> bool:
        return False
    
    def set_framerate(self, fps: float) -> None:
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_FPS, fps)
       
    def get_framerate(self) -> Optional[float]:
        if self.camera is not None:
            return self.camera.get(cv2.CAP_PROP_FPS)

    def get_framerate_range(self) -> Optional[Tuple[float,float]]:
        pass

    def get_framerate_increment(self) -> Optional[float]:
        pass

    def gain_available(self) -> bool:
        return False
    
    def set_gain(self, gain: float) -> None:
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_GAIN, gain)

    def get_gain(self) -> Optional[float]:
        if self.camera is not None:
            return self.camera.get(cv2.CAP_PROP_GAIN)

    def get_gain_range(self) -> Optional[Tuple[float,float]]:
        pass

    def get_gain_increment(self) -> Optional[float]:
        pass

    def ROI_available(self) -> bool:
        return False
    
    def set_ROI(self, left: int, bottom: int, height: int, width: int) -> None:
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_ROI(self) -> Optional[Tuple[int,int,int,int]]:
        pass

    def offsetX_available(self) -> bool:
        return False
    
    def set_offsetX(self, offsetX: int) -> None:
        pass

    def get_offsetX(self) -> Optional[int]:
        pass

    def get_offsetX_range(self) -> Optional[Tuple[int,int]]:
        pass

    def get_offsetX_increment(self) -> Optional[int]:
        pass

    def offsetY_available(self) -> bool:
        return False
    
    def set_offsetY(self, offsetY: int) -> None:
        pass

    def get_offsetY(self) -> Optional[int]:
        pass

    def get_offsetY_range(self) -> Optional[Tuple[int,int]]:
        pass

    def get_offsetY_increment(self) -> Optional[int]:
        pass

    def width_available(self) -> bool:
        return True
    
    def set_width(self, width: int) -> None:
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)

    def get_width(self) -> Optional[int]:
        self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)

    def get_width_range(self) -> Optional[Tuple[int,int]]:
        return (640, 3840)

    def get_width_increment(self) -> Optional[int]:
        return 2  

    def height_available(self) -> bool:
        return True
    
    def set_height(self, height) -> None:
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    def get_height(self) -> Optional[int]:
        self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)    
    
    def get_height_range(self) -> Optional[Tuple[int,int]]:
        return (480, 2160)

    def get_height_increment(self) -> Optional[int]:
        return 2 

class OpenCV_Webcam_InitEveryFrame(OpenCV_Webcam):

    def get_frame(self) -> NDArray:
        
        self.start_acquisition()
        ret, frame = self.camera.read()
        self.stop_acquisition()

        self.index += 1
        timestamp = time.monotonic() - self.time_start
        frame = np.array(
            (self.index, timestamp, frame),
            dtype = np.dtype([
                ('index', int),
                ('timestamp', np.float32),
                ('image', frame.dtype, frame.shape)
            ])
        )
        return frame
