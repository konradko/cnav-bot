import time
import datetime

import cv2
import numpy as np

from picamera.array import PiRGBArray
from picamera import PiCamera

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

    blur = cv2.blur(frame, (3, 3))

    # Bright green
    lower = np.array([10, 150, 0], dtype="uint8")
    upper = np.array([120, 255, 0], dtype="uint8")

    thresh = cv2.inRange(blur, lower, upper)
    thresh2 = thresh.copy()

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )

    max_area = 1000
    largest_area_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            largest_area_contour = contour

    if not largest_area_contour:
        continue

    moments = cv2.moments(largest_area_contour)
    centre = ((int(moments['m10'] / moments['m00']),
               int(moments['m01'] / moments['m00'])))
    print "{} - {}".format(datetime.datetime.now(), centre)

