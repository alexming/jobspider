# -*- encoding=utf-8 -*-


import os
import sys
import threading
from scrapy import log
from jobspider.utils.tools import getGuid


class DbFile(object):

    def __init__(self):
        self.dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
        self.dirname += "/commands"
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)
        self.locker = threading.Condition()

    def addCommand(self, dbname, command, multi = True):
        ret = False
        #以读写追加模式打开
        self.locker.acquire()
        try:
            try:
                curpath = self.dirname + '/' + dbname
                if not os.path.exists(curpath):
                    os.makedirs(curpath)
                if multi:
                    curfile = curpath + '/_init_'
                else:
                    curfile = curpath + '/' + getGuid() + '.sql'
                fp = open(curfile, "ab+")
                ic = False
                try:
                    fs = os.path.getsize(curfile)
                    #print '大小=', fs
                    #写入文件 utf-8编码
                    fp.write(command.encode('utf-8'))
                    fp.write(";")
                    fp.write(os.linesep)
                    #文件大于1M，即新建文件
                    if fs > 5 * 1024:
                        nf = curpath + '/' + getGuid() + '.sql'
                        fp.flush()
                        fp.close()
                        os.rename(curfile, nf)
                        ic = True
                    ret = True
                finally:
                    if ic == False:
                        fp.flush()
                        fp.close()
            except Exception, e:
                log.msg(format = u'add sql commamd error,cause:%s,cmd=%s' % (str(e), command))
        finally:
            self.locker.release()
            return ret
