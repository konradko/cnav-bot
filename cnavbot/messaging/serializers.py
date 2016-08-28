import base64
import json


class DataSerializer(object):
    data_type = None

    def serialize(self, data):
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, data):
        raise NotImplementedError()


class Unicode(DataSerializer):
    data_type = 'text'

    def serialize(self, data):
        return unicode(data)

    @classmethod
    def deserialize(cls, data):
        return unicode(data)


class JSON(DataSerializer):
    data_type = 'json'

    def serialize(self, data):
        return json.dumps(data)

    @classmethod
    def deserialize(cls, data):
        return json.loads(data)


class FilePath(JSON):
    data_type = 'file_path'


class Base64(DataSerializer):
    data_type = 'base64'

    def serialize(self, data):
        return base64.b64encode(data)

    @classmethod
    def deserialize(cls, data):
        return base64.b64decode(data)
