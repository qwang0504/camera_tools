from ipc_tools import MultiRingBuffer_Locked
from camera_tools.frame import BaseFrame, Frame
from numpy.typing import NDArray, ArrayLike, DTypeLike
import numpy as np
from typing import Optional

class RingBuffer(MultiRingBuffer_Locked):

    def __init__(
            self, 
            num_items: int,
            frame_shape: ArrayLike, 
            frame_dtype: DTypeLike,
            t_refresh: float = 0.001
        ):

        super().__init__(
            num_items,
            item_shape = [1,1,frame_shape],
            data_type = [np.int64, np.float64, frame_dtype],
            t_refresh = t_refresh,
        )

    def get(self, blocking: bool = True, timeout: float = float('inf'), copy: bool = False) -> Optional[Frame]:

        data = super().get(blocking, timeout, copy)
        return BaseFrame(data[0].item(),data[1].item(),data[2])

    def put(self, frame: Frame) -> None:

        super().put([frame.index, frame.timestamp, frame.image])