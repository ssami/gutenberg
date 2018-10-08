from abc import ABC, abstractmethod
from minio import Minio
from src.location import MinioLocation
from src.exceptions import LoaderException

import os


class BaseModelLoader(ABC):

    def __init__(self, location):
        self.location = location

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def unread(self):
        pass


class MinioLoader(BaseModelLoader):

    def __init__(self, location):
        BaseModelLoader.__init__(self, location)
        self.location = MinioLocation(location)

    def read(self, local_path=None):
        """
        :return:
        """
        # todo: put access/key, local path pref, inside model config

        local_path = os.path.join(local_path, self.location.get_object_name())
        try:
            client = Minio(self.location.get_host(), access_key='admin',
                           secret_key='password', secure=False)
            client.fget_object(bucket_name=self.location.get_bucket(),
                               object_name=self.location.get_object_name(),
                               file_path=local_path)
        except Exception as e:
            raise LoaderException(str(e))

        return local_path

    def unread(self):
        pass

