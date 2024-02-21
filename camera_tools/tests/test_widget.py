import sys
from PyQt5.QtWidgets import QApplication
from camera_tools import (
    CameraWidget, XimeaCamera
)

#cam = MovieFileCam('/home/martin/Downloads/19-40-44.avi')
#cam = OpenCV_Webcam()
#cam = V4L2_Webcam()
cam = XimeaCamera()
#cam = RandomCam(shape=(512,512), dtype=np.uint8)


# test widget
app = QApplication(sys.argv)
window = CameraWidget(cam)
window.show()
sys.exit(app.exec())

