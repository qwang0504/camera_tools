from camera_tools import OpenCV_Webcam, RingBuffer
import numpy as np

cam = OpenCV_Webcam()
cam.start_acquisition()
img = cam.get_frame()
cam.stop_acquisition()

mybuf = RingBuffer(num_items=100,frame_shape=(480,640,3),frame_dtype=np.uint8)
mybuf.put(img)

print(mybuf)

img2 = mybuf.get()

img2.index == img.index
img2.timestamp == img.timestamp
all(img2.image == img.image)