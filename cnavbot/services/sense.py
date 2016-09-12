import zmq

from zmqservices import pubsub, clientserver, messages
import cnavconstants.topics
import cnavconstants.publishers
import cnavconstants.servers

from cnavbot import settings


class Client(object):

    def __init__(self, *args, **kwargs):
        if settings.CNAV_SENSE_ENABLED:
            self.setup_sense_services()

    @staticmethod
    def get_sense_service_address(port):
        return 'tcp://{}:{}'.format(settings.CNAV_SENSE_ADDRESS, port)

    def setup_sense_services(self):
        inertial_service = self.get_sense_service_address(
            port=cnavconstants.publishers.INERTIAL_SENSORS_PORT
        )
        self.compass_subscriber = pubsub.LastMessageSubscriber(
            publishers=(inertial_service, ),
            topics=(cnavconstants.topics.COMPASS, ),
        )
        self.orientation_subscriber = pubsub.LastMessageSubscriber(
            publishers=(inertial_service, ),
            topics=(cnavconstants.topics.ORIENTATION, ),
        )

        environmental_service = self.get_sense_service_address(
            port=cnavconstants.publishers.ENVIRONMENTAL_SENSORS_PORT
        )
        self.temperature_subscriber = pubsub.LastMessageSubscriber(
            publishers=(environmental_service, ),
            topics=(cnavconstants.topics.TEMPERATURE, ),
        )
        self.pressure_subscriber = pubsub.LastMessageSubscriber(
            publishers=(environmental_service, ),
            topics=(cnavconstants.topics.PRESSURE, ),
        )
        self.humidity_subscriber = pubsub.LastMessageSubscriber(
            publishers=(environmental_service, ),
            topics=(cnavconstants.topics.HUMIDITY, ),
        )

        self.joystick_subscriber = pubsub.Subscriber(
            publishers=(self.get_sense_service_address(
                port=cnavconstants.publishers.JOYSTICK_PORT
            ), ),
            topics=(cnavconstants.topics.JOYSTICK, ),
        )
        # Do not wait for joystick input - timeout after 1 ms
        self.set_joystick_timeout(timeout=1)

        self.led_matrix_client = clientserver.Client(
            servers=(self.get_sense_service_address(
                port=cnavconstants.servers.LED_MATRIX_PORT
            ), ),
        )

    def display_text(self, text):
        self.led_matrix_client.request(message=messages.JSON(
            data={
                'method': 'show_message',
                'params': {'text': text}
            }
        ))

    @property
    def compass(self):
        return self.compass_subscriber.receive().data

    @property
    def orientation(self):
        return self.orientation_subscriber.receive().data

    @property
    def yaw(self):
        return self.orientation['yaw']

    @property
    def temperature(self):
        return self.temperature_subscriber.receive().data

    @property
    def pressure(self):
        return self.pressure_subscriber.receive().data

    @property
    def humidity(self):
        return self.humidity_subscriber.receive().data

    def set_joystick_timeout(self, timeout):
        self.joystick_subscriber.socket.RCVTIMEO = timeout

    @property
    def joystick(self):
        try:
            return self.joystick_subscriber.receive().data
        except zmq.error.Again:
            # this error is raised on timeout - we're only interested in
            # already provided input, thus ignoring
            return None

    @property
    def joystick_direction(self):
        data = self.joystick
        return data['direction'] if data else None
