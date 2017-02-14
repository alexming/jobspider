# -*- coding: utf-8 -*-
#!/usr/bin/env python


from scrapy.utils.project import Settings


#增加http随机请求头
def addHttpRotateUserAgent(settings):
    #默认下载中间件
    defaultDownloaderMiddleware = settings.getdict('DOWNLOADER_MIDDLEWARES', default={})
    rotateHttpUserAgent = settings.getdict('ROTATE_HTTP_USERAGENT_MIDDLEWARE', {})
    defaultDownloaderMiddleware = dict(rotateHttpUserAgent, **defaultDownloaderMiddleware)
    settings.set('DOWNLOADER_MIDDLEWARES', defaultDownloaderMiddleware)
    #To make RotateUserAgentMiddleware enable.
    settings.set('USER_AGENT', '')
    
#增加htpp随机动态代理
def addHttpRotateProxy(settings, downloaderMiddleware):
    settings.set('DOWNLOADER_MIDDLEWARES', downloaderMiddleware)

#增加htpp随机动态代理
def addHttpRotateProxyForBGZ(settings):
    #默认下载中间件
    defaultDownloaderMiddleware = settings.getdict('DOWNLOADER_MIDDLEWARES', default={})
    rotateHttpProxy = settings.getdict('ROTATE_HTTP_PROXY_MIDDLEWARE_FOR_BGZ', {})
    defaultDownloaderMiddleware = dict(rotateHttpProxy, **defaultDownloaderMiddleware)
    settings.set('DOWNLOADER_MIDDLEWARES', defaultDownloaderMiddleware)

#指定pipline({mysqlpipeline: 90})
def setPipeLines(settings, pipeLines):
    settings.set('ITEM_PIPELINES', pipeLines)
    