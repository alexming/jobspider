#!/usr/bin/env python
#-*-coding:utf-8-*-

import base64
import random
from scrapy import log
from jobspider.scrapy_db.db_pool import TQDbPool
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware

class RotateHttpProxyMiddleware():

    http_proxy_list = []

    def __init__(self, db_name):
        rows = TQDbPool.query(db_name, 'select ProxyServer,ProxyPort,ProxyUser,ProxyPassword from JWebJob_ProxyList where IsEnable=1')
        for row in rows:
            proxy = 'http://%(ProxyServer)s:%(ProxyPort)d' % {'ProxyServer': row['ProxyServer'], 'ProxyPort': row['ProxyPort']}
            auth = '%(ProxyUser)s:%(ProxyPassword)s' % {'ProxyUser': row['ProxyUser'], 'ProxyPassword': row['ProxyPassword']}
            #base64编码
            auth = base64.encodestring(auth)
            auth = auth.rstrip()
            self.http_proxy_list.append({'proxy': proxy, 'auth': auth})

    @classmethod
    def from_settings(cls, settings):
        db_name = settings.get('PROXY_DBNAME', 'remote_253')
        return cls(db_name)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls.from_settings(settings)

    def _http_proxy(self, spider):
        return random.choice(self.http_proxy_list)

    def process_request(self, request, spider):
        #ignore if not set use_proxy
        if 'use_proxy' not in request.meta:
            return
        if not request.meta['use_proxy']:
            return
        hp = self._http_proxy(spider)
        if hp:
            request.meta['proxy'] = hp['proxy']
            request.headers['Proxy-Authorization'] = 'Basic ' + hp['auth']

    #处理请求异常
    def process_exception(self, request, exception, spider):
        log.msg('Error downloading %s' % request, level = log.ERROR)
        log.msg('cause by %s' % exception, level = log.ERROR)
        if request.meta.has_key('proxy'):
            log.msg('proxy: %s' % request.meta['proxy'], level = log.ERROR)
        return request
