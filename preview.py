from psychopy import sound
from ximea import xiapi
from multiprocessing import Process, Queue
import os 
import time
from datetime import datetime
import cv2
import pandas

## parameters -----------------------------
# video preview
DISPLAY_FPS = 30
DISPLAY_SCALE = 0.5
# camera parameters
FPS = 60
EXPOSURE = 5000
GAIN = 4.0
WIDTH  = 1536
HEIGHT = 1536
# queue size monitor
MONITOR_RATE_HZ = 10
SLEEP_TIME_S = 0.01
## ------------------------------------------    

# open camera 
cam = xiapi.Camera()
cam.open_device()
img = xiapi.Image()

# get ROI parameters 
x_inc = cam.get_offsetX_increment()
y_inc = cam.get_offsetY_increment()
max_width = cam.get_offsetX_maximum()+cam.get_width_maximum()
max_height = cam.get_offsetY_maximum()+cam.get_height_maximum()
OFFSET_X = int((max_width-WIDTH)/(2*x_inc))*x_inc
OFFSET_Y = int((max_height-HEIGHT)/(2*y_inc))*y_inc

# configure camera
cam.set_exposure(EXPOSURE)
cam.set_acq_timing_mode('XI_ACQ_TIMING_MODE_FRAME_RATE_LIMIT')
cam.set_framerate(FPS)
cam.set_gain(GAIN)
cam.set_width(WIDTH)
cam.set_height(HEIGHT)
cam.set_offsetX(OFFSET_X)
cam.set_offsetY(OFFSET_Y)

def monitor_queue_sizes(queue_store, queue_display, queue_sound):
    while True:
        start = time.time()
        while time.time() - start < 1/MONITOR_RATE_HZ:
            time.sleep(SLEEP_TIME_S)
        print(f'Storage: {queue_store.qsize()}, Display: {queue_display.qsize()}, Sound: {queue_sound.qsize()}', flush = True)

def display_image(queue_display):
    cv2.namedWindow('display')
    while True:
        data = queue_display.get()
        if data is None:
            break
        im_num = data[0]    
        ts_sec = data[1]
        ts_usec = data[2]
        first_time_usec = data[3]
        pixeldata = data[4]
        frame = pixeldata.reshape(HEIGHT,WIDTH)
        cur_time =  (ts_sec*1_000_000 +  ts_usec) - first_time_usec
        cur_time_sec = cur_time/1_000_000
        frame_small = cv2.resize(frame, None, None, DISPLAY_SCALE, DISPLAY_SCALE)
        cv2.imshow('display', frame_small)
        cv2.waitKey(1)
    cv2.destroyAllWindows()


queue_display = Queue()

display = Process(target=display_image, args=(queue_display,))
monitor = Process(target=monitor_queue_sizes, args=(queue_display,))

monitor.start()
display.start()

# img.acq_nframe is one-indexed
cam.start_acquisition()
while True:
    try:
        # get image and metadata
        cam.get_image(img)
        pixeldata = img.get_image_data_numpy()
        im_num = img.acq_nframe
        ts_sec = img.tsSec
        ts_usec = img.tsUSec
        if im_num == 1: # xiapi.Image.acq_nframe is one-based
            first_time_usec = ts_sec*1_000_000 +  ts_usec
        if (im_num*1000/FPS) % DISPLAY_FPS*1000 == 0:
            queue_display.put((im_num, ts_sec, ts_usec, first_time_usec, pixeldata))
    except:
        cam.stop_acquisition()
        cam.close_device()
        queue_display.put(None)
        display.join()
        monitor.terminate()
        break


