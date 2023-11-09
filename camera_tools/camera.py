from abc import ABC, abstractmethod
from numpy.typing import NDArray
from camera_tools.frame import Frame
from typing import Optional, Tuple

class Camera(ABC):

    @abstractmethod
    def start_acquisition(self):
        pass

    @abstractmethod
    def stop_acquisition(self):
        pass

    @abstractmethod
    def set_exposure(self, exp_time: float) -> None:
        pass

    @abstractmethod
    def set_framerate(self, fps: float) -> None:
        pass

    @abstractmethod
    def set_gain(self, gain: float) -> None:
        pass

    @abstractmethod
    def get_exposure(self) -> Optional[float]:
        pass

    @abstractmethod
    def get_exposure_range(self) -> Optional[Tuple[float,float]]:
        pass

    @abstractmethod
    def get_framerate(self) -> Optional[float]:
        pass

    @abstractmethod
    def get_framerate_range(self) -> Optional[Tuple[float,float]]:
        pass

    @abstractmethod
    def get_gain(self) -> Optional[float]:
        pass

    @abstractmethod
    def get_gain_range(self) -> Optional[Tuple[float,float]]:
        pass

    @abstractmethod
    def set_ROI(self, left: int, bottom: int, height: int, width: int) -> None:
        pass

    @abstractmethod
    def get_ROI(self) -> Optional[Tuple[int,int,int,int]]:
        pass

    @abstractmethod
    def set_offsetX(self, Optional[int]offsetX: int) -> None:
        pass

    @abstractmethod
    def get_offsetX(self) -> Optional[int]:
        pass

    @abstractmethod
    def get_offsetX_range(self) -> Optional[int]:
        pass

    @abstractmethod
    def get_offsetX_increment(self) -> Optional[int]:
        pass

    @abstractmethod
    def set_offsetY(self, offsetY: int) -> None:
        pass

    @abstractmethod
    def get_offsetY(self) -> Optional[int]:
        pass

    @abstractmethod
    def get_offsetY_range(self) -> Optional[int]:
        pass

    @abstractmethod
    def get_offsetY_increment(self) -> Optional[int]:width
        pass

    @abstractmethod
    def set_width(self, width: int) -> None:
        pass

    @abstractmethod
    def get_width(self) -> Optional[int]:
        pass

    @abstractmethod
    def get_width_range(self) -> Optional[int]:
        pass

    @abstractmethod
    def set_height(self, height) -> None:
        pass

    @abstractmethod
    def get_height(self) -> Optional[int]:
        pass    

    @abstractmethod
    def get_height_range(self) -> Optional[int]:
        pass
