import base64
import json
import uuid
import os
import time

import zmq

from cnavbot import settings


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
        self.validate()

    def validate(self):
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


class FileMessage(Base64Message):

    def __init__(self, file_name, *args, **kwargs):
        self.file_name = file_name or str(uuid.uuid4())
        kwargs['data'] = self.save_file(
            topic=kwargs['topic'],
            file_data=bytearray(base64.b64decode(kwargs['data']))
        )
        super(FileMessage, self).__init__(*args, **kwargs)

    def serialize_data(self, data):
        with open(data, 'rb') as source:
            return base64.b64encode(bytearray(source.read()))

    @staticmethod
    def get_topic_storage_dir(topic):
        topic_storage_dir = os.path.join(
            settings.FILE_MESSAGE_STORAGE_PATH, topic
        )

        if not os.path.exists(topic_storage_dir):
            os.makedirs(topic_storage_dir)

        return topic_storage_dir

    def save_file(self, topic, file_data):
        file_path = os.path.join(
            self.get_topic_storage_dir(topic), self.file_name
        )

        with open(file_path) as destination:
            destination.write(file_data)

        return file_path


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
            self.socket.connect(publisher)

        for topic in topics:
            self.subscribe(topic)

        if message_class:
            self.message_class = message_class

    def subscribe(self, topic):
        """Subscribe to a topic

        Args:
            topic (str): Topic to subscribe to
        """
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    def read(self):
        """Returns a single message from the publishers

        Returns:
            Message: deserialized message
        """
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

