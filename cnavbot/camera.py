import datetime
from io import BytesIO
import time
from multiprocessing import Process

from cnavbot import settings, logger, messaging


class Service(object):

    def __init__(self, *args, **kwargs):
        self.interval = kwargs.get('interval', settings.CAMERA_INTERVAL)
        self.resolution = kwargs.get('resolution', settings.CAMERA_RESOLUTION)
        self.camera = kwargs.get('camera', settings.CAMERA)
        self.publisher = kwargs.get(
            'publisher',
            messaging.LastMessagePublisher(
                port=settings.CAMERA_PUBLISHER_PORT
            )
        )
        self.capturing = Process(target=self.take_picture_continously)

    def run(self):
        logger.info("Starting camera service...")
        self.capturing.start()

    @staticmethod
    def get_file_name():
        return "{}.jpg".format(datetime.datetime.utcnow().isoformat())

    def take_picture_continously(self):
        with self.camera.PiCamera() as camera:
            camera.resolution = self.resolution
            while True:
                time.sleep(self.interval)
                stream = BytesIO()
                camera.capture(stream, 'jpeg')
                file_name = self.get_file_name()
                logger.info("Picture taken: {}".format(file_name))

                self.publisher.send(messaging.FilePathMessage(
                    topic=settings.CAMERA_PUBLISHER_TOPIC,
                    data=stream.read(),
                    file_name=file_name,
                ))


def get_reader():
    return messaging.LastMessageSubscriber(
        publishers=(settings.LOCAL_CAMERA_PUBLISHER_ADDRESS, ),
        topics=(settings.CAMERA_PUBLISHER_TOPIC, )
    )


if __name__ == '__main__':
    Service().run()
