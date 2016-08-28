from multiprocessing import Process

from cnavbot.utils import logger


class Base(object):

    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.process = Process(target=self.run)

        logger.info("Starting {} service...".format(self.name))
        self.process.start()

    @staticmethod
    def get_subscriber():
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()
