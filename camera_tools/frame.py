from abc import ABC, abstractmethod
from numpy.typing import NDArray
import numpy as np

class Frame(ABC):
    
    @property
    @abstractmethod
    def index(self) -> int:
        pass

    @property
    @abstractmethod
    def timestamp(self) -> float:
        pass

    @property
    @abstractmethod
    def image(self) -> NDArray:
        pass

    @property
    def width(self) -> int:
        return self.image.shape[1]
    
    @property
    def height(self) -> int:
        return self.image.shape[0]
    
    @property
    def dtype(self) -> np.dtype:
        return self.image.dtype


class BaseFrame(Frame):
    def __init__(self, index: int, timestamp: float, image: NDArray):

        self._image = image
        self._timestamp = timestamp
        self._index = index

    @property
    def index(self) -> int:
        return self._index

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def image(self) -> NDArray:
        return self._image 
    