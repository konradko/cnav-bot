# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
camera.hflip = True

rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array

    blur = cv2.blur(image, (3, 3))

    lower = np.array([76, 31, 4], dtype="uint8")
    upper = np.array([210, 90, 70], dtype="uint8")

    thresh = cv2.inRange(blur, lower, upper)
    thresh2 = thresh.copy()

    # find contours in the threshold image
    image, contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # finding contour with maximum area and store it as best_cnt
    max_area = 100
    best_cnt = 1
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            best_cnt = cnt

    moments = cv2.moments(best_cnt)
    centre = ((int(moments['m10'] / moments['m00']),
               int(moments['m01'] / moments['m00'])))
    print centre

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
