from collections import defaultdict
import logging
import time

from zmqservices import messages, services, pubsub
from cnavconstants.publishers import (
    LOCAL_BLUETOOTH_ADDRESS, BLUETOOTH_SERVICE_PORT
)
import cnavconstants.topics

from cnavbot import settings
from cnavbot.utils import log_exceptions


numpy = settings.NUMPY

logger = logging.getLogger()


class Bluetooth(services.PublisherResource):
    topics = {
        'scan': cnavconstants.topics.BLUETOOTH,
    }

    def __init__(self, *args, **kwargs):
        super(Bluetooth, self).__init__(*args, **kwargs)

        self.driver = kwargs.pop('driver', settings.BLUETOOTH_DRIVER)
        self.scanner = kwargs.pop('scanner', settings.IBEACON_SCANNER)

    def run(self):
        with log_exceptions():
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
        parsed = [
            self.parse(result) for result in
            self.scanner.parse_events(self.socket, loop_count=100)
        ]
        return self.filter_beacons(results=parsed)

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

    @staticmethod
    def filter_beacons(results):
        rssis_per_beacon = defaultdict(list)

        for result in results:
            if result['uuid'] in settings.BEACONS:
                rssis_per_beacon[result['uuid']].append(int(result['rssi']))

        return {
            beacon: numpy.mean(rssis)
            for beacon, rssis in rssis_per_beacon.iteritems()
        }


class Service(services.PublisherService):
    name = 'bluetooth'
    resource = Bluetooth
    address = LOCAL_BLUETOOTH_ADDRESS
    port = BLUETOOTH_SERVICE_PORT
    publisher = pubsub.LastMessagePublisher
    subscriber = pubsub.LastMessageSubscriber


def start():
    return Service().start()


if __name__ == '__main__':
    start()
