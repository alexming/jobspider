# -*- encoding=utf-8 -*-
from pymongo import MongoClient


MONGODB_CONFIG = {
#企业mongo数据
    'remote_252': {'host': '192.168.1.251', 'port': 27017, 'db': 'jobwebspider'},
#职位mongo数据
    'remote_238': {'host': '192.168.1.250', 'port': 27017, 'db': 'jobwebspider'},
#待同步职位全量mongo数据
    'remote_252_jobsync':{'host': '192.168.1.251', 'port': 27017, 'db': 'jobwebspider'},
#待清洗职位全量mongo数据
    'remote_252_webjob':{'host': '192.168.1.251', 'port': 27017, 'db': 'jobwebspider'},
#本地mongo
    'localhost':{'host': '127.0.0.1', 'port': 27017, 'db': 'jobwebspider'}
    }


class TQMongo:
#私有类变量
    __MongoDict = {}

#私有方法
    @classmethod
    def __getpool(self, mongoname):
        global MONGODB_CONFIG
        if self.__MongoDict.has_key(mongoname):
            return self.__MongoDict[mongoname]
        else:
            mongoc = MongoClient(host = MONGODB_CONFIG[mongoname]['host'], port = MONGODB_CONFIG[mongoname]['port'])
            dbname = MONGODB_CONFIG[mongoname]['db']
            db = mongoc[dbname]
            self.__MongoDict[mongoname] = db
            return db

    @classmethod
    def getDb(self, mongoname):
        db = self.__getpool(mongoname)
        return db

    @classmethod
    def closeDb(self, mongoname):
        global MONGODB_CONFIG
        if self.__MongoDict.has_key(mongoname):
            db = self.__MongoDict[mongoname]
            db.connection.close()


