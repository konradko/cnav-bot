import datetime
import time

from cnavbot import settings
from cnavbot.utils import logger, sentry
from cnavbot.messaging import messages, service


class Camera(service.Resource):
    topics = {
        'take_picture': settings.CAMERA_TOPIC,
    }

    def __init__(self, *args, **kwargs):
        super(Camera, self).__init__(*args, **kwargs)

        self.interval = kwargs.pop('interval', settings.CAMERA_INTERVAL)
        self.resolution = kwargs.pop('resolution', settings.CAMERA_RESOLUTION)
        self.camera = kwargs.pop('camera', settings.CAMERA)

    def run(self):
        with self.camera.PiCamera() as camera:
            camera.resolution = self.resolution
            while True:
                time.sleep(self.interval)
                self.take_picture(camera)

    def take_picture(self, camera):
        message = messages.FilePath(topic=self.topics['take_picture'])
        message.set_file_path(file_name=self.get_file_name())

        camera.capture(message.file_path)
        logger.debug("Picture taken: '{}'".format(message.file_path))

        self.publisher.send(message)

    @staticmethod
    def get_file_name():
        return "{}.jpg".format(datetime.datetime.utcnow().isoformat())


class Service(service.Service):
    name = 'camera'
    resource = Camera
    address = settings.LOCAL_CAMERA_PUBLISHER_ADDRESS
    port = settings.CAMERA_PORT_ADDRESS


@sentry
def start():
    return Service()


if __name__ == '__main__':
    start()
