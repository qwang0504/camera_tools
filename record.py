from multiprocessing import Process, Event
import os 
import time
from datetime import datetime
import cv2
import pandas
import subprocess
import numpy as np
from camera_tools import Frame_RingBuffer, OpenCV_Webcam, XimeaCamera
from queue import Empty


## parameters -----------------------------
# video preview
DISPLAY_FPS = 30
DISPLAY_SCALE = 0.5
# camera parameters
FPS = 50
EXPOSURE = 4000
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
DURATION_S = 60*30
NUMFRAMES = DURATION_S * FPS
# pause
PAUSE_BEFORE_S = 0
CQ = 10
## ------------------------------------------    

# open camera 
cam = XimeaCamera()

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

# processes
def monitor_queue_sizes(queue_store, queue_display, stop_event: Event):
    while not stop_event.is_set():
        start = time.time()
        while time.time() - start < 1/MONITOR_RATE_HZ:
            time.sleep(SLEEP_TIME_S)
        print(f'Storage: {queue_store.qsize()}, Display: {queue_display.qsize()}', flush = True)

def display_image(queue_display, stop_event: Event):
    cv2.namedWindow('display')
    while not stop_event.is_set():
        try:
            data = queue_display.get()
            frame_small = cv2.resize(data.image, None, None, DISPLAY_SCALE, DISPLAY_SCALE)
            frame_small = cv2.putText(frame_small, f'{data.timestamp}s', (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, 255)
            cv2.imshow('display', frame_small)
            cv2.waitKey(1)
        except Empty:
            pass
    cv2.destroyAllWindows()

def compress_image_ffmpeg_GPU(queue_store, stop_event: Event):
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
    while not stop_event.is_set():
        try:
            data = queue_store.get()
            metadata.append([data.index, data.timestamp])
            pixeldata_RGB = np.dstack((data.image,data.image,data.image))
            ffmpeg_process.stdin.write(pixeldata_RGB.tobytes())
        except Empty:
            pass

    metadata_df = pandas.DataFrame(metadata, columns=['img_num', 'timestamp_sec'])
    metadata_df.to_csv(METADATA_NAME)
    ffmpeg_process.stdin.flush()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()

def compress_image_ffmpeg_CPU(queue_store, stop_event: Event):
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
    while not stop_event.is_set():
        data = queue_store.get()
        if data is None:
            break
        metadata.append([data.index, data.timestamp])
        ffmpeg_process.stdin.write(data.image.tobytes())

    metadata_df = pandas.DataFrame(metadata, columns=['img_num', 'timestamp_sec'])
    metadata_df.to_csv(METADATA_NAME)
    ffmpeg_process.stdin.flush()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()

queue_display = Frame_RingBuffer(
    num_items=100,
    frame_shape=(HEIGHT,WIDTH),
    frame_dtype=np.uint8,
    copy = False
)
queue_store = Frame_RingBuffer(
    num_items=100,
    frame_shape=(HEIGHT,WIDTH),
    frame_dtype=np.uint8,
    copy = False
)
stop = Event()

store = Process(target=compress_image_ffmpeg_GPU, args=(queue_store,stop))
display = Process(target=display_image, args=(queue_display,stop))
monitor = Process(target=monitor_queue_sizes, args=(queue_store, queue_display,stop))

# experiment loop
input("""
Make sure that the IR LED power supply is on.
Press Enter to start the experiment ...
""")
print(f'Waiting {PAUSE_BEFORE_S}s...')
time.sleep(PAUSE_BEFORE_S)      
print('Experiment starting')

monitor.start()
display.start()
store.start()

try:
    # img.acq_nframe is one-indexed
    cam.start_acquisition()
    for i in range(NUMFRAMES):
        # get image and metadata
        frame = cam.get_frame()
        # put on queue
        queue_store.put(frame)
        if (frame.index*1000/FPS) % DISPLAY_FPS*1000 == 0:
            queue_display.put(frame)
finally:
    # send stop signal
    stop.set()
    cam.stop_acquisition()
    store.join()
    display.join()
    monitor.join()

