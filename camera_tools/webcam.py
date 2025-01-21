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
        self.index = 0
        self.time_start = time.monotonic()

    def stop_acquisition(self) -> None:
        self.camera.release() 
    
    def get_frame(self) -> NDArray:
        ret, img = self.camera.read()
        img_rgb = img[:,:,::-1]
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

def get_cam_properties():
    VIDEO_CAPTURE_PROPERTIES = {
        0: "CAP_PROP_POS_MSEC",             # Current position of the video file in milliseconds
        1: "CAP_PROP_POS_FRAMES",           # Index of the next frame to be captured
        2: "CAP_PROP_POS_AVI_RATIO",        # Relative position of the video file: 0=start, 1=end
        3: "CAP_PROP_FRAME_WIDTH",          # Width of the frames in the video stream
        4: "CAP_PROP_FRAME_HEIGHT",         # Height of the frames in the video stream
        5: "CAP_PROP_FPS",                  # Frame rate
        6: "CAP_PROP_FOURCC",               # Codec four-character code
        7: "CAP_PROP_FRAME_COUNT",          # Number of frames in the video file
        8: "CAP_PROP_FORMAT",               # Format of the Mat object returned by VideoCapture::retrieve()
        9: "CAP_PROP_MODE",                 # Backend-specific value indicating the current capture mode
        10: "CAP_PROP_BRIGHTNESS",          # Brightness of the image (only for cameras)
        11: "CAP_PROP_CONTRAST",            # Contrast of the image (only for cameras)
        12: "CAP_PROP_SATURATION",          # Saturation of the image (only for cameras)
        13: "CAP_PROP_HUE",                 # Hue of the image (only for cameras)
        14: "CAP_PROP_GAIN",                # Gain of the image (only for cameras)
        15: "CAP_PROP_EXPOSURE",            # Exposure (only for cameras)
        16: "CAP_PROP_CONVERT_RGB",         # Boolean: images will be converted to RGB or not
        17: "CAP_PROP_WHITE_BALANCE_BLUE_U",# White balance - Blue/U
        18: "CAP_PROP_RECTIFICATION",       # Rectification flag for stereo cameras (note: only for stereo cameras)
        19: "CAP_PROP_MONOCHROME",          # Monochrome mode
        20: "CAP_PROP_SHARPNESS",           # Sharpness of the image
        21: "CAP_PROP_AUTO_EXPOSURE",       # Auto exposure mode
        22: "CAP_PROP_GAMMA",               # Gamma correction
        23: "CAP_PROP_TEMPERATURE",         # Temperature of the image
        24: "CAP_PROP_TRIGGER",             # Trigger
        25: "CAP_PROP_TRIGGER_DELAY",       # Delay for the trigger
        26: "CAP_PROP_WHITE_BALANCE_RED_V", # White balance - Red/V
        27: "CAP_PROP_ZOOM",                # Zoom level
        28: "CAP_PROP_FOCUS",               # Focus setting
        29: "CAP_PROP_GUID",                # GUID for the device (only for FireWire cameras)
        30: "CAP_PROP_ISO_SPEED",           # ISO speed
        32: "CAP_PROP_BACKLIGHT",           # Backlight compensation
        33: "CAP_PROP_PAN",                 # Pan setting
        34: "CAP_PROP_TILT",                # Tilt setting
        35: "CAP_PROP_ROLL",                # Roll setting
        36: "CAP_PROP_IRIS",                # Iris setting
        37: "CAP_PROP_SETTINGS",            # Pop up the camera settings window
        38: "CAP_PROP_BUFFERSIZE",          # Number of frames to buffer
        39: "CAP_PROP_AUTOFOCUS",           # Autofocus
        40: "CAP_PROP_SAR_NUM",             # Sample aspect ratio numerator
        41: "CAP_PROP_SAR_DEN",             # Sample aspect ratio denominator
        42: "CAP_PROP_BACKEND",             # Video backend (enum)
        43: "CAP_PROP_CHANNEL",             # Current capture channel
        44: "CAP_PROP_AUTO_WB",             # Auto white balance
        45: "CAP_PROP_WB_TEMPERATURE",      # White balance temperature
        46: "CAP_PROP_CODEC_PIXEL_FORMAT",  # Pixel format of the codec
        47: "CAP_PROP_BITRATE",             # Video bitrate
        48: "CAP_PROP_ORIENTATION_META",    # Orientation metadata
        49: "CAP_PROP_ORIENTATION_AUTO",    # Automatic orientation handling
        53: "CAP_PROP_OPEN_TIMEOUT_MSEC",   # Timeout for opening the capture device (in milliseconds)
        54: "CAP_PROP_READ_TIMEOUT_MSEC",   # Timeout for reading a frame (in milliseconds)
    }

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open video capture device.")
    else:
        properties = {}
        for prop_id, prop_name in VIDEO_CAPTURE_PROPERTIES.items():
            value = cap.get(prop_id)
            if value != -1:  # Property is supported
                properties[prop_name] = value
        cap.release()

        # Print supported properties and their current values
        print("Supported properties and their values:")
        for name, value in properties.items():
            print(f"{name}: {value}")