# TODO record to file ?

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from qt_widgets import LabeledDoubleSpinBox, LabeledSliderSpinBox, NDarray_to_QPixmap
from camera_tools.camera import Camera

# TODO adjust display FPS

class CameraWidget(QWidget):

    def __init__(self, camera: Camera, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.camera = camera
        self.acquisition_started = False
        
        self.declare_components()
        self.layout_components()
        self.set_timers()

    # UI ---------------------------------------------------------
    
    def create_spinbox(self, attr: str):
        '''
        Creates spinbox with correct label, value, range and increment
        as specified by the camera object. Connects to relevant
        callback
        '''
        setattr(self, attr + '_spinbox', LabeledDoubleSpinBox(self))
        spinbox = getattr(self, attr + '_spinbox')
        callback = getattr(self, 'set_' + attr)
        spinbox.setText(attr)
        spinbox.valueChanged.connect(callback)
        value = getattr(self.camera, 'get_' + attr)()
        range = getattr(self.camera, 'get_' + attr + '_range')()
        increment = getattr(self.camera, 'get_' + attr + '_increment')()
        
        if (
            value is not None 
            and range is not None
            and increment is not None
        ):
            spinbox.setValue(value)
            spinbox.setRange(range)
            spinbox.setSingleStep(increment)
        else:
            spinbox.setDisabled(True)
            
    def declare_components(self):

        # Image --------------------------------------------------

        self.image_label = QLabel(self) 

        # Basic camera controls ----------------------------------
         
        self.start_button = QPushButton(self)
        self.start_button.setText('start')
        self.start_button.clicked.connect(self.start_acquisition)

        self.stop_button = QPushButton(self)
        self.stop_button.setText('stop')
        self.stop_button.clicked.connect(self.stop_acquisition)

        # controls 

        self.create_spinbox('framerate')
        self.create_spinbox('exposure')
        self.create_spinbox('gain')
        self.create_spinbox('offsetX')
        self.create_spinbox('offsetY')
        self.create_spinbox('height')
        self.create_spinbox('width')

        # Region of interest ------------------------------------

        self.ROI_frame = QFrame(self)
        self.ROI_frame.setFrameShape(QFrame.StyledPanel)

    def layout_components(self):

        layout_start_stop = QHBoxLayout()
        layout_start_stop.addWidget(self.start_button)
        layout_start_stop.addWidget(self.stop_button)

        layout_frame = QVBoxLayout(self.ROI_frame)
        layout_frame.addWidget(self.offsetX_spinbox)
        layout_frame.addWidget(self.offsetY_spinbox)
        layout_frame.addWidget(self.height_spinbox)
        layout_frame.addWidget(self.width_spinbox)

        layout_controls = QVBoxLayout()
        layout_controls.addWidget(self.exposure_spinbox)
        layout_controls.addWidget(self.gain_spinbox)
        layout_controls.addWidget(self.framerate_spinbox)
        layout_controls.addWidget(self.ROI_frame)
        layout_controls.addLayout(layout_start_stop)
        layout_controls.addStretch()

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(layout_controls)

    def set_timers(self):

        self.timer = QTimer()
        self.timer.timeout.connect(self.grab)
        self.timer.setInterval(33)
        self.timer.start()

    # Callbacks --------------------------------------------------------- 

    def grab(self):
        if self.acquisition_started:
            frame = self.camera.get_frame()
            self.image_label.setPixmap(NDarray_to_QPixmap(frame.image))

    def start_acquisition(self):
        if not self.acquisition_started:
            self.camera.start_acquisition()
            self.acquisition_started = True
            
    def stop_acquisition(self):
        if self.acquisition_started:
            self.camera.stop_acquisition()
            self.acquisition_started = False

    def set_exposure(self):
        self.camera.set_exposure(self.exposure_spinbox.value())

    def set_gain(self):
        self.camera.set_exposure(self.gain_spinbox.value())

    def set_framerate(self):
        self.camera.set_exposure(self.framerate_spinbox.value())

    def set_offsetX(self):
        self.camera.set_offsetX(self.offsetX_spinbox.value())

    def set_offsetY(self):
        self.camera.set_offsetY(self.offsetY_spinbox.value())

    def set_width(self):
        self.camera.set_width(self.width_spinbox.value())

    def set_height(self):
        self.camera.set_height(self.height_spinbox.value())
       
