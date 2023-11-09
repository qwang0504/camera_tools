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

        self.framerate_spinbox = LabeledDoubleSpinBox(self)
        self.framerate_spinbox.setText('fps')
        self.framerate_spinbox.valueChanged.connect(self.set_framerate)
        framerate_value = self.camera.get_framerate()
        if framerate_value is not None:
            self.framerate_spinbox.setValue(framerate_value) 
            framerate_range = self.camera.get_framerate_range()
            if framerate_range  is not None:
                self.framerate_spinbox.setRange(framerate_range )
        else:
            self.framerate_spinbox.setDisabled(True)

        self.exposure_spinbox = LabeledDoubleSpinBox(self)
        self.exposure_spinbox.setText('exposure')
        self.exposure_spinbox.valueChanged.connect(self.set_exposure)
        exposure_value = self.camera.get_exposure()
        if exposure_value is not None:
            self.exposure_spinbox.setValue(exposure_value) 
            exposure_range = self.camera.get_exposure_range()
            if exposure_range is not None:
                self.exposure_spinbox.setRange(exposure_range)
        else:
            self.exposure_spinbox.setDisabled(True)

        self.gain_spinbox = LabeledDoubleSpinBox(self)
        self.gain_spinbox.setText('gain')
        self.gain_spinbox.valueChanged.connect(self.set_gain)
        gain_value = self.camera.get_gain()
        if gain_value is not None:
            self.gain_spinbox.setValue(gain_value)
            gain_range = self.camera.get_gain_range()
            if gain_range is not None:
                self.gain_spinbox.setRange(gain_range)
        else:
            self.gain_spinbox.setDisabled(True)

        # Region of interest ------------------------------------

        self.ROI_frame = QFrame(self)
        self.ROI_frame.setFrameShape(QFrame.StyledPanel)

        self.left_spinbox = LabeledSliderSpinBox(self.ROI_frame)
        self.left_spinbox.setText('left')
        self.left_spinbox.valueChanged.connect(self.set_ROI)
        offsetX_value = 
        offsetX_range = self.camera.get_offsetX_range()
        offsetX_increment = self.camera.get_offsetX_increment()
        if (offsetX_range is not None) and (offsetX_increment is not None):
            self.left_spinbox.setRange(offsetX_range)
            self.left_spinbox.setSingleStep(offsetX_increment)
        else:
            self.left_spinbox.setDisabled(True)

        self.bottom_spinbox = LabeledSliderSpinBox(self.ROI_frame)
        self.bottom_spinbox.setText('bottom')
        self.bottom_spinbox.valueChanged.connect(self.set_ROI)
        offsetY_range = self.camera.get_offsetY_range()
        offsetY_increment = self.camera.get_offsetY_increment()   
        if (offsetY_range is not None) and (offsetY_increment is not None):
            self.bottom_spinbox.setRange(offsetY_range)
            self.bottom_spinbox.setSingleStep(offsetY_increment)
        else:
            self.bottom_spinbox.setDisabled(True)

        self.height_spinbox = LabeledSliderSpinBox(self.ROI_frame)
        self.height_spinbox.setText('height')
        self.height_spinbox.valueChanged.connect(self.set_ROI)
        height_range = self.camera.get_height_range()
        if (height_range is not None) and (offsetY_increment is not None):
            self.height_spinbox.setRange(height_range)
            self.height_spinbox.setSingleStep(offsetY_increment)
        else:
            self.height_spinbox.setDisabled(True)

        self.width_spinbox = LabeledSliderSpinBox(self.ROI_frame)
        self.width_spinbox.setText('width')
        self.width_spinbox.valueChanged.connect(self.set_ROI)
        width_range = self.camera.get_width_range()
        if (width_range is not None) and (offsetX_increment is not None):
            self.width_spinbox.setRange(width_range)
            self.width_spinbox.setSingleStep(offsetX_increment)
        else:
            self.width_spinbox.setDisabled(True)

    def layout_components(self):

        layout_start_stop = QHBoxLayout()
        layout_start_stop.addWidget(self.start_button)
        layout_start_stop.addWidget(self.stop_button)

        layout_frame = QVBoxLayout(self.ROI_frame)
        layout_frame.addWidget(self.left_spinbox)
        layout_frame.addWidget(self.bottom_spinbox)
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

    def set_ROI(self):
        self.camera.set_ROI(
            left = self.left_spinbox.value(),
            bottom = self.bottom_spinbox.value(),
            height = self.height_spinbox.value(),
            width = self.width_spinbox.value()
        )


