import base64
import datetime
import json
from uuid import uuid4
import os
import time

import zmq

from cnavbot import settings, logger


class InvalidMessageError(Exception):
    pass


class DataSerializer(object):
    data_type = None

    def serialize(self, data):
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError()


class UnicodeSerializer(DataSerializer):
    data_type = 'text'

    def serialize(self, data):
        return unicode(data)

    @classmethod
    def deserialize(cls, data):
        return unicode(data)


class JsonSerializer(DataSerializer):
    data_type = 'json'

    def serialize(self, data):
        return json.dumps(data)

    @classmethod
    def deserialize(cls, data):
        return json.loads(data)


class Base64Serializer(DataSerializer):
    data_type = 'base64'

    def serialize(self, data):
        return base64.b64encode(data)

    @classmethod
    def deserialize(cls, data):
        return base64.b64decode(data)


class Message(object):
    serializer = None

    def __init__(self, *args, **kwargs):
        """
        Args:
            topic (str): topic of the message
            data (str): message data
        """
        self.serializer = kwargs.get('serializer', self.serializer)
        self.uuid = kwargs.get('uuid', str(uuid4()))
        self.timestamp = kwargs.get('timestamp', time.time())
        self.topic = kwargs.get('topic')
        self.data = kwargs.get('data')

    def validate(self):
        logger.info("Validating message '{}'".format(self.uuid))
        try:
            self.serialize()
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))

    def serialize(self):
        """Returns serialized message

        Returns:
            str: serialized message
        """
        logger.info("Serializing message '{}'".format(self.uuid))
        return "{topic} {id} {timestamp} {data_type} {data}".format(
            topic=self.topic,
            id=self.uuid,
            timestamp=self.timestamp,
            data_type=self.data_type,
            data=self.serializer.serialize(self.data)
        )

    def deserialize(self, raw_message):
        """Deserializes a message

        Args:
            raw_message (str): serialized message

        Returns:
            Message: new instance of the message
        """
        logger.info("Deserializing message...")
        try:
            topic, uuid, timestamp, data_type, data = raw_message.split()

            if data_type != self.data_type:
                raise InvalidMessageError(
                    u"Invalid data_type '{}', "
                    "expected: '{}'".format(
                        data_type, self.data_type
                    )
                )

            data = self.serializer.deserialize_data(data)
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))
        else:
            logger.info("Message '{}' deserialized".format(uuid))
            return self.__class__(
                topic=topic,
                uuid=uuid,
                timestamp=timestamp,
                data_type=data_type,
                data=data,
            )

    def __unicode__(self):
        return self.serialize()


class UnicodeMessage(Message):
    serializer = UnicodeSerializer


class Base64Message(Message):
    serializer = Base64Serializer
    file_path = None

    @staticmethod
    def get_topic_storage_dir(topic):
        topic_storage_dir = os.path.join(
            settings.FILE_MESSAGE_STORAGE_PATH, topic
        )

        if not os.path.exists(topic_storage_dir):
            os.makedirs(topic_storage_dir)

        return topic_storage_dir

    def get_file_name(self):
        return "{}-{}".format(
            datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            self.uuid,
        )

    def get_file_path(self, file_name=None):
        return os.path.join(
            self.get_topic_storage_dir(self.topic),
            file_name or self.get_file_name()
        )

    def save(self, file_name=None):
        file_path = self.get_file_path(file_name)

        logger.info("Saving message '{}' data to '{}'".format(
            self.uuid, file_path
        ))

        with open(file_path) as destination:
            destination.write(bytearray(self.data))

        logger.info("Message '{}' data saved".format(self.uuid))
        self.file_path = file_path

        return file_path


class JsonMessage(Message):
    serializer = JsonSerializer


class FilePathMessage(JsonMessage):

    @property
    def file_path(self):
        return self.data['file_path']


class MessageParser(object):

    message_for_data_type = {
        UnicodeMessage.serializer.data_type: UnicodeMessage,
        Base64Message.serializer.data_type: Base64Message,
        JsonMessage.serializer.data_type: JsonMessage,
        FilePathMessage.serializer.data_type: FilePathMessage,
    }

    @classmethod
    def parse(cls, raw_message):
        """Parses a raw message and returns a Message instance of correct type

        Args:
            raw_message (str): serialized message

        Returns:
            Message: deserialized message
        """
        logger.info("Deserializing message...")
        try:
            topic, uuid, timestamp, data_type, data = raw_message.split()
        except Exception as e:
            raise InvalidMessageError(u"Invalid message: {}".format(e))
        else:
            if data_type not in cls.serializers:
                raise InvalidMessageError(
                    u"Invalid message data_type '{}', "
                    "allowed data types: '{}'".format(
                        data_type, ", ".join(cls.serializers.keys())
                    )
                )

            message = cls.message_for_data_type[data_type]
            data = message.serializer.deserialize(data)

            logger.info("Message '{}' deserialized".format(uuid))

            return message(
                topic=topic,
                uuid=uuid,
                timestamp=timestamp,
                data_type=data_type,
                data=data,
            )


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
        logger.info("Sending message '{}'' to topic {}".format(
            message.uuid, message.topic
        ))
        self.socket.send(message.serialize())
        logger.info("Message '{}'' sent".format(message.uuid))


class Subscriber(Socket):
    """ZMQ subscriber"""

    def __init__(self, publishers, topics):
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
        return MessageParser.parse(raw_message=message)


class MessageForwarder(Subscriber):

    def __init__(self, publisher, *args, **kwargs):
        super(MessageForwarder, self).__init__(*args, **kwargs)
        self.publisher = publisher

    def read(self, *args, **kwargs):
        """Returns a single message from the publishers

        Returns:
            Message: deserialized message
        """
        message = super(MessageForwarder, self).read(*args, **kwargs)
        self.forward(message)
        return message

    def forward(self, message):
        """Forward a message

        Args:
            message (Message): Message to forward
        """
        logger.info("Forwarding message '{}'".format(message.uuid))
        self.publisher.send(message)


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
