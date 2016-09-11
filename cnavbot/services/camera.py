import datetime
import io
import time

from zmqservices import messages, services, pubsub
from cnavconstants.publishers import (
    LOCAL_CAMERA_ADDRESS, CAMERA_SERVICE_PORT
)
import cnavconstants.topics

from cnavbot import settings
from cnavbot.utils import logger, log_exceptions


class Camera(services.PublisherResource):
    topics = {
        'pictures': cnavconstants.topics.CAMERA,
    }
    capture_to_stream = True

    def __init__(self, *args, **kwargs):
        super(Camera, self).__init__(*args, **kwargs)

        self.interval = kwargs.pop('interval', settings.CAMERA_INTERVAL)
        self.resolution = kwargs.pop('resolution', settings.CAMERA_RESOLUTION)
        self.camera = kwargs.pop('camera', settings.CAMERA)

    def run(self):
        with log_exceptions():
            with self.camera.PiCamera() as camera:
                camera.resolution = self.resolution
                while True:
                    time.sleep(self.interval)

                    if self.capture_to_stream:
                        message = messages.Base64()
                        destination = io.BytesIO()
                        capture_args = (destination, 'jpeg')
                    else:
                        message = messages.FilePath()
                        message.set_file_path(file_name=self.get_file_name())
                        destination = message.file_path
                        message.data = destination
                        capture_args = (destination, )

                    self.take_picture(camera, capture_args)

                    if self.capture_to_stream:
                        message.data = destination.read()

                    message.topic = self.topics['pictures']
                    self.publisher.send(message)

    def take_picture(self, camera, capture_args):
        logger.debug("Taking picture")
        return camera.capture(*capture_args)

    @staticmethod
    def get_file_name():
        return "{}.jpg".format(datetime.datetime.utcnow().isoformat())


class Service(services.PublisherService):
    name = 'camera'
    resource = Camera
    address = LOCAL_CAMERA_ADDRESS
    port = CAMERA_SERVICE_PORT
    publisher = pubsub.LastMessagePublisher
    subscriber = pubsub.LastMessageSubscriber


def start():
    return Service().start()


if __name__ == '__main__':
    start()
