from abc import ABC, abstractmethod

from couchbase.bucket import Bucket, NotFoundError
from couchbase.views.iterator import View
from couchbase.n1ql import N1QLQuery

from src.exceptions import InvalidType
import time


class AbstractDatabase(ABC):
    def __init__(self, host, port, user=None, password=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = self.__create__()

    @abstractmethod
    def __create__(self):
        pass


class ModelInfoDatabase(AbstractDatabase):

    @abstractmethod
    def find_model_info(self, key):
        pass


    @abstractmethod
    def find_all_model_info(self, limit=10):
        pass


    @abstractmethod
    def store_model_info(self, key, model_info):
        pass


class FeedbackDatabase(AbstractDatabase):

    @abstractmethod
    def store_feedback(self, key, feedback_info):
        pass

    @abstractmethod
    def get_feedback(self, key, limit):
        pass


class CouchFeedback(FeedbackDatabase) :
    """
    TODO: add a "start" point as well as a limit
        1. create some random unique id (timestamp) for each doc
        2. add model id for each doc
        3. create expiry for each doc
        4. run a query to find all docs for that model id (in N1QL)
        """
    def __create__(self):
        conn_str = self.CONNSTR.format(self.host, self.port)
        return Bucket(conn_str, username=self.user, password=self.password)

    CONNSTR = 'couchbase://localhost:8091/feedback'
    ALL_QUERY_STRING = 'SELECT * FROM feedback'
    MODEL_QUERY_STRING = 'WHERE feedback.model_id == {0}'
    PRIMARY_INDEX = 'prifb'
    TEN_DAYS_SECONDS = 10*24*60*60

    def store_feedback(self, feedback_info, key=None):
        # if key is none, create a timestamp
        if not key:
            key = str(int(time.time()))
        self.db.insert(key, feedback_info, ttl=self.TEN_DAYS_SECONDS)
        return key

    def get_feedback(self, key, limit):
        fb = []
        count = 0
        if key:
            q = N1QLQuery(self.ALL_QUERY_STRING + ' ' + self.MODEL_QUERY_STRING.format(key))
        else:
            q = N1QLQuery(self.ALL_QUERY_STRING)
        results = self.db.n1ql_query(q)
        for i in results:
            if count < limit:
                info = i['feedback']
                fb.append(info)
                count += 1
            else:
                break

        return fb


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
        # TODO: add a "start" point as well as a limit
        # so that you can paginate
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


def get_feedback_db(db_class, host='localhost', port='8091', user=None, password=None):
    # TODO: make sure DB connection is created and cached
    for clz in FeedbackDatabase.__subclasses__():
        if clz.__name__ == db_class:
            return clz(host, port, user, password)

    raise InvalidType('{0} is not a valid database type'.format(db_class))
