from ximea import xiapi
from multiprocessing import Process, Queue
import os 
import time
from datetime import datetime
import cv2
import pandas
import subprocess
import numpy as np

## parameters -----------------------------
# video preview
DISPLAY_FPS = 30
DISPLAY_SCALE = 0.5
# camera parameters
FPS = 200
EXPOSURE = 6000
GAIN = 4.0
WIDTH  = 2048
HEIGHT = 2048
# video recording
EXP_NUM = 0
FOLDER = 'data'
PREFIX = datetime.today().strftime('%Y_%m_%d') + f'_{EXP_NUM:02d}'
while os.path.isdir(os.path.join(FOLDER, PREFIX)):
    EXP_NUM += 1
    PREFIX = datetime.today().strftime('%Y_%m_%d') + f'_{EXP_NUM:02d}'
os.mkdir(os.path.join(FOLDER, PREFIX))
METADATA_NAME = os.path.join(FOLDER, PREFIX, PREFIX + '.csv')
# video compression
VIDEO_NAME =  os.path.join(FOLDER, PREFIX, PREFIX + '.mp4')
# queue size monitor
MONITOR_RATE_HZ = 10
SLEEP_TIME_S = 0.01
# experiment design
DURATION_S = 60*2
NUMFRAMES = DURATION_S * FPS
# pause
PAUSE_BEFORE = 0
CQ = 10
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

# processes
def monitor_queue_sizes(queue_store, queue_display):
    while True:
        start = time.time()
        while time.time() - start < 1/MONITOR_RATE_HZ:
            time.sleep(SLEEP_TIME_S)
        print(f'Storage: {queue_store.qsize()}, Display: {queue_display.qsize()}', flush = True)

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
        frame_small = cv2.putText(frame_small, f'{cur_time_sec}s', (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, 255)
        cv2.imshow('display', frame_small)
        cv2.waitKey(1)
    cv2.destroyAllWindows()

def compress_image_ffmpeg_GPU(queue_store):
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),  # Frames per second
        "-s", f"{WIDTH}x{HEIGHT}",  # Specify image size
        "-i", "-",  # Input from pipe
        "-c:v", "hevc_nvenc", 
        "-profile:v", "main",
        "-preset", "slow", # try p1 
        "-cq:v", str(CQ),
        "-pix_fmt", "yuv420p",  # Pixel format (required for compatibility)
        VIDEO_NAME,
    ]
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    metadata = []
    while True:
        data = queue_store.get()
        if data is None:
            break
        im_num = data[0]    
        ts_sec = data[1]
        ts_usec = data[2]
        first_time_usec = data[3]
        pixeldata = data[4]
        cur_time_usec =  (ts_sec*1_000_000 +  ts_usec) - first_time_usec
        cur_time_sec = cur_time_usec/1_000_000
        metadata.append([im_num, cur_time_sec])
        pixeldata_RGB = np.dstack((pixeldata,pixeldata,pixeldata))
        ffmpeg_process.stdin.write(pixeldata_RGB.astype(np.uint8).tobytes())

    metadata_df = pandas.DataFrame(metadata, columns=['img_num', 'timestamp_sec'])
    metadata_df.to_csv(METADATA_NAME)
    ffmpeg_process.stdin.flush()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()

def compress_image_ffmpeg_CPU(queue_store):
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),  # Frames per second
        "-s", f"{WIDTH}x{HEIGHT}",  # Specify image size
        "-i", "-",  # Input from pipe
        "-c:v", "libx264", 
        "-profile:v", "baseline",
        "-preset", "fast", # try p1 
        "-crf", str(CQ),
        "-pix_fmt", "yuv420p",  # Pixel format (required for compatibility)
        VIDEO_NAME,
    ]
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    metadata = []
    while True:
        data = queue_store.get()
        if data is None:
            break
        im_num = data[0]    
        ts_sec = data[1]
        ts_usec = data[2]
        first_time_usec = data[3]
        pixeldata = data[4]
        cur_time_usec =  (ts_sec*1_000_000 +  ts_usec) - first_time_usec
        cur_time_sec = cur_time_usec/1_000_000
        metadata.append([im_num, cur_time_sec])
        pixeldata_RGB = np.dstack((pixeldata,pixeldata,pixeldata))
        ffmpeg_process.stdin.write(pixeldata_RGB.astype(np.uint8).tobytes())

    metadata_df = pandas.DataFrame(metadata, columns=['img_num', 'timestamp_sec'])
    metadata_df.to_csv(METADATA_NAME)
    ffmpeg_process.stdin.flush()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()

queue_store = Queue()
queue_display = Queue()
queue_sound = Queue()

store = Process(target=compress_image_ffmpeg_GPU, args=(queue_store,))
display = Process(target=display_image, args=(queue_display,))
monitor = Process(target=monitor_queue_sizes, args=(queue_store, queue_display))

# experiment loop
input("""
Make sure that the IR LED power supply is on.
Press Enter to start the experiment ...
""")
print(f'Waiting {PAUSE_BEFORE}s...')
time.sleep(PAUSE_BEFORE)      
print('Experiment starting')

monitor.start()
display.start()
store.start()

try:
    # img.acq_nframe is one-indexed
    cam.start_acquisition()
    for i in range(NUMFRAMES):
        # get image and metadata
        cam.get_image(img)
        pixeldata = img.get_image_data_numpy()
        im_num = img.acq_nframe
        ts_sec = img.tsSec
        ts_usec = img.tsUSec
        if im_num == 1: # xiapi.Image.acq_nframe is one-based
            first_time_usec = ts_sec*1_000_000 +  ts_usec

        # put on queue
        queue_store.put((im_num, ts_sec, ts_usec, first_time_usec, pixeldata))
        if (im_num*1000/FPS) % DISPLAY_FPS*1000 == 0:
            queue_display.put((im_num, ts_sec, ts_usec, first_time_usec, pixeldata))
finally:
    # send stop signal
    queue_sound.put(None)
    queue_store.put(None)
    queue_display.put(None)
    cam.stop_acquisition()
    cam.close_device()
    store.join()
    display.join()
    monitor.terminate()

