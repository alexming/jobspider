# -*- coding: utf-8 -*-


from datetime import datetime
from scrapy import Item, log
from jobspider.scrapy_db.db_pool import TQDbPool


class ItemDao(Item):

    DBKey = None
    StoreTable = None

    def __init__(self):
        super(ItemDao, self).__init__()
        for field in self.fields:
            self[field] = ''

    def object2sql(self):
        command = 'insert into %s(' % self.StoreTable
        for field in self.fields:
            command += '%s,' % field
        command = command[0: -1]
        command += ') values ('
        for field in self.fields:
            if type(self[field]) in [str, unicode]:
                command += "'%s'," % self[field]
            elif type(self[field]) == int:
                command += '%d,' % self[field]
            elif type(self[field]) == float:
                command += '%f,' % self[field]
            elif type(self[field]) == bool:
                command += '%d,' % 1 if self[field] else 0
            elif type(self[field]) == datetime:
                command += "'%s'," % self[field].strftime('%Y/%m/%d %H:%M:%S')
            else:
                command += "'%s'," % self[field]
        command = command[0: -1]
        command += ')'
        return command

    def default2store(self):
        result = False
        if not self.DBKey:
            log.msg(u'item=[%s]没有指定存储的DBKey.' % self.__class__.__name__, level=log.ERROR)
        elif not self.StoreTable:
            log.msg(u'%s 没有指定存储的StoreTable' % self.__class__.__name__, level=log.ERROR)
        else:
            command = self.object2sql()
            if command != '':
                ret = TQDbPool.execute(self.DBKey, command)
                if ret is None:
                    log.msg(u'sql指令执行失败,出现异常:dbname=%s,commamd=%s' % (self.DBKey, command), level=log.ERROR)
                elif ret == -2:
                    log.msg(u'数据库连接失败导致执行失败:dbname=%s,commamd=%s' % (self.DBKey, command), level=log.ERROR)
                else:
                    result = True
            else:
                log.msg(u'class=%s.save2db没有需要执行的指令.' % self.__class__.__name__, level=log.ERROR)
        #
        return result

