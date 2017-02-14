# -*- encoding=utf-8 -*-


import json
from scrapy import Spider, log, Request, FormRequest
from scrapy.selector import Selector
from jobspider.kanzhun_items import *
from jobspider.scrapy_requests.start_requests import *
from jobspider.utils.tools import *


class BGZSpider(Spider):

    name = 'bgz'
    download_delay = 2
    randomize_download_delay = True

    def __init__(self, reqHeaders, baseUrl, category = None, *args, **kwargs):
        super(BGZSpider, self).__init__(*args, **kwargs)
        self.reqHeaders = reqHeaders
        self.baseUrl = baseUrl
        self.token = ''

    @classmethod
    def from_settings(cls, settings):
        reqHeaders = settings.get('KANZHUN_REQUEST_HEADERS', '')
        baseUrl = settings.get('KANZHUN_BASEURL', 'http://www.kanzhun.com')
        return cls(reqHeaders, baseUrl)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls.from_settings(settings)

    def create_url(self, parameters):
        if parameters is None:
            return ''
        if not parameters.startswith('/'):
            return self.baseUrl + '/' + parameters
        else:
            return self.baseUrl + parameters

    #入口函数
    def start_requests(self):
        #首先需要登录
        if self.token == '':
            formdata = {}
            formdata['_remember'] = 'on'
            formdata['account'] = 'firstwater@sohu.com'
            formdata['password'] = 'fw!@#123'
            formdata['redirect'] = self.baseUrl
            formdata['remember'] = 'true'
            yield FormRequest(url = self.create_url('login.json'),
                headers = dict({'X-Requested-With': 'XMLHttpRequest'}, **self.reqHeaders),
                formdata = formdata,
                dont_filter = True,
                meta = {'use_proxy': True},
                callback = self.parse_login)
        #已登陆，直接抓取
        else:
            yield self.start_city_requests(1)

    def start_city_requests(self, id):
        return Request(url = self.create_url('xsa%dp1.html' % id),
            meta = {'use_proxy': True, 'CityId': id},
            dont_filter = True,
            callback = self.parse_city_list)

    #登录解析
    def parse_login(self, response):
        js = json.loads(response.body)
        if js:
            if js['rescode'] == 1:
                self.token = js['token'] #zPuPbc0yDh2xsgs
                log.msg(u'登录成功.', level = log.INFO)
                yield self.start_city_requests(1)
            else:
                self.token = ''
                log.msg(u'登录失败,原因:%s' % js['resmsg'])

    #列表解析
    def parse_city_list(self, response):
        hxs = Selector(response)
        items = hxs.xpath("//div[@class='search-list-co-brief']/a[@class='fright mt15']")
        for item in items:
            link = first_item(item.xpath("@href").extract())
            if link != '':
                yield Request(url = self.create_url(link),
                    meta = {'use_proxy': True},
                    dont_filter = True,
                    callback = self.parse_salary)
        site_id = response.meta['CityId']
        if site_id < 472:
            site_id += 1
            yield self.start_city_requests(site_id)

    #薪资解析
    def parse_salary(self, response):
        hxs = Selector(response)
        items = hxs.xpath("//table[@id='salaryDescTable']/tr[@data-url]")
        for item in items:
            salary = Salary()
            #
            name = first_item(item.xpath('td/a/text()').extract())
            if name.endswith(')'):
                ix = name.rfind('(')
                if ix == -1:
                    salary['job_name'] = name
                    salary['job_count'] = 0
                else:
                    salary['job_name'] = name[0: ix]
                    salary['job_count'] = int(name[ix + 1: -2])
            else:
                salary['job_name'] = name
                salary['job_count'] = 0
            salary['average'] = first_item(item.xpath("td[@class='s-d-average']/text()").extract())
            salary['average'] = salary['average'].replace('￥', '').replace(',', '')
            salary['company_logo'] = first_item(hxs.xpath("//a[@ka='com-logo']/img/@src").extract())
            salary['src_url'] = self.create_url(first_item(item.xpath('td/a/@href').extract()))
            #
            company_url = first_item(hxs.xpath("//a[@ka='com-logo']/@href").extract())
            if company_url is not None:
                salary['company_url'] = self.create_url(company_url)
                start = company_url.find('gso')
                end = company_url.find('.html')
                salary['company_code'] = company_url[start: end]
            else:
                salary['company_url'] = ''
                salary['company_code'] = ''
            co_info = hxs.xpath("//div[@class='co_info']")
            salary['company_name'] = first_item(co_info.xpath("p[@id='companyName']/@data-companyname").extract())
            salary['praise_rate'] = first_item(co_info.xpath("div[@class='msgs']/strong/text()").extract())
            other = co_info.xpath("p[@class='params grey_99 mt5']//text()").extract()
            salary['industry'] = ''
            salary['city_name'] = ''
            salary['company_type'] = ''
            salary['company_scale'] = ''
            if other is not None:
                other_str = ''
                for ix in other:
                    other_str += ix
                other_array = other_str.split('|')
                if len(other_array) > 0:
                    salary['industry'] = other_array[0]
                if len(other_array) > 1:
                    salary['city_name'] = other_array[1]
                if len(other_array) > 2:
                    salary['company_scale'] = other_array[2]
                if len(other_array) > 3:
                    salary['company_type'] = other_array[3]
            #
            id = first_item(item.xpath('@id').extract())
            if id != '':
                id += '_C'
                ul = hxs.xpath("//table[@id='salaryDescTable']/tr[@id='%s']/td/div/ul" % id)
                if ul:
                    salary['high'] = first_item(ul.xpath("li[@class='s-d-low']/text()").extract())
                    salary['low'] = first_item(ul.xpath("li[@class='s-d-high']/text()").extract())
                    salary['mark'] = first_item(ul.xpath("li[@class='s-d-mark']/a/em/text()").extract())
                    salary['high'] = salary['high'].replace('￥', '').replace(',', '').lstrip(' ')
                    salary['low'] = salary['low'].replace('￥', '').replace(',', '').lstrip(' ')

            yield salary
        #下页处理
        link = first_item(hxs.xpath("//div[@class='page_wrap']/div/a[@class='p_next']/@href").extract())
        if link is not None:
            yield Request(url = self.create_url(link),
                meta = {'use_proxy': True},
                dont_filter = True,
                callback = self.parse_salary)

