from abc import ABC, abstractmethod
import redis
from src.exceptions import InvalidType
from flask import g
import src.constants


class Database(ABC):

    def __init__(self, host, port, user=None, password=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = self.__create__()

    def get_db(self):
        return self.db

    @abstractmethod
    def __create__(self):
        pass

    @abstractmethod
    def store(self, key, info):
        pass

    @abstractmethod
    def find(self, key):
        pass

    @abstractmethod
    def findall(self, key):
        pass


class RedisDB(Database):

    def __create__(self):
        return redis.StrictRedis(
            host=self.host,
            port=self.port,
            password=self.password,
            charset='utf-8',
            decode_responses=True
        )

    def store(self, key, info):
        """
        For some reason I decided to treat
        Redis like a document store.
        This will split the key into a set
        and connect the key with its
        'document', the info
        :param key:
        :param info:
        :return:
        """
        self.db.sadd(src.constants.MODEL_KEYSPACE, key)
        self.db.hmset(key, info)

    def findall(self, key):
        return self.db.smembers(key)

    def find(self, key):
        return self.db.hgetall(key)


class FeedbackDB(ABC):

    def __init__(self, host, port, user=None, password=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = self.__create__()

    @abstractmethod
    def store_feedback(self, model_key, feedback_info):
        pass

    @abstractmethod
    def get_feedback_for_model(self, model_key):
        pass

    @abstractmethod
    def __create__(self):
        pass


def get_db(db_class, host='localhost', port='6379', user=None, password=None):
    # if 'db' not in g:
    #     g.db = redis.Redis(
    #         host="localhost",
    #         port=6379,
    #         password=None
    #     )
    # return g.db
    # TODO: make sure DB connection is created and cached
    for clz in Database.__subclasses__():
        if clz.__name__ == db_class:
            return clz(host, port, user, password)

    raise InvalidType('{0} is not a valid database type'.format(db_class))


def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)