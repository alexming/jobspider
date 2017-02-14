# -*- encoding=utf-8 -*-
#!/usr/bin/env python


import sys
from scrapy import Request, log, signals
from jobspider.spiders.base_spider import BaseSpider
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from jobspider.utils.tools import InitLog


#兼职列表
jobs = (
    '学生兼职',
    '促销/导购',
    '传单派发',
    '钟点工',
    '服务员',
    '生活配送员',
    '护工',
    '催乳师',
    '问卷调查',
    '活动策划',
    '网络营销',
    '游戏代练',
    '网站建设',
    'SEO优化',
    '软件开发/编程',
    '兼职测试',
    '网络布线/维修',
    '美工/平面设计',
    'CAD制图/装修设计',
    '图片处理',
    '手绘/漫画',
    '视频剪辑/制作',
    '技工',
    '家教',
    '艺术老师',
    '健身教练',
    '汽车陪练',
    '汽车代驾',
    '导游',
    '写作',
    '会计',
    '翻译',
    '律师/法务',
    '摄影/摄像',
    '化妆师',
    '礼仪/模特',
    '司仪/驻唱/演出',
    '志愿者',
    '其他兼职',
)

jobs = (
    '学生兼职',
    '钟点工',
    '家教',
    '促销员',
    '传单派发',
    '实习生',
    '模特',
    '礼仪小姐',
    '摄影师',
    '问卷调查',
    '网站建设',
    '设计制作',
    '会计',
    '翻译',
    '其他兼职',
)


class JobKeySpider(BaseSpider):

    name = 'jobkey'
    flag = 0

    #入口函数
    def start_requests(self):
        if self.flag == 1:
            return
        self.flag = 1
        for JobName in jobs:
            '''
            linkURL = 'http://app.58.com/api/log/api/info/infotiplist/4/13941/?key=' + JobName
            yield Request(url = linkURL,
                method='GET',
                meta={'JobName': JobName},
                dont_filter=True,
                callback=self.parse_jobkeys
                )
            '''
            args = 'jsonArgs={"cityScriptIndex":"401","categoryId":"3","keyword":"%s"}' % JobName
            yield Request(url='http://mobds.ganji.com/datashare/',
                          method='POST',
                          meta={'JobName': JobName},
                          headers={
                              'customerId': '801',
                              'clientAgent': 'samsung/SM-N900#1080*1920#3.0#4.4.2',
                              'versionId': '6.5.0',
                              'model': 'Generic/AnyPhone',
                              'Accept-Encoding': 'gzip',
                              'contentformat': 'json2',
                              'userId': '80E861CDA4063326698DB8A9B45323D2',
                              'agency': 'qq',
                              'clientTest': 'false',
                              'interface': 'ajaxSuggestion',
                              'Content-Type': 'application/x-www-form-urlencoded',
                              'Host': 'mobds.ganji.com',
                              'Connection': 'Keep-Alive'
                          },
                          body=args,
                          callback=self.parse_jobkeys)

    def parse_jobkeys(self, response):
        data = response.body
        js = BaseSpider.fmt_json(self, data)
        if js:
            '''
            for item in js['result']:
                log.msg(response.meta['JobName'] + '#' + item[1] + '#' + item[0])
            '''
            for item in js:
                log.msg(response.meta['JobName'] + '#' + item['text'] + '#' + item['count'])

def run_main():
  log.start()
  InitLog()
  settings = get_project_settings()
  crawler = Crawler(settings)
  spider = JobKeySpider.from_crawler(crawler)
  crawler.signals.connect(reactor.stop, signal = signals.spider_closed)
  crawler.configure()
  crawler.crawl(spider)
  crawler.start(close_if_idle = True)
  reactor.run() # the script will block here until the spider_closed signal was sent

if __name__ == '__main__':
  reload(sys)
  sys.setdefaultencoding('utf-8')
  run_main()
