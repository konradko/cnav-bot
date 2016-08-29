import time

from cnavbot import settings
from cnavbot.utils import logger, sentry
from cnavbot.messaging import pubsub, messages, service


class Service(service.Base):
    name = 'bluetooth'

    def __init__(self, *args, **kwargs):
        self.driver = kwargs.get('driver', settings.BLUETOOTH_DRIVER)
        self.scanner = kwargs.get('scanner', settings.IBEACON_SCANNER)

        super(Service, self).__init__(self, *args, **kwargs)

    @staticmethod
    def get_subscriber():
        return pubsub.LastMessageSubscriber(
            publishers=(settings.LOCAL_BLUETOOTH_PUBLISHER_ADDRESS, ),
            topics=(settings.BLUETOOTH_PUBLISHER_TOPIC, )
        )

    def run(self):
        publisher = pubsub.LastMessagePublisher(
            port=settings.BLUETOOTH_PUBLISHER_PORT
        )
        try:
            logger.info("Connecting to bluetooth device...")
            socket = self.driver.hci_open_dev(0)
            scanner = self.scanner
            scanner.hci_le_set_scan_parameters(socket)
            scanner.hci_enable_le_scan(socket)
        except Exception as e:
            logger.exception(
                u"Failed to connect to bluetooth device: {}".format(e)
            )
        else:
            logger.info("Scanning with bluetooth")
            while True:
                time.sleep(settings.BLUETOOTH_SCAN_INTERVAL)
                self.publish_scan_results(publisher, socket, scanner)

    @staticmethod
    def scan(socket, scanner):
        logger.debug("Scanning with bluetooth...")
        return scanner.parse_events(socket, loop_count=5)

    @classmethod
    def publish_scan_results(cls, publisher, socket, scanner):
        scan_results = cls.scan(socket, scanner)

        publisher.send(messages.JSON(
            topic=settings.BLUETOOTH_PUBLISHER_TOPIC,
            data=scan_results,
        ))


@sentry
def start():
    return Service()


if __name__ == '__main__':
    start()
