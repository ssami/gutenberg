from src.db import Database


class TestDB(Database):

    def store(self, key, info):
        self.db[key] = info

    def find(self, key):
        return self.db.get(key)

    def __create__(self):
        self.db = {}