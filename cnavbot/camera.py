import time
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    while True:
        time.sleep(10)
        camera.capture('/data/bot.jpg')
