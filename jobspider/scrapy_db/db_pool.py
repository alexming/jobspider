# -*- encoding=utf-8 -*-


from DBUtils.PooledDB import PooledDB
from DBUtils.PersistentDB import PersistentDB
import pymssql
import MySQLdb
from MySQLdb.cursors import DictCursor
import datetime
import traceback
from pymssql import OperationalError, InternalError
from jobspider.utils.tools import logger


DB_CONFIG = {
    #mssql
    'remote_253':
    {
        'type': 'mssql', 'host': '192.168.1.253', 'port': 1433, 'user': 'sa',
        'passwd': 'qy7tt@br38w', 'db': 'JobDataSpider'
    },
    #mysql
    'v2_job_company_db':
    {
        'type': 'mysql', 'host': '192.168.133.198', 'port': 3306, 'user': 'dev_import',
        'passwd':'Iamis_2015_IMPORT_0202', 'db': 'v2_job_company_db'
    },
    #mysql proxy
    'proxy_server':
    {
        'type': 'mysql', 'host': '192.168.1.251', 'port': 3306, 'user': 'root',
        'passwd': 'root', 'db': 'jobdataspider'
    },
    #mysql
    'remote_233':
    {
        'type': 'mysql', 'host': '192.168.1.233', 'port': 3306, 'user': 'root',
        'passwd':'root', 'db': 'jobdataspider'
    },
    #GSX
    'GSX':
    {
        'type': 'mysql', 'host': '192.168.1.251', 'port': 3306, 'user': 'root',
        'passwd': 'root', 'db': 'jobdataspider'
    },
    #Foreign
    'Foreign':
    {
        'type': 'mssql', 'host': '192.168.1.253', 'port': 1433, 'user': 'sa',
        'passwd': 'qy7tt@br38w', 'db': 'JobDataForeign'
    },
    'yyg':
    {
        'type': 'mysql', 'host': '192.168.1.251', 'port': 3306, 'user': 'root',
        'passwd': 'root', 'db': 'yyg'
    },
    'BuDejie':
    {
        'type': 'mysql', 'host': '192.168.1.252', 'port': 3306, 'user': 'root',
        'passwd': 'root', 'db': 'budejie'
    },
}


class TQDbManager():
    def __init__(self, dbname):
        if DB_CONFIG.has_key(dbname):
            args = (0, 0, 0, 200, 0, 0, None)
            if DB_CONFIG[dbname]['type'] == 'mssql':
                conn_args = {
                    'host': DB_CONFIG[dbname]['host'],
                    'port': DB_CONFIG[dbname]['port'],
                    'user': DB_CONFIG[dbname]['user'],
                    'password': DB_CONFIG[dbname]['passwd'],
                    'database': DB_CONFIG[dbname]['db'],
                    'charset': 'utf8'
                }
                try:
                    #使用PooledDB的效率存在问题，执行效率远低于PersistentDB
                    #PersistentDB采用一个线程一个db连接，在线程不频繁创建销毁的情景下，效率更好
                    self._pool = PersistentDB(pymssql, maxusage = 100, **conn_args)
                    #self._pool = PooledDB(pymssql, *args, **conn_args)
                except Exception, e:
                    raise u"The parameters for DBUtils is:", conn_args
            elif DB_CONFIG[dbname]['type'] == 'mysql':
                conn_args = {
                    'host': DB_CONFIG[dbname]['host'],
                    'port': DB_CONFIG[dbname]['port'],
                    'user': DB_CONFIG[dbname]['user'],
                    'passwd': DB_CONFIG[dbname]['passwd'],
                    'db': DB_CONFIG[dbname]['db'],
                    'charset': 'utf8',
                    'cursorclass': DictCursor
                }
                try:
                    self._pool = PersistentDB(MySQLdb, maxusage = 100, **conn_args)
                    #self._pool = PooledDB(MySQLdb, *args, **conn_args)
                except Exception, e:
                    raise u"The parameters for DBUtils is:", conn_args
            else:
                raise u'未支持的数据库类型(%s)' % DB_CONFIG[dbname]['dbtype']
        else:
            raise u'未约定的数据库连接名称(%s)' % dbname

    def getConn(self):
        return self._pool.connection()

