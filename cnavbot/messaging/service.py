from multiprocessing import Process

from cnavbot.utils import logger
from cnavbot.messaging import pubsub


class Resource(object):
    topics = {}

    def run(publisher):
        raise NotImplementedError()


class Service(object):

    # required
    name = None
    resource = None
    address = None
    port = None

    # set after start
    resource_instance = None
    process = None

    running = False

    def __init__(self, *args, **kwargs):
        required_attributes = ('name', 'resource', 'address', 'port')

        for attr in required_attributes:
            if kwargs.get(attr):
                setattr(self, attr, kwargs.pop(attr))

        if not all((getattr(self, attr) for attr in required_attributes)):
            raise NotImplementedError(
                "Not all required attributes set: {}".format(
                    ", ".join(required_attributes)
                )
            )

    @classmethod
    def get_subscriber(cls, publisher_address=None):
        return pubsub.Subscriber(
            publishers=(publisher_address or cls.address, ),
            topics=cls.resource.topics.values(),
        )

    def get_publisher(self):
        return pubsub.Publisher(port=self.port)

    def start(self):
        if self.running:
            logger.warning("Service already running")
            return

        logger.info("Starting {} service...".format(self.name))
        self.resource_instance = self.resource()
        self.process = Process(
            target=self.resource_instance.run, args=(self.get_publisher(), )
        )
        self.process.start()
        self.running = True
