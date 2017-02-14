# -*- encoding=utf-8 -*-


import json
import scrapy
from scrapy import Spider, log, Request
from scrapy.selector import Selector
from jobspider.utils.tools import first_text
from jobspider.scrapy_dao.item_dao_mysql import ItemDaoMysql


class Period(ItemDaoMysql):

    good_id    = scrapy.Field()
    good_code  = scrapy.Field()
    good_name  = scrapy.Field()
    cate_1     = scrapy.Field()
    cate_2     = scrapy.Field()
    cate_3     = scrapy.Field()
    period_id  = scrapy.Field()
    good_value = scrapy.Field()
    user_id    = scrapy.Field()
    user_name  = scrapy.Field()
    user_addr  = scrapy.Field()
    jx_time    = scrapy.Field()
    yg_time    = scrapy.Field()
    yg_times   = scrapy.Field()
    ygm        = scrapy.Field()

    DBKey = 'yyg'
    StoreTable = 'goods_period_info'


class Invoke(ItemDaoMysql):

    good_id       = scrapy.Field()
    good_code     = scrapy.Field()
    period_id     = scrapy.Field()
    invoke_time   = scrapy.Field()
    invoke_device = scrapy.Field()
    user_id       = scrapy.Field()
    user_name     = scrapy.Field()
    user_photo    = scrapy.Field()
    invoke_times  = scrapy.Field()
    invoke_ip     = scrapy.Field()
    invoke_addr   = scrapy.Field()

    DBKey = 'yyg'
    StoreTable = 'goods_involve'


class YYGPipeline(object):

    def process_item(self, item, spider):
        item.default2store()
        return item


