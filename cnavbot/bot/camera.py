import datetime
import time

from cnavbot import settings
from cnavbot.utils import logger, sentry
from cnavbot.messaging import pubsub, messages, service


class Service(service.Base):
    name = 'camera'

    def __init__(self, *args, **kwargs):
        self.interval = kwargs.get('interval', settings.CAMERA_INTERVAL)
        self.resolution = kwargs.get('resolution', settings.CAMERA_RESOLUTION)
        self.camera = kwargs.get('camera', settings.CAMERA)

        super(Service, self).__init__(self, *args, **kwargs)

    @staticmethod
    def get_subscriber():
        return pubsub.LastMessageSubscriber(
            publishers=(settings.LOCAL_CAMERA_PUBLISHER_ADDRESS, ),
            topics=(settings.CAMERA_PUBLISHER_TOPIC, )
        )

    def run(self):
        publisher = pubsub.LastMessagePublisher(
            port=settings.CAMERA_PUBLISHER_PORT
        )
        with self.camera.PiCamera() as camera:
            camera.resolution = self.resolution
            while True:
                time.sleep(self.interval)
                self.publish_pictures(publisher, camera)

    @staticmethod
    def get_file_name():
        return "{}.jpg".format(datetime.datetime.utcnow().isoformat())

    @staticmethod
    def take_picture(camera, file_path):
        camera.capture(file_path)
        logger.debug("Picture taken: '{}'".format(file_path))

    @classmethod
    def publish_pictures(cls, publisher, camera):
        message = messages.FilePath(
            topic=settings.CAMERA_PUBLISHER_TOPIC,
        )
        message.set_file_path(file_name=cls.get_file_name())

        cls.take_picture(camera, message.file_path)

        publisher.send(message)


@sentry
def start():
    return Service()


if __name__ == '__main__':
    start()
