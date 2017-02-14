# -*- coding: utf-8 -*-
#-*-coding:utf-8-*-


import base64
from scrapy import log
from jobspider.scrapy_db.db_pool import TQDbPool
from jobspider.scrapy_redis.redis_pool import TQRedis
from jobspider.contrib.downloadproxy.random_proxy import RandomProxy
from jobspider.utils.tools import zeroPointUnixTime
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware


class RotateHttpProxyMiddlewareForBGZ():
    
    def __init__(self):
        self.r0 = TQRedis.GetRedis('redis_cache_2')
        
    def process_request(self, request, spider):
        #ignore if not set use_proxy
        if 'use_proxy' not in request.meta:
            return
        if not request.meta['use_proxy']:
            return
        hp = None
        acquireCount = 0
        while not hp:
            #100次仍未获取到合适的代理
            if acquireCount >= 100:
                return request
            hp = self._http_proxy()
            acquireCount += 1
            if hp:
                request.meta['proxy'] = hp['proxy']
                request.meta['download_timeout'] = 20
                #如果需要用户名认证，则需要加入认证信息
                if hp['auth'] <> '':
                    request.headers['Proxy-Authorization'] = 'Basic ' + hp['auth']
                    
    #处理请求异常
    def process_exception(self, request, exception, spider):
        log.msg('Error downloading %s' % request, level = log.ERROR)
        log.msg('cause by %s' % exception, level = log.ERROR)
        log.msg('proxy: %s' % request.meta['proxy'], level = log.ERROR)
        return request
            
    def _http_proxy(self):
        ret = RandomProxy()
        if ret:
            server = ret['server']
            port   = ret['port']
            username = ret['username']
            password = ret['password']
            #从redis检测该代理今日是否有使用
            if self._proxy_redis_available(server, port):
                auth = ''
                proxy = 'http://%(ProxyServer)s:%(ProxyPort)d' % {'ProxyServer': server, 'ProxyPort': port}
                if username <> '':
                    auth = '%(ProxyUser)s:%(ProxyPassword)s' % {'ProxyUser': username, 'ProxyPassword': password}
                    #base64编码
                    auth = base64.encodestring(auth)
                    auth = auth.rstrip()
                return {'proxy': proxy, 'auth': auth}
    
    #验证代理的可用性,依据redis上存储的代理信息过滤
    #redis会设置过期时间(每日零点过期)
    def _proxy_redis_available(self, server, port):
        #
        key = 'iproxy.%s.%d' % (server, port)
        reuse = self.r0.get(key)
        #代理重用次数超过4次则丢弃
        if reuse and int(reuse) >= 4:
            self.r0.delete(key)
            return False
        #增加代理重用次数
        else:
            if not reuse:
                #获得明日零点
                tomorrow = zeroPointUnixTime(delta = 1)
                self.r0.set(key, 1)
                self.r0.expireat(key, tomorrow)
            else:
                self.r0.incr(key)
            return True
        
    #单元测试
    def unit_test(self):
        hp = None
        while not hp:
            hp = self._http_proxy()
            if hp:
                print 'proxy:', hp['proxy']
                print 'auth:', hp['auth']
                
#单元测试入口
if __name__ == '__main__':
    import sys
    sys.path.append('../../../')
    httpProxy = RotateHttpProxyMiddlewareForBGZ()
    while True:
        httpProxy.unit_test()