from .camera import Camera
from typing import Tuple, Optional
from numpy.typing import NDArray
import cv2
from numpy.linalg import lstsq
import numpy as np

def get_camera_distortion(
        cam: Camera, 
        checkerboard_size: Tuple[int,int],
        checkerboard_corners_world_coordinates_mm: NDArray,
        num_images: int = 10
    ) -> Tuple[NDArray, NDArray, NDArray]:
    '''
    Take picture of a checkerboard pattern with known world coordinates, and 
    compute lens distortion + transformation.
    NOTE: The function requires white space (like a square-thick border, the wider the better) 
    around the board to make the detection more robust in various environments. 
    Otherwise, if there is no border and the background is dark, 
    the outer black squares cannot be segmented properly and so 
    the square grouping and ordering algorithm fails.
    Camera settings must be preadjusted for best detection.
    You need to take at least 10 images and move the checkerboard pattern around
    '''
    
    cam.start_acquisition()

    world_coords = []
    image_coords = []
    for i in range(num_images):
        image, corners_px = get_checkerboard_corners(cam, checkerboard_size)
        world_coords.append(checkerboard_corners_world_coordinates_mm)
        image_coords.append(corners_px)

    cam.stop_acquisition()

    shp = image.shape[:2] 

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        world_coords, 
        image_coords, 
        shp[::-1], 
        None, 
        None
    )

    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, shp, 0, shp)

    return mtx, newcameramtx, dist

def get_checkerboard_corners(
        cam: Camera,
        checkerboard_size: Tuple[int,int],
        camera_matrix: Optional[NDArray] = None, 
        distortion_coef: Optional[NDArray] = None
    ) -> Tuple[NDArray, NDArray]: 
    '''
    take a picture every one second and tries to find checkerboard corners
    '''
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    checkerboard_found = False
    cv2.namedWindow('camera')
    while not checkerboard_found:
        # get image from camera
        frame = cam.get_frame()
        image = frame.image

        if camera_matrix is not None:
            image = cv2.undistort(image, camera_matrix, distortion_coef)

        # display image, detect corners if y is pressed
        cv2.imshow('camera', image)
        key = cv2.waitKey(33)

        if key == ord('y'):

            checkerboard_found, corners = cv2.findChessboardCorners(image, checkerboard_size)

            if checkerboard_found:

                corners_sub = cv2.cornerSubPix(image[:,:,1], corners, (11,11), (-1,-1), criteria)

                # show corners
                cv2.drawChessboardCorners(image, checkerboard_size, corners_sub, checkerboard_found)
                cv2.imshow('chessboard', image)
                key = cv2.waitKey(0)

                # return images and detected corner if y is pressed
                if key == ord('y'):
                    cv2.destroyAllWindows()
                    return image, corners
                else:
                    cv2.destroyWindow('chessboard')
                    checkerboard_found = False
            
            else:
                print('checkerboard not found')


def get_camera_px_per_mm(
        cam: Camera,
        checkerboard_size: Tuple[int,int],
        checkerboard_corners_world_coordinates_mm: NDArray,
        camera_matrix: NDArray, 
        distortion_coef: NDArray
    ):
    '''
    Place checkerboard where the images will be recorded
    '''
 
    # get undistorted checkerboard corner locations
    cam.start_acquisition()
    image, corners_px = get_checkerboard_corners(cam, checkerboard_size, camera_matrix, distortion_coef)
    cam.stop_acquisition()

    # use homogeneous coordinates
    world_coords = np.ones_like(checkerboard_corners_world_coordinates_mm)
    world_coords[:,:2] = checkerboard_corners_world_coordinates_mm[:,:2] 

    corners_px = corners_px.squeeze()
    image_coords =  np.ones_like(checkerboard_corners_world_coordinates_mm)
    image_coords[:,:2] = corners_px

    # least square fit 
    world_to_image = lstsq(world_coords, image_coords, rcond=None)[0]
    px_per_mm_X = world_to_image[0,0]
    px_per_mm_Y = world_to_image[1,1]
    px_per_mm = (px_per_mm_X + px_per_mm_Y)/2

    return px_per_mm