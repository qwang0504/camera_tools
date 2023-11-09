from camera_tools.camera import Camera
from camera_tools.frame import Frame, BaseFrame
from typing import Optional, Tuple
from ximea import xiapi
from numpy.typing import NDArray

class XimeaCamera(Camera):

    def __init__(self, *args, **kwargs):

        super().__init__()
        
        self.xi_cam = None
        self.xi_img = None

    def configure(self):
        # open camera
        self.xi_cam = xiapi.Camera()
        self.xi_cam.open_device()
        
        # create buffer 
        self.xi_img = xiapi.Image()        
        
    def start_acquisition(self) -> None:
        self.configure()
        self.xi_cam.start_acquisition()
    
    def stop_acquisition(self) -> None:
        self.xi_cam.stop_acquisition()

    def set_exposure(self, exp_time: float) -> None:
        self.xi_cam.set_exposure(exp_time)

    def get_exposure(self) -> Optional[float]:
        return self.xi_cam.get_exposure()

    def get_exposure_range(self) -> Optional[Tuple[float,float]]:
        exposure_min = self.xi_cam.get_exposure_minimum()
        exposure_max = self.xi_cam.get_exposure_maximum()
        return (exposure_min, exposure_max)

    def get_exposure_increment(self) -> Optional[float]:
        return self.xi_cam.get_exposure_increment()

    def set_framerate(self, fps: float) -> None:
        if fps == 0:
            self.xi_cam.set_acq_timing_mode('XI_ACQ_TIMING_MODE_FREE_RUN')
        else:
            self.xi_cam.set_acq_timing_mode('XI_ACQ_TIMING_MODE_FRAME_RATE_LIMIT')
            self.xi_cam.set_framerate(fps)

    def get_framerate(self) -> Optional[float]:
        return self.xi_cam.get_framerate()

    def get_framerate_range(self) -> Optional[Tuple[float,float]]:
        framerate_min = self.xi_cam.get_framerate_minimum()
        framerate_max = self.xi_cam.get_framerate_maximum()
        return (framerate_min, framerate_max)

    def get_framerate_increment(self) -> Optional[float]:
        return self.xi_cam.get_framerate_increment()

    def set_gain(self, gain: float) -> None:
        self.xi_cam.set_gain(gain)

    def get_gain(self) -> Optional[float]:
        return self.xi_cam.get_gain()

    def get_gain_range(self) -> Optional[Tuple[float,float]]:
        gain_min = self.xi_cam.get_gain_minimum()
        gain_max = self.xi_cam.get_gain_maximum()
        return (gain_min, gain_max)

    def get_gain_increment(self) -> Optional[float]:
        return self.xi_cam.get_gain_increment()

    def set_ROI(self, left: int, bottom: int, height: int, width: int) -> None:
        
        # Ximea camera restricts the ROI to be some integer multiples 
        x_inc = self.xi_cam.get_offsetX_increment()
        y_inc = self.xi_cam.get_offsetY_increment()
        max_width = self.xi_cam.get_offsetX_maximum()+self.xi_cam.get_width_maximum()
        max_height = self.xi_cam.get_offsetY_maximum()+self.xi_cam.get_height_maximum()
        
        # TODO check that ROI is valid 

        self.xi_cam.set_width(width)
        self.xi_cam.set_height(height)
        self.xi_cam.set_offsetX(left)
        self.xi_cam.set_offsetY(bottom)

    def get_ROI(self) -> Optional[Tuple[int,int,int,int]]:
        pass

    def set_offsetX(self, offsetX: int) -> None:
        # TODO check that value is valid
        self.xi_cam.set_offsetX(offsetX)

    def get_offsetX(self) -> Optional[int]:
        return self.xi_cam.get_offsetX()

    def get_offsetX_range(self) -> Optional[int]:
        offsetX_min = self.xi_cam.get_offsetX_minimum()
        offsetX_max = self.xi_cam.get_offsetX_maximum()
        return (offsetX_min, offsetX_max)

    def get_offsetX_increment(self) -> Optional[int]:
        return self.xi_cam.get_offsetX_increment()

    def set_offsetY(self, offsetY: int) -> None:
        # TODO check that value is valid
        self.xi_cam.set_offsetX(offsetY)

    def get_offsetY(self) -> Optional[int]:
        return self.xi_cam.get_offsetY()

    def get_offsetY_range(self) -> Optional[int]:
        offsetY_min = self.xi_cam.get_offsetY_minimum()
        offsetY_max = self.xi_cam.get_offsetY_maximum()
        return (offsetY_min, offsetY_max)

    def get_offsetY_increment(self) -> Optional[int]:
        return self.xi_cam.get_offsetY_increment()

    def set_width(self, width: int) -> None:
        self.xi_cam.set_width(width)

    def get_width(self) -> Optional[int]:
        return self.xi_cam.get_width()

    def get_width_range(self) -> Optional[int]:
        width_min = self.xi_cam.get_width_minimum()
        width_max = self.xi_cam.get_width_maximum()
        return (width_min, width_max)

    def get_width_increment(self) -> Optional[int]:
        return self.xi_cam.get_width_increment()

    def set_height(self, height) -> None:
        self.xi_cam.set_height(height)
    
    def get_height(self) -> Optional[int]:
        self.xi_cam.get_height()    
    
    def get_height_range(self) -> Optional[int]:
        height_min = self.xi_cam.get_height_minimum()
        height_max = self.xi_cam.get_height_maximum()
        return (height_min, height_max)
    
    def get_height_increment(self) -> Optional[int]:
        return self.xi_cam.get_height_increment()

    def get_frame(self) -> Frame:
        self.xi_cam.get_image(self.xi_img)
        pixeldata = self.xi_img.get_image_data_numpy()
        im_num = self.xi_img.acq_nframe
        ts_sec = self.xi_img.tsSec
        ts_usec = self.xi_img.tsUSec
        timestamp = (ts_sec*1_000_000 +  ts_usec)/1_000_000
        return BaseFrame(im_num, timestamp, pixeldata)

    def __del__(self):
        if self.xi_cam is not None:
            self.xi_cam.close_device()