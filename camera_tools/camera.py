from abc import ABC, abstractmethod
from numpy.typing import NDArray
from camera_tools.frame import Frame

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
    def set_framerate(self, exp_time: float) -> None:
        pass

    @abstractmethod
    def set_gain(self, exp_time: float) -> None:
        pass

    @abstractmethod
    def set_ROI(self, left: int, bottom: int, height: int, width: int) -> None:
        pass

    @abstractmethod
    def get_frame(self) -> Frame:
        pass
    