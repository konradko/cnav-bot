import json

import zmq


class InvalidMessageError(Exception):
    pass


class Message(object):
    """Summary"""

    def __init__(self, topic, data):
        """
        Args:
            topic (str): topic of the message
            data (str): json-serializable message data
        """
        self.topic = topic
        self.data = data
        self.validate()

    def validate(self):
        try:
            self.serialized
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))

    @property
    def serialized(self):
        """Returns serialized message

        Returns:
            str: serialized message
        """
        return "{topic} {data}".format(
            topic=self.topic, data=json.dumps(self.data)
        )

    @staticmethod
    def deserialize(message):
        """Deserializes a message

        Args:
            message (str): serialized message

        Returns:
            Message: deserialized message
        """
        try:
            topic, data = message.split()
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))
        else:
            return Message(topic=topic, data=data)

    def __unicode__(self):
        return self.serialise()


class Publisher(object):
    """ZMQ publisher"""

    def __init__(self, port):
        """Init publisher

        Args:
            port (int): Port to bind on
        """
        context = zmq.Context()
        self.port = port
        self.socket = context.socket(zmq.PUB)
        self.socket.bind(port)

    def send(self, message):
        """Publish topic data

        Args:
            message (Message): Message to send
        """
        self.socket.send(message.serialized)


class Subscriber(object):
    """ZMQ subscriber"""

    def __init__(self, publishers, topics=None):
        """Init subscriber

        Args:
            publishers ([str]): List of "<host>:<port>" publisher addresses
            topics ([str]): List of topics to subscribe to
        """
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        for publisher in publishers:
            self.socket.connect(publisher)

        for topic in topics:
            self.subscribe(topic)

    def subscribe(self, topic):
        """Subscribe to a topic

        Args:
            topic (str): Topic to subscribe to
        """
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    def get_message(self):
        """Returns a single message from the publishers

        Returns:
            Message: deserialized message
        """
        message = self.socket.recv()
        return Message.deserialize(message=message)


class LastMessageSubscriber(object):
    """ZMQ subscriber reading only the latest message"""

    def __init__(self, *args, **kwargs):
        super(LastMessageSubscriber, self).__init__(*args, **kwargs)
        self.socket.setsockopt(zmq.CONFLATE, 1)