class YYGSpider(Spider):

    name = 'yyg'
    download_delay = 0.1
    randomize_download_delay = True

    def __init__(self, settings, category = None, *args, **kwargs):
        super(YYGSpider, self).__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls(settings, None, *args, **kwargs)

    def start_requests(self):
        meta = {'sid': 1, 'eid': 100}
        yield Request(
            url = 'http://api.1yyg.com/JPData?action=getLotteryList&FIdx={sid}&EIdx={eid}&SortID=0&IsCount=1&fun='.format(**meta),
            headers = {'Host': 'api.1yyg.com', 'Referer': 'http://www.1yyg.com/lottery/m%d.html' % (meta['eid'] / 100)},
            meta = meta,
            dont_filter = True,
            callback = self.parse_good_page
        )

    def parse_good_page(self, rep):
        jv = json.loads(rep.body.lstrip('(').rstrip(')').replace("'", '"'))
        if jv['code'] == 0:
            rows = jv['listItems']
            for row in rows:
                yield Request(
                    url = 'http://www.1yyg.com/lottery/%d.html' % row['codeID'],
                    meta = {'FF': True},
                    dont_filter = True,
                    callback = self.parse_period
                )
            if len(rows) == 100:
                rep.meta['sid'] += 100
                rep.meta['eid'] += 100
                yield Request(
                    url = 'http://api.1yyg.com/JPData?action=getLotteryList&FIdx={sid}&EIdx={eid}&SortID=0&IsCount=1&fun='.format(**rep.meta),
                    headers = {'Host': 'api.1yyg.com', 'Referer': 'http://www.1yyg.com/lottery/m%d.html' % (rep.meta['sid'] / 100)},
                    meta = rep.meta,
                    dont_filter = True,
                    callback = self.parse_good_page
                )

    def parse_period_page(self, rep):
        jv = json.loads(rep.body.lstrip('(').rstrip(')'))
        if jv['code'] == 0:
            rows = jv['listItems']
            for row in rows:
                # 已经开奖
                if row['codeState'] == 3:
                    meta = {'FF': False, 'code': row['codeID'], 'gid': rep.meta['gid'], 'pid': row['codePeriod'],'sid': 1, 'eid': 10}
                    yield Request(
                        url = 'http://www.1yyg.com/lottery/{}.html'.format(meta['code']),
                        meta = meta,
                        dont_filter = True,
                        callback = self.parse_period
                    )
            if len(rows) == 100:
                rep.meta['sid'] += 100
                rep.meta['eid'] += 100
                yield Request(
                    url = 'http://api.1yyg.com/JPData?action=getGoodsPeriodPage&goodsID={gid}&FIdx={sid}&EIdx={eid}&IsCount=1&fun='.format(**rep.meta),
                    headers = {'Host': 'api.1yyg.com', 'Referer': 'http://www.1yyg.com/lottery/{}.html'.format(rep.meta['code'])},
                    meta = rep.meta,
                    dont_filter = True,
                    callback = self.parse_period_page
                )


    def parse_period(self, rep):
        hxs = Selector(None, rep.body)
        gid = first_text(hxs.xpath('//input[@id="hidGoodsID"]/@value'))
        # 首次请求
        if rep.meta['FF']:
            code = hxs.xpath('//input[@id="hidCodeID"]/@value')
            yield Request(
                url = 'http://api.1yyg.com/JPData?action=getGoodsPeriodPage&goodsID={}&FIdx=1&EIdx=100&IsCount=1&fun='.format(gid),
                headers = {'Host': 'api.1yyg.com', 'Referer': 'http://www.1yyg.com/lottery/{}.html'.format(code)},
                meta = {'gid': gid, 'code': code, 'sid': 1, 'eid': 100},
                dont_filter = True,
                callback = self.parse_period_page
            )
        else:
            period = Period()
            period['good_id'] = gid
            period['good_code'] = rep.meta['code']
            period['cate_1'] = first_text(hxs.xpath('//div[@class="Current_nav"]/a[3]/text()'))
            period['cate_2'] = first_text(hxs.xpath('//div[@class="Current_nav"]/a[4]/text()'))
            period['cate_3'] = first_text(hxs.xpath('//div[@class="Current_nav"]/a[5]/text()'))
            period['good_name'] = first_text(hxs.xpath('//div[@class="ng-result-img"]/div/a/@title'))
            period['good_value'] = first_text(hxs.xpath('//input[@id="hidCodeQuantity"]/@value'))
            period['user_id'] = first_text(hxs.xpath('//p[@class="r-name"]/span/a/@href'))
            # 取后10位
            period['user_id'] = period['user_id'][:-11:-1][::-1]
            period['user_name'] = first_text(hxs.xpath('//p[@class="r-name"]/span/a/@title'))
            period['user_addr'] = first_text(hxs.xpath('//p[@class="r-name"]').xpath('string(.)')).replace(' ','').replace('\r','').replace('\n','').replace('\t','')
            period['user_addr'] = period['user_addr'].replace(period['user_name'], '').replace('(','').replace(')','')
            period['jx_time'] = first_text(hxs.xpath('//div[@class="result-main"]/div[@class="result-con-info"]/p[3]/span/text()'))
            period['yg_time'] = first_text(hxs.xpath('//div[@class="result-main"]/div[@class="result-con-info"]/p[4]/span/text()'))
            period['yg_times'] = first_text(hxs.xpath('//span[@class="r-num"]/text()'))
            period['ygm'] = first_text(hxs.xpath('//input[@id="hidCodeRno"]/@value'))
            # (第145733云)
            pid = first_text(hxs.xpath('//span[@class="num"]/text()'))
            pid = pid.replace(u'(第', '').replace('云)', '')
            period['period_id'] = pid
            yield period
            meta = {'code': rep.meta['code'], 'gid': period['good_id'], 'pid': pid, 'sid': 1, 'eid': 10}
            yield Request(
                url = 'http://api.1yyg.com/JPData?action=GetUserBuyListByCodeEnd&codeID={code}&FIdx={sid}&EIdx={eid}&isCount=0&fun='.format(**meta),
                headers = {'Host': 'api.1yyg.com', 'Referer': 'http://www.1yyg.com/lottery/{code}.html'.format(**meta)},
                meta = meta,
                dont_filter = True,
                callback = self.parse_invoke
            )

    def parse_invoke(self, rep):
        jv = json.loads(rep.body.lstrip('(').rstrip(')'))
        if jv['Code'] == 0:
            gid = rep.meta['gid']
            pid = rep.meta['pid']
            code = rep.meta['code']
            rows = jv['Data']['Tables']['BuyList']['Rows']
            for r in rows:
                invoke = Invoke()
                invoke['good_id'] = gid
                invoke['good_code'] = code
                invoke['period_id'] = pid
                invoke['invoke_time'] = r['buyTime']
                invoke['invoke_device'] = r['buyDevice']
                invoke['user_id'] = r['userWeb']
                invoke['user_name'] = r['userName']
                invoke['user_photo'] = r['userPhoto']
                invoke['invoke_times'] = r['buyNum']
                invoke['invoke_ip'] = r['buyIP']
                invoke['invoke_addr'] = r['buyIPAddr']
                yield invoke
            # 下一页
            if len(rows) == 10:
                rep.meta['sid'] += 10
                rep.meta['eid'] += 10
                yield Request(
                    url = 'http://api.1yyg.com/JPData?action=GetUserBuyListByCodeEnd&codeID={code}&FIdx={sid}&EIdx={eid}&isCount=0&fun='.format(**rep.meta),
                    headers = {'Host': 'api.1yyg.com', 'Referer': 'http://www.1yyg.com/lottery/{code}.html'.format(**rep.meta)},
                    meta = rep.meta,
                    dont_filter = True,
                    callback = self.parse_invoke
                )
