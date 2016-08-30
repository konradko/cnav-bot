import datetime
import io
import time

from cnavbot import settings
from cnavbot.utils import logger, sentry
from cnavbot.messaging import messages, service


class Camera(service.Resource):
    topics = {
        'pictures': settings.CAMERA_TOPIC,
    }
    capture_to_stream = True

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

                self.take_picture(camera, *capture_args)

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
