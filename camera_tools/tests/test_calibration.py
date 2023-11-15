import numpy as np
from camera_tools import XimeaCamera, get_camera_distortion, get_camera_px_per_mm
import pickle

cam = XimeaCamera()

WIDTH = 1800
HEIGHT = 1800
EXPOSURE = 3000
FPS = 30
GAIN = 0

# get ROI parameters 
x_inc = cam.get_offsetX_increment()
y_inc = cam.get_offsetY_increment()
max_width = cam.get_offsetX_range()[1]+cam.get_width_range()[1]
max_height = cam.get_offsetY_range()[1]+cam.get_height_range()[1]
OFFSET_X = int((max_width-WIDTH)/(2*x_inc))*x_inc
OFFSET_Y = int((max_height-HEIGHT)/(2*y_inc))*y_inc

# configure camera
cam.set_exposure(EXPOSURE)
cam.set_framerate(FPS)
cam.set_gain(GAIN)
cam.set_width(WIDTH)
cam.set_height(HEIGHT)
cam.set_offsetX(OFFSET_X)
cam.set_offsetY(OFFSET_Y)

checker_sz = (9,6)
square_sz_mm = 2

objp = np.zeros((np.prod(checker_sz),3), np.float32)
objp[:,:2] = np.mgrid[
    0:checker_sz[0]*square_sz_mm:square_sz_mm,
    0:checker_sz[1]*square_sz_mm:square_sz_mm
].T.reshape(-1,2)

mtx, newcameramtx, dist = get_camera_distortion(cam,checker_sz,objp)
px_per_mm = get_camera_px_per_mm(cam,checker_sz,objp, newcameramtx, dist)

# if you do not wish to correct distortion
# px_per_mm = get_camera_px_per_mm(cam,checker_sz,objp, None, None)

with open('ximea.pkl', 'wb') as f:
    pickle.dump(
        {'camera_matrix': mtx, 
        'new_camera_matrix': newcameramtx, 
        'distortion': dist, 
        'px_per_mm': px_per_mm}, 
        f
    )