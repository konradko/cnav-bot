import time

from zmqservices import messages, services, pubsub

from cnavbot import settings
from cnavbot.utils import logger, sentry


class Bluetooth(services.PublisherResource):
    topics = {
        'scan': settings.BLUETOOTH_TOPIC,
    }

    def __init__(self, *args, **kwargs):
        super(Bluetooth, self).__init__(*args, **kwargs)

        self.driver = kwargs.pop('driver', settings.BLUETOOTH_DRIVER)
        self.scanner = kwargs.pop('scanner', settings.IBEACON_SCANNER)

    def run(self):

        self.connect()
        logger.info("Scanning with bluetooth")

        while True:
            time.sleep(settings.BLUETOOTH_SCAN_INTERVAL)

            self.publisher.send(messages.JSON(
                topic=self.topics['scan'],
                data=self.scan(),
            ))

    def connect(self):
        logger.info("Connecting to bluetooth device...")
        self.socket = self.driver.hci_open_dev(0)
        self.scanner.hci_le_set_scan_parameters(self.socket)
        self.scanner.hci_enable_le_scan(self.socket)

    def scan(self):
        logger.debug("Scanning with bluetooth...")
        return [
            self.parse(result) for result in
            self.scanner.parse_events(self.socket, loop_count=10)
        ]

    @staticmethod
    def parse(result):
        mac, uuid, major, minor, txpower, rssi = result.split(",")

        return {
            'mac': mac,
            'uuid': uuid,
            'major': major,
            'minor': minor,
            'txpower': txpower,
            'rssi': rssi,
        }


class Service(services.PublisherService):
    name = 'bluetooth'
    resource = Bluetooth
    address = settings.LOCAL_BLUETOOTH_PUBLISHER_ADDRESS
    port = settings.BLUETOOTH_PORT_ADDRESS
    publisher = pubsub.LastMessagePublisher
    subscriber = pubsub.LastMessageSubscriber


@sentry
def start():
    return Service()


if __name__ == '__main__':
    start()
