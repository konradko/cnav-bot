import time
from multiprocessing import Process

from cnavbot import settings, logger, messaging


class Service(object):

    def __init__(self, *args, **kwargs):
        self.driver = kwargs.get('driver') or settings.BLUETOOTH_DRIVER
        self.scanner = kwargs.get('scanner') or settings.IBEACON_SCANNER
        self.publisher = kwargs.get('scanner') or messaging.Publisher(
            port=settings.BLUETOOTH_PUBLISHER_PORT
        )

        self.scanning = Process(target=self.scan_and_publish_continuously)

    def run(self):
        logger.info("Starting bluetooth service...")
        self.scanning.start()

    def scan_and_publish_continuously(self):
        """Scan for nearby bluetooth devices"""
        try:
            socket = self.driver.hci_open_dev(0)
            self.scanner.hci_le_set_scan_parameters(socket)
            self.scanner.hci_enable_le_scan(socket)
        except:
            logger.exception("Failed to scan with Bluetooth")
        else:
            while True:
                time.sleep(settings.BLUETOOTH_SCAN_INTERVAL)
                events = self.scanner.parse_events(socket, loop_count=5)

                self.publisher.send(messaging.Message(
                    topic=settings.BLUETOOTH_PUBLISHER_TOPIC,
                    data=events,
                ))


def get_reader():
    return messaging.LastJsonMessageSubscriber(
        publishers=(settings.LOCAL_BLUETOOTH_PUBLISHER_ADDRESS, ),
        topics=(settings.BLUETOOTH_PUBLISHER_TOPIC, )
    )


if __name__ == '__main__':
    Service().run()
