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

    def serialize_data(self, data):
        return str(data)

    def serialize(self):
        """Returns serialized message

        Returns:
            str: serialized message
        """
        logger.info("Serializing message '{}'".format(self.id))
        return "{topic} {timestamp} {data}".format(
            topic=self.topic,
            timestamp=self.timestamp,
            data=self.serialize_data(self.data)
        )

    @classmethod
    def deserialize_data(cls, data):
        return str(data)

    @classmethod
    def deserialize(cls, message):
        """Deserializes a message

        Args:
            message (str): serialized message

        Returns:
            Message: deserialized message
        """
        logger.info("Deserializing message...")
        try:
            topic, timestamp, data = message.split()
            data = cls.deserialize_data(data)
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))
        else:
            return cls(topic=topic, data=data)

    def __unicode__(self):
        return self.serialize()


class JsonMessage(Message):

    def serialize_data(self, data):
        return json.dumps(data)

    @classmethod
    def deserialize_data(cls, data):
        return json.loads(data)


class Base64Message(Message):

    def serialize_data(self, data):
        return base64.b64encode(data)

    @classmethod
    def deserialize_data(cls, data):
        return base64.b64decode(data)

    @staticmethod
    def get_topic_storage_dir(topic):
        topic_storage_dir = os.path.join(
            settings.FILE_MESSAGE_STORAGE_PATH, topic
        )

        if not os.path.exists(topic_storage_dir):
            os.makedirs(topic_storage_dir)

        return topic_storage_dir

    @classmethod
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

        if not isinstance(self.data, basestring):
            self.data = self.save_to_file(
                file_data=bytearray(base64.b64decode(self.data)),
                file_name=self.file_name,
            )

    def serialize_data(self, data):
        if isinstance(data, basestring):
            with open(data, 'rb') as source:
                serialized = base64.b64encode(bytearray(source.read()))
        else:
            serialized = base64.b64encode(bytearray(data))

        return serialized


class Socket(object):

    @staticmethod
    def get_socket(socket_type):
        context = zmq.Context()
        return context.socket(socket_type)


class Publisher(Socket):
    """ZMQ publisher"""

    def __init__(self, port):
        """Init publisher

        Args:
            port (int): Port to bind on
        """
        self.socket = self.get_socket(zmq.PUB)
        self.port = port
        self.socket.bind(port)

    def send(self, message):
        """Publish topic data

        Args:
            message (Message): Message to send
        """
        logger.info("Sending message {} to topic {}".format(
            message.id, message.topic
        ))
        self.socket.send(message.serialize())
        logger.info("Message {} sent".format(message.id))


class Subscriber(Socket):
    """ZMQ subscriber"""

    message_class = Message

    def __init__(self, publishers, topics, message_class=None):
        """Init subscriber

        Args:
            publishers ([str]): List of "<host>:<port>" publisher addresses
            topics ([str]): List of topics to subscribe to
        """
        self.socket = self.get_socket(zmq.SUB)

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


class LastMessageMixin(object):

    @staticmethod
    def get_socket(socket_type):
        context = zmq.Context()
        socket = context.socket(socket_type)
        socket.setsockopt(zmq.CONFLATE, 1)
        return socket


class LastMessagePublisher(LastMessageMixin, Publisher):
    """ZMQ publisher sending only the latest message"""
    pass


class LastMessageSubscriber(LastMessageMixin, Subscriber):
    """ZMQ subscriber reading only the latest message"""
    pass


class LastJsonMessageSubscriber(LastMessageSubscriber):
    message_class = JsonMessage


class LastBase64MessageSubscriber(LastMessageSubscriber):
    message_class = Base64Message


class LastFileMessageSubscriber(LastMessageSubscriber):
    message_class = FileMessage
