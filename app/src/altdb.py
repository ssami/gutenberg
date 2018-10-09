from abc import ABC, abstractmethod

##
# Couchbase:
# username: admin
# password: password
# docker run -d --name db -p 8091-8096:8091-8096 -p 11210-11211:11210-11211 couchbase

# cbexport json -c couchbase://172.17.0.2 -u admin -p password -b feedback -o feedback.json -f lines
# cbimport json -c couchbase://172.17.0.2 -u admin -p password -b feedback -d file://feedback.json -f lines
##
from couchbase.bucket import Bucket, NotFoundError
from couchbase.views.iterator import View

from src.exceptions import InvalidType

class ModelInfoDatabase(ABC):

    def __init__(self, host, port, user=None, password=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = self.__create__()

    @abstractmethod
    def __create__(self):
        pass

    @abstractmethod
    def find_model_info(self, key):
        pass


    @abstractmethod
    def find_all_model_info(self, limit=10):
        pass


    @abstractmethod
    def store_model_info(self, key, model_info):
        pass


class FeedbackDatabase(ABC):

    @abstractmethod
    def store_feedback(self, key, feedback_info):
        pass

    @abstractmethod
    def get_feedback(self, key):
        pass


class CouchFeedback(FeedbackDatabase) :
    """
        Two options for feedback:
        1. create multiple feedback buckets, which needs us to do Couchbase API calls
        2. create a single bucket but have each key store giant documents
        For now, I decided to go with option 2) for simplicity.
        Ideally when we create a new object to store model_info we should also
        create a new bucket for feedback!
        """

    # CONNSTR = 'couchbase://localhost:8091/feedback'


    def store_feedback(self, key, feedback_info):
        pass

    def get_feedback(self, key):
        pass


class CouchModelInfo(ModelInfoDatabase) :

    CONNSTR = 'couchbase://{0}:{1}/model-info'
    DDOC = 'dev_metrics'
    VIEW = 'model_metrics' # todo: are views exported?

    def __create__(self):
        conn_str = self.CONNSTR.format(self.host, self.port)
        return Bucket(conn_str, username=self.user, password=self.password)

    def find_model_info(self, key):
        try:
            result = self.db.get(key)
            return result.value
        except NotFoundError:
            return None

    def store_model_info(self, key, model_info):
        self.db.insert(key, model_info)

    def find_all_model_info(self, limit=10):
        view = View(self.db, self.DDOC, self.VIEW)
        results = []
        count = 0
        for v in view:
            if count == limit:
                break
            model = dict()
            model[v.key] = v.value
            results.append(model)
            count += 1

        return results


def get_modelinfo_db(db_class, host='localhost', port='8091', user=None, password=None):
    # if 'db' not in g:
    #     g.db = redis.Redis(
    #         host="localhost",
    #         port=6379,
    #         password=None
    #     )
    # return g.db
    # TODO: make sure DB connection is created and cached
    for clz in ModelInfoDatabase.__subclasses__():
        if clz.__name__ == db_class:
            return clz(host, port, user, password)

    raise InvalidType('{0} is not a valid database type'.format(db_class))
