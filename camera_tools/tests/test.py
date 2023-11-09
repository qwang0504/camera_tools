import sys
from PyQt5.QtWidgets import QApplication
from camera_tools import CameraWidget, OpenCV_Webcam, ZeroCam, RandomCam
import numpy as np

cam = OpenCV_Webcam()
#cam = RandomCam(shape=(512,512), dtype=np.uint8)


# test widget
app = QApplication(sys.argv)
window = CameraWidget(cam)
window.show()
sys.exit(app.exec())

