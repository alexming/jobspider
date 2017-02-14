#!/usr/bin/python
#-*-coding:utf-8-*-


from time import sleep
import threading
from scrapy import log, Request
from scrapy.core.scheduler import Scheduler
from scrapy.utils.reactor import CallLaterOnce


class RotateScheduler(Scheduler):

    def open(self, spider):
        super(RotateScheduler, self).open(spider)
        self.nextcall = CallLaterOnce(self.more_request)
        self.locker = threading.Condition()

    def next_request(self):
        self.locker.acquire()
        try:
            request = super(RotateScheduler, self).next_request()
            if not request:
                request = self.more_request()
                #while not request:
                #    request = self.more_request()
                #    sleep(5)
                #    request = self.next_request()
                #else:
                #    pass
                    #while not next_request():
                    #    self.nextcall.schedule(2000)
            return request
        finally:
            self.locker.release()

    def more_request(self):
        log.msg(format = u'请求队列为空,从起始地址获取更多请求任务.', level = log.INFO)
        hasmore = False
        requests = self.spider.start_requests()
        for request in requests:
            hasmore = True
            self.enqueue_request(request)
        return request
