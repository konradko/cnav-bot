from multiprocessing import Process

from cnavbot.utils import logger
from cnavbot.messaging import pubsub


class Resource(object):
    topics = {}

    def __init__(self, publisher, *args, **kwargs):
        self.publisher = publisher

    def run(publisher):
        raise NotImplementedError()


class Service(object):
    publisher = pubsub.Publisher
    subscriber = pubsub.Subscriber

    # required
    name = None
    resource = None
    address = None
    port = None

    # set after start
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
        return cls.subscriber(
            publishers=(publisher_address or cls.address, ),
            topics=cls.resource.topics.values(),
        )

    @classmethod
    def get_publisher(cls):
        return cls.publisher(port=cls.port)

    def start(self):
        if self.running:
            logger.warning("Service already running")
            return

        logger.info("Starting {} service...".format(self.name))
        self.process = Process(target=self.run_resource)
        self.process.start()
        self.running = True

    def run_resource(self):
        resource_instance = self.resource(publisher=self.get_publisher())
        resource_instance.run()
