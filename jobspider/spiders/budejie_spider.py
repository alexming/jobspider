# -*- coding: utf-8 -*-

import json
from scrapy import Spider, log, Request
from jobspider.budejie_items import Topic, User, Comment, Theme
from jobspider.utils.tools import FmtSQLCharater


categorys = [
    (10, '图片'),
    (29, '段子'),
    (31, '声音'),
    (41, '视频')
]

PAGE_SIZE = 20
MAX_PAGE = 100

format_url = 'http://api.budejie.com/api/api_open.php?a=list&c=data&type={type}&page={page}&maxtime={maxtime}&from=ios&per=%d' % PAGE_SIZE


class BudejieSpider(Spider):

    name = "budejie"

    def __init__(self):
        self.IsInit = False

    @classmethod
    def from_settings(cls, settings):
        return cls()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls.from_settings(settings)

    def _createNextRequest(self, meta):
        return Request(
                url = format_url.format(**meta),
                meta = meta,
                dont_filter=True,
                callback = self.parse_info_list)

    #入口函数
    def start_requests(self):
        if self.IsInit: return
        self.IsInit = True
        for item in categorys:
            meta = {'type': item[0], 'name': item[1], 'page': 1, 'maxtime': 0}
            yield self._createNextRequest(meta)

    def parse_info_list(self, resp):
        meta = resp.meta
        log.msg(u'已下载<%s>第<%d>页,开始解析...' % (meta['name'], meta['page']), log.INFO)
        ret = json.loads(resp.body)
        list = ret['list']
        log.msg(u'<%s>第<%d>页数量<%d>' % (meta['name'], meta['page'], len(list)))
        for item in list:
            fieldNames = item.keys();
            #
            topic = Topic()
            topicFields = topic.fields.keys()
            user = User()
            userFields = user.fields.keys()
            theme = Theme()
            themeFields = theme.fields.keys()
            #
            for field in fieldNames:
                if field in topicFields:
                    if field not in ['top_cmt', 'themes']:
                        topic[field] = FmtSQLCharater(item[field])
                if field in userFields:
                    user[field] = FmtSQLCharater(item[field])
                if field in themeFields:
                    theme[field] = FmtSQLCharater(item[field])
            #
            yield user
            yield topic
            yield theme
            #
        # 下一页请求
        if len(list) > 0 and meta['page'] < MAX_PAGE:
            # 下次请求参数
            meta['page'] += 1
            meta['maxtime'] = ret['info']['maxtime']
            yield self._createNextRequest(meta)
