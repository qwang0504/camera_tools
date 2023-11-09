from camera_tools.camera import Camera
from camera_tools.frame import Frame, BaseFrame
from typing import Tuple
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

    def get_exposure(self) -> Optional[float]:
        return self.xi_cam.get_exposure()

    def get_exposure_range(self) -> Optional[Tuple[float,float]]:
        pass

    def get_framerate(self) -> Optional[float]:
        return self.xi_cam.get_framerate()

    def get_framerate_range(self) -> Optional[Tuple[float,float]]:
        pass

    def get_gain(self) -> Optional[float]:
        return self.xi_cam.get_gain()

    def get_gain_range(self) -> Optional[Tuple[float,float]]:
        pass
    
    def set_exposure(self, exp_time: float) -> None:
        self.xi_cam.set_exposure(exp_time)

    def set_framerate(self, fps: float) -> None:
        self.xi_cam.set_acq_timing_mode('XI_ACQ_TIMING_MODE_FRAME_RATE_LIMIT')
        self.xi_cam.set_framerate(fps)

    def set_gain(self, gain: float) -> None:
        self.xi_cam.set_gain(gain)

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

    def get_offsetX_range(self) -> Optional[int]:
        pass

    def get_offsetX_increment(self) -> Optional[int]:
        pass

    def get_offsetY_range(self) -> Optional[int]:
        pass

    def get_offsetY_increment(self) -> Optional[int]:width
        pass

    def get_width_range(self) -> Optional[int]:
        pass

    def get_height_range(self) -> Optional[int]:
        pass

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