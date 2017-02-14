# -*- encoding=utf8 -*-


import json
from scrapy import Spider, log


class BaseSpider(Spider):

    def __init__(self, settings, category = None, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls(settings, None, *args, **kwargs)

    def create_url(self, parameters):
        if parameters is None:
            return ''
        if not hasattr(self, 'base_url'):
            return ''
        if not parameters.startswith('/'):
            return self.base_url + '/' + parameters
        else:
            return self.base_url + parameters

    #将http请求返回结果json反序列化
    def fmt_json(self, data):
        if data == '' or data == '[]':
            return None
        js = json.loads('{}')
        try:
            js = json.loads(data)
            return js
        except:
            return None

    #异常http请求回调
    def requestErrorBack(self, error):
        log.msg(u'error.请求异常,原因:%s,内容:%s' % (error.value.message, error.value.response.url), level = log.ERROR)

