import base64
import json
import uuid
import os
import time

import zmq

from cnavbot import settings, logger


class InvalidMessageError(Exception):
    pass


class Message(object):
    """Summary"""

    def __init__(self, topic, data, timestamp=None):
        """
        Args:
            topic (str): topic of the message
            data (str): message data
        """
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.data = data
        self.timestamp = timestamp or time.time()

    def validate(self):
        logger.info("Validating message '{}'".format(self.id))
        try:
            self.serialize()
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))

    def serialize_data(self):
        logger.info("Serializing message '{}' data".format(self.id))
        return str(self.data)

    def serialize(self):
        """Returns serialized message

        Returns:
            str: serialized message
        """
        logger.info("Serializing message '{}'".format(self.id))
        return "{topic} {timestamp} {data}".format(
            topic=self.topic,
            timestamp=self.timestamp,
            data=self.serialize_data()
        )

    def deserialize_data(self):
        logger.info("Deserializing message '{}' data".format(self.id))
        return str(self.data)

    def deserialize(self, message):
        """Deserializes a message

        Args:
            message (str): serialized message

        Returns:
            Message: deserialized message
        """
        logger.info("Deserializing message '{}'".format(self.id))
        try:
            topic, timestamp, data = message.split()
            data = self.deserialize_data(data)
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))
        else:
            return self.__class__(topic=topic, data=data)

    def __unicode__(self):
        return self.serialize()


class JsonMessage(Message):

    def serialize_data(self):
        logger.info("Serializing message '{}' data".format(self.id))
        return json.dumps(self.data)

    def deserialize_data(self):
        logger.info("Deserializing message '{}' data".format(self.id))
        return json.loads(self.data)


class Base64Message(Message):

    def serialize_data(self):
        logger.info("Serializing message '{}' data".format(self.id))
        return base64.b64encode(self.data)

    def deserialize_data(self):
        logger.info("Deserializing message '{}' data".format(self.id))
        return base64.b64decode(self.data)

    @staticmethod
    def get_topic_storage_dir(topic):
        topic_storage_dir = os.path.join(
            settings.FILE_MESSAGE_STORAGE_PATH, topic
        )

        if not os.path.exists(topic_storage_dir):
            os.makedirs(topic_storage_dir)

        return topic_storage_dir

    def save_to_file(self, file_data, file_name):
        logger.info("Saving message '{}' data to a file".format(self.id))
        file_path = os.path.join(
            self.get_topic_storage_dir(self.topic), file_name
        )

        with open(file_path) as destination:
            destination.write(file_data)

        return file_path


class FileMessage(Base64Message):

    def __init__(self, *args, **kwargs):
        self.file_name = kwargs.pop('file_name', str(uuid.uuid4()))
        super(FileMessage, self).__init__(*args, **kwargs)

    def serialize_data(self):
        logger.info("Serializing message '{}' data".format(self.id))
        with open(self.data, 'rb') as source:
            return base64.b64encode(bytearray(source.read()))

    def deserialize_data(self):
        logger.info("Deserializing message '{}' data".format(self.id))
        return self.save_to_file(
            file_data=bytearray(base64.b64decode(self.data)),
            file_name=self.file_name,
        )


class Base64ToFileMessage(FileMessage):

    def serialize_data(self):
        logger.info("Serializing message '{}' data".format(self.id))
        if isinstance(self.data, basestring):
            serialized = super(Base64ToFileMessage, self).serialize_data()
        else:
            serialized = base64.b64encode(bytearray(self.data))

        return serialized

    def deserialize_data(self):
        logger.info("Deserializing message '{}' data".format(self.id))
        return self.save_to_file(
            file_data=bytearray(base64.b64decode(self.data)),
            file_name=self.file_name,
        )


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
        logger.info("Sending message to topic {}".format(message.topic))
        self.socket.send(message.serialize())


class Subscriber(object):
    """ZMQ subscriber"""

    message_class = Message

    def __init__(self, publishers, topics, message_class=None):
        """Init subscriber

        Args:
            publishers ([str]): List of "<host>:<port>" publisher addresses
            topics ([str]): List of topics to subscribe to
        """
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        for publisher in publishers:
            self.connect(publisher)

        for topic in topics:
            self.subscribe(topic)

        if message_class:
            self.message_class = message_class

    def connect(self, publisher):
        logger.info("Connecting to publisher {}".format(publisher))
        self.socket.connect(publisher)

    def subscribe(self, topic):
        """Subscribe to a topic

        Args:
            topic (str): Topic to subscribe to
        """
        logger.info("Subscribing to topic {}".format(topic))
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    def read(self):
        """Returns a single message from the publishers

        Returns:
            Message: deserialized message
        """
        logger.info("Reading message")
        message = self.socket.recv()
        return self.message_class.deserialize(message=message)


class LastMessageSubscriber(Subscriber):
    """ZMQ subscriber reading only the latest message"""

    def __init__(self, *args, **kwargs):
        super(LastMessageSubscriber, self).__init__(*args, **kwargs)
        self.socket.setsockopt(zmq.CONFLATE, 1)


class LastJsonMessageSubscriber(LastMessageSubscriber):
    message_class = JsonMessage


class LastBase64MessageSubscriber(LastMessageSubscriber):
    message_class = Base64Message


class LastFileMessageSubscriber(LastMessageSubscriber):
    message_class = FileMessage


class LastBase64ToFileMessageSubscriber(LastMessageSubscriber):
    message_class = Base64ToFileMessage


