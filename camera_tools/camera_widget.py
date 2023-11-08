# basic widget that provide support for abstract camera functionalities

# + record to file ?

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from qt_widgets import LabeledDoubleSpinBox, LabeledSliderSpinBox, NDarray_to_QPixmap
from camera_tools.camera import Camera
from camera_tools.frame import Frame, BaseFrame

class CameraWidget(QWidget):

    def __init__(self, camera: Camera, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.camera = camera
        self.declare_components()
        self.layout_components()
    
    def declare_components(self):

        # Image --------------------------------------------------
        
        self.image_label = QLabel(self) 

        # Basic camera controls ----------------------------------
         
        self.start_button = QPushButton(self)
        self.start_button.setText('start')

        self.stop_button = QPushButton(self)
        self.stop_button.setText('stop')

        self.framerate_spinbox = LabeledDoubleSpinBox(self)
        self.framerate_spinbox.setText('fps')

        self.exposure_spinbox = LabeledDoubleSpinBox(self)
        self.exposure_spinbox.setText('exposure')

        self.gain_spinbox = LabeledDoubleSpinBox(self)
        self.gain_spinbox.setText('gain')

        # Region of interest ------------------------------------

        self.ROI_frame = QFrame(self)
        self.ROI_frame.setFrameShape(QFrame.StyledPanel)

        self.left_spinbox = LabeledSliderSpinBox(self.ROI_frame)
        self.left_spinbox.setText('left')

        self.bottom_spinbox = LabeledSliderSpinBox(self.ROI_frame)
        self.bottom_spinbox.setText('bottom')

        self.height_spinbox = LabeledSliderSpinBox(self.ROI_frame)
        self.height_spinbox.setText('height')

        self.width_spinbox = LabeledSliderSpinBox(self.ROI_frame)
        self.width_spinbox.setText('width')
    
    def layout_components(self):

        layout_start_stop = QHBoxLayout(self)
        layout_start_stop.addWidget(self.start_button)
        layout_start_stop.addWidget(self.stop_button)

        layout_frame = QVBoxLayout(self.ROI_frame)
        layout_frame.addWidget(self.left_spinbox)
        layout_frame.addWidget(self.bottom_spinbox)
        layout_frame.addWidget(self.height_spinbox)
        layout_frame.addWidget(self.width_spinbox)

        layout_controls = QVBoxLayout(self)
        layout_controls.addWidget(self.exposure_spinbox)
        layout_controls.addWidget(self.gain_spinbox)
        layout_controls.addWidget(self.framerate_spinbox)
        layout_controls.addWidget(self.ROI_frame)
        layout_controls.addLayout(layout_start_stop)





