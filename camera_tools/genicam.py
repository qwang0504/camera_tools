from camera_tools.camera import Camera
from camera_tools.frame import Frame
from harvesters.core import Harvester
from numpy.typing import NDArray


class FrameHarvesters(Frame):
    def __init__(self, buffer):
        self._buffer = buffer

    @property
    def index(self) -> int:
        return self._buffer.num

    @property
    def timestamp(self) -> float:
        return self._buffer.timestamp

    @property
    def image(self) -> NDArray:
        return self._buffer.payload.component[0].data

    def reallocate(self):
        """This is important to allow the camera to reuse the buffer"""
        self._buffer.queue()

class GenicamHarvesters(Camera):

    def __init__(self, gentl_producer, **kwargs):
        """
        Open camera using the GenICam/GenTL API
        Inputs:
            gentl_producer: *.cti file from camera vendor     
        """

        super().__init__(**kwargs)

        self.img_count: int = 0
        self._h = Harvester()
        self._h.add_file(gentl_producer)
        self._h.update()

        # discover cameras
        if ~self._h.device_info_list:
            RuntimeError('No camera found')
        else:
            print(f"Found {len(self._h.device_info_list)} devices")

        self._imAcq = self._h.create(self._camera_index)
        self._imAcq.num_buffers = self._num_buffers
        self.node_map = self._imAcq.remote_device.node_map

        node_map.Width.value = self._width
        node_map.Height.value = self._height
        node_map.OffsetX.value = self._left
        node_map.OffsetY.value = self._top
        node_map.PixelFormat.value = self._pixel_format
        node_map.TriggerMode.value = self._triggers
        node_map.Gain.value = self._gain
        node_map.ExposureTime.value = self._exposure_time
    
    def set_exposure(self, exp_time: float) -> None:
        pass

    def set_framerate(self, fps: float) -> None:
        node_map = self._imAcq.remote_device.node_map
        node_map.AcquisitionFrameRate.value = self._fps

    def set_gain(self, gain: float) -> None:
        pass

    def set_ROI(self, left: int, bottom: int, height: int, width: int) -> None:
        pass

    def start_acquisition(self):
        self._imAcq.start()

    def stop_acquisition(self):
        self._imAcq.stop()

    def get_frame(self) -> Frame:
        # TODO check that it is passed by reference and there is no copy
        # and that the buffer is not destroyed at the end of the function
        self.img_count += 1
        buf = FrameHarvesters(self._imAcq.fetch())
        return buf
    
    def __del__(self):
        print(self._imAcq.statistics)
        self._imAcq.destroy()
        self._h.reset()