import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from camera_tools import (
    CameraWidget, XimeaCamera, Camera
)

#cam = MovieFileCam('/home/martin/Downloads/19-40-44.avi')
#cam = OpenCV_Webcam()
#cam = V4L2_Webcam()

#cam = RandomCam(shape=(512,512), dtype=np.uint8)

class MainWindow(QMainWindow):
    
    def __init__(self, camera: Camera, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera_widget = CameraWidget(camera)
        self.setCentralWidget(self.camera_widget)

if __name__ == '__main__':
    cam = XimeaCamera()
    app = QApplication(sys.argv)
    window = MainWindow(cam)
    window.show()
    sys.exit(app.exec())

