import sys
from PyQt5.QtWidgets import QApplication
from camera_tools.camera_widget import CameraWidget
from camera_tools.webcam import OpenCV_Webcam

cam = OpenCV_Webcam()

# test widget
app = QApplication(sys.argv)
window = CameraWidget(cam)
window.show()
sys.exit(app.exec())

