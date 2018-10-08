"""
Location object containing information about
where the model is stored
"""
from src.exceptions import InvalidDataError
import urllib
import os

class BaseLocation():

    def __init__(self, full_location):
        self.full_location = full_location
        try:
            self.parsed = urllib.parse.urlparse(self.full_location)
        except:
            raise InvalidDataError("Full location passed in should be a URL schema")
        if self.parsed:
            self.host = self.parsed.netloc

    def get_full_location(self):
        return self.full_location

    def get_host(self):
        return self.host


class MinioLocation(BaseLocation):

    def __init__(self, full_location):
        super(MinioLocation, self).__init__(full_location)
        self.__qualify_full_location()

    def __qualify_full_location(self):
        if self.parsed:
            self.path = self.parsed.path
            self.bucket = os.path.dirname(os.path.dirname('/models/gutenberg_test/'))[1:]
            self.object_name = os.path.basename(self.parsed.path)

    def get_bucket(self):
        return self.bucket

    def get_object_name(self):
        return self.object_name