class TQDbPool:

    __DbManagerDict = {}

    @classmethod
    def getConn(self, dbname):
        if DB_CONFIG.has_key(dbname):
            _dbManager = None
            if self.__DbManagerDict.has_key(dbname):
                _dbManager = self.__DbManagerDict[dbname]
            else:
                _dbManager = TQDbManager(dbname)
                self.__DbManagerDict[dbname] = _dbManager
            return _dbManager.getConn()
        else:
            raise '未约定的数据库连接名称(%s)' % dbname

    @classmethod
    def callReConn(self, dbname):
        ret = False
        if DB_CONFIG.has_key(dbname):
            if self.__DbManagerDict.has_key(dbname):
                try:
                    print "%s: now try to reconnect Database(%s)!" % (datetime.datetime.now(), dbname)
                    #_dbManager ＝ self.__DbManagerDict[dbname]
                    _dbManager = TQDbManager(dbname)
                    self.__DbManagerDict[dbname] = _dbManager
                    print u"%s reconnect database(%s) success!" % (datetime.datetime.now(), dbname)
                    ret = True
                except Exception, e:
                    logger.error(u'callReConn error:' + dbname + ' cause:' + str(e))
                    traceback.print_exc()
                    print u"%s reconnect database(%s) failed!" % (datetime.datetime.now(), dbname)
                finally:
                    return ret
        else:
            logger.error(u'未约定的数据库连接名称(%s)' % dbname)
            return ret

    @classmethod
    def testConn(self, dbname):
        conn = None
        cur = None
        res = False
        msg = ""
        try:
            conn = self.getConn(dbname)
            cur = conn.cursor()
            cur.execute("select 1")
            res = cur.fetchall()
            res = True
        except Exception, e:
            logger.error(u'testConn error:' + str(e))
            traceback.print_exc()
            msg = e
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
            return res, msg

    @classmethod
    def query(self, dbname, command):
        conn = None
        cur = None
        res = None
        try:
            conn = self.getConn(dbname)
            if DB_CONFIG[dbname]['type'] == 'mssql':
                cur = conn.cursor(True)
            elif DB_CONFIG[dbname]['type'] == 'mysql':
                cur = conn.cursor(None)
            else:
                raise '非法的数据库类型', dbname
            cur.execute(command)
            res = cur.fetchall()
        except (OperationalError, InternalError):
            logger.error(u'query error:' + command)
            self.callReConn(dbname)
            traceback.print_exc()
        except Exception, e:
            print str(e)
            traceback.exc()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
            return res

    @classmethod
    def queryOne(self, dbname, command):
        conn = None
        cur = None
        res = None
        try:
            conn = self.getConn(dbname)
            if DB_CONFIG[dbname]['type'] == 'mssql':
                cur = conn.cursor(True)
            elif DB_CONFIG[dbname]['type'] == 'mysql':
                cur = conn.cursor(None)
            else:
                raise '非法的数据库类型', dbname
            cur.execute(command)
            res = cur.fetchone()
        except (OperationalError, InternalError):
            logger.error(u'query one error:' + command)
            self.callReConn(dbname)
            traceback.print_exc()
        except Exception, e:
            print e
            traceback.exc()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
            return res

    @classmethod
    def execute(self, dbname, command):
        conn = None
        cur = None
        res = None
        try:
            conn = self.getConn(dbname)
            cur = conn.cursor()
            cur.execute(command)
            res = cur._cursor.rowcount
            conn.commit()
        except Exception, e:
            logger.error(u'execute error:%s,cause:%s' % (command, str(e)))
            if conn:
                conn.rollback()
            traceback.print_exc()
        finally:
            ret = True
            if res == -1:
                #可能是数据库断开连接
                ret, msg = self.testConn(dbname)
            if not ret:
                self.callReConn(dbname)
                res = -2
            if cur:
                cur.close()
            if conn:
                conn.close()
            return res

    @classmethod
    def mutiExecute(self, dbname, commandList):
        conn = None
        cur = None
        res = []
        flag = True
        sql = ''
        try:
            conn = self.getConn(dbname)
            cur = conn.cursor()
            for sql in commandList:
                cur.execute(sql)
                num = cur._cursor.rowcount
                res.append(num)
            conn.commit()
        except Exception, e:
            logger.error(u'execute error:%s,cause:%s' % (sql, str(e)))
            if conn:
                conn.rollback()
            traceback.print_exc()
        finally:
            if -1 in res:
                ret, msg = self.testConn(dbname)
                if not ret:
                    self.callReConn(dbname)
                    flag = False
                    res = [-2,]
            if cur:
                cur.close()
            if conn:
                conn.close()
            return flag, res
