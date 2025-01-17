import cv2 
import time
from numpy.typing import NDArray
from camera_tools.camera import Camera
from typing import Optional, Tuple
import numpy as np
from image_tools import im2gray

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
        self.camera.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_RGB)
        self.index = 0
        self.time_start = time.monotonic()

    def stop_acquisition(self) -> None:
        self.camera.release() 
    
    def get_frame(self) -> NDArray:
        ret, img_rgb = self.camera.read()
        #img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.index += 1
        timestamp = time.monotonic() - self.time_start
        frame = np.array(
            (self.index, timestamp, img_rgb),
            dtype = np.dtype([
                ('index', int),
                ('timestamp', np.float32),
                ('image', img_rgb.dtype, img_rgb.shape)
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
        return True
    
    def set_framerate(self, fps: float) -> None:
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_FPS, fps)
       
    def get_framerate(self) -> Optional[float]:
        if self.camera is not None:
            return self.camera.get(cv2.CAP_PROP_FPS)

    def get_framerate_range(self) -> Optional[Tuple[float,float]]:
        return (1, 1000)

    def get_framerate_increment(self) -> Optional[float]:
        return 1

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
        return self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)

    def get_width_range(self) -> Optional[Tuple[int,int]]:
        return (640, 3840)

    def get_width_increment(self) -> Optional[int]:
        return 2  

    def height_available(self) -> bool:
        return True
    
    def set_height(self, height) -> None:
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    def get_height(self) -> Optional[int]:
        return self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)    
    
    def get_height_range(self) -> Optional[Tuple[int,int]]:
        return (480, 2160)

    def get_height_increment(self) -> Optional[int]:
        return 2 
    
    def get_num_channels(self):
        return 3

class OpenCV_Webcam_InitEveryFrame(OpenCV_Webcam):

    # workaround to clear buffer and always get last frame. 
    # this is a bit slow 

    def get_frame(self) -> NDArray:
        
        self.start_acquisition()
        ret, img = self.camera.read()
        self.stop_acquisition()

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.index += 1
        timestamp = time.monotonic() - self.time_start
        frame = np.array(
            (self.index, timestamp, img_rgb),
            dtype = np.dtype([
                ('index', int),
                ('timestamp', np.float32),
                ('image', img_rgb.dtype, img_rgb.shape)
            ])
        )
        return frame

class OpenCV_Webcam_Gray(OpenCV_Webcam):

    def get_frame(self):
        ret, img = self.camera.read()
        img_gray = im2gray(img)
        self.index += 1
        timestamp = time.monotonic() - self.time_start
        frame = np.array(
            (self.index, timestamp, img_gray),
            dtype = np.dtype([
                ('index', int),
                ('timestamp', np.float32),
                ('image', img_gray.dtype, img_gray.shape)
            ])
        )
        return frame

    def get_num_channels(self):
        return 1
    
class OpenCV_Webcam_LastFrame(OpenCV_Webcam):

    # workaround to clear buffer and always get last frame. 
    # constantly get images in a separate thread in a loop, 
    # and overwrite a single variable.
    pass
