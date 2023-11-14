from .camera import Camera
from dataclasses import dataclass
from typing import Tuple
from numpy.typing import NDArray
import cv2

@dataclass
class Distortion:
    k1: float
    k2: float
    k3: float
    p1: float
    p2: float

def calibration(
        cam: Camera, 
        checkerboard_size: Tuple[int,int],
        checkerboard_corners_world_coordinates: NDArray
    ) -> :
    '''
    Take picture of a checkerboard pattern with known world coordinates, and 
    compute distortion + transformation 
    '''

    
    cam.start_acquisition()



    cam.stop_acquisition()

def get_checkerboard_corners(cam: Camera):

    checkerboard_found = False
    while not checkerboard_found:
        image = cam.get