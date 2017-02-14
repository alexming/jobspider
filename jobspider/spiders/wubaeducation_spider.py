# -*- coding: utf-8 -*-

import json
import re
import HTMLParser
from scrapy.selector import Selector
from scrapy import Spider, log, Request
from jobspider.wuba_items import WubaEnterprice, WubaShop, WubaComment
from jobspider.utils.tools import first_item

PAGE_SIZE = 25

#分类
categorys = [
    ('jiajiao',     u'家教机构'),
    ('fudao',       u'中小学辅导'),
    #('zhiyepeix',   u'职业培训'),
    #('xueli',       u'学历教育'),
    ('techang',     u'艺术培训'),
    ('tiyu',        u'体育培训'),
    #('shejipeixun', u'设计培训'),
    #('jisuanji',    u'IT培训'),
    ('waiyu',       u'语言培训'),
    #('mba',         u'管理培训'),
    ('youjiao',     u'婴幼儿教育'),
    #('liuxue',      u'出国留学'),
    #('yimin',       u'移民'),
    #('yiduiyi',     u'中小学一对一')
]


class WubaEducationSpider(Spider):

    name = "wuba.education"

    html_parser = HTMLParser.HTMLParser()
    citys = []

    def __init__(self, headers, base_url, list_info, info, category = None, *args, **kwargs):
        super(WubaEducationSpider, self).__init__(*args, **kwargs)
        self.headers = headers
        self.base_url = base_url
        self.list_info = list_info
        self.info = info
        #
        self.cityIndex = 0
        #self.citys.append(('sz', '深圳'))

        fp = open('jobspider/filedata/wuba_city.dat')
        try:
            row = fp.readline()
            while row:
                row = row.strip('\n')
                row = row.strip('\r')
                city = row.split('#')[0]
                name = row.split('#')[1]
                self.citys.append((city, name))
                row = fp.readline()
        finally:
            fp.close()

    @classmethod
    def from_settings(cls, settings):
        headers = settings.get('WUBA_REQUEST_HEADERS1', '')
        base_url = settings.get('WUBA_BASEURL', '')
        list_info = settings.get('WUBA_LISTINFO', '')
        info = settings.get('WUBA_INFO', '')
        return cls(headers, base_url, list_info, info)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls.from_settings(settings)

    def create_url(self, parameters):
        if parameters is None:
            return ''
        if not parameters.startswith('/'):
            return self.base_url + '/' + parameters
        else:
            return self.base_url + parameters

    #入口函数
    def start_requests(self):
        if self.cityIndex >= len(self.citys):
            self.cityIndex = 0
            log.msg(u'所有分类已经抓取完成,抓取即将关闭.')
            return
        r = 9
        if self.cityIndex + r + 1 > len(self.citys):
            r = len(self.citys) - self.cityIndex - 1
            if r == 0:
                r = 1
        for x in xrange(0,r):
            city = self.citys[self.cityIndex + x]
            for category in categorys:
                link_url = self.list_info.replace('<?category?>', category[0]).replace('<?city?>', city[0]).replace('<?page?>', '1')
                yield Request(url=self.create_url(link_url),
                    headers=self.headers,
                    meta={'category': category[0], 'name': category[1], 'city': city[0], 'cityname': city[1], 'timeout': 1000},
                    dont_filter=True,
                    callback=self.parse_info_list)
        #
        self.cityIndex += r + 1

    #列表解析
    def parse_info_list(self, response):
        data = response.body
        data = self.html_parser.unescape(data)
        data = data.replace('\r\n', '')
        data = data.replace('\t', '')
        data = data.replace('},]', '}]')
        data = data.replace('</root>', '</root>\r\n')
        #正则替换掉其中的xml字符串，否则解析json异常
        data, _ = re.subn(r'<root>.+</root>', '', data)
        data = data.replace('\r\n', '')
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'城市[%s]-类别[%s]的机构列表请求结果解析异常,非json数据.url=%s' % (response.meta['cityname'], response.meta['name'], response.url), level = log.INFO)
            return
        if js['status'] == 0:
            #
            jsl = js['result']['getListInfo']
            #
            category = response.meta['category']
            name = response.meta['name']
            city = response.meta['city']
            cityname = response.meta['cityname']
            page = jsl['pageIndex']
            size = len(jsl['infolist'])
            #下一页
            if not jsl['lastPage']:
                page = jsl['pageIndex'] + 1
                link_url = self.list_info.replace('<?category?>', category).replace('<?city?>', city).replace('<?page?>', str(page))
                yield Request(url=self.create_url(link_url),
                    headers=self.headers,
                    meta={'category': category, 'name': name, 'city': city, 'cityname': cityname, 'timeout': 2000},
                    dont_filter=True,
                    callback=self.parse_info_list)
            else:
                log.msg(u'到此结束:%d' % jsl['pageIndex'])
            #
            log.msg(u'城市[%s]-类别[%s]的机构列表当前页[%d],数量[%d]' % (cityname, name, page, size))
            #
            for item in jsl['infolist']:
                infoID = item['infoID']
                enterpriceName = item['enterpriceName']
                link_url = self.info.replace('<?category?>', category).replace('<?infoID?>', str(infoID)).replace('<?city?>', city)
                yield Request(url=self.create_url(link_url),
                    headers=self.headers,
                    meta={'category': category, 'name': name, 'city': city, 'cityname': cityname, 'enterpriceName': enterpriceName, 'timeout': 2000},
                    dont_filter=True,
                    callback=self.parse_info)
        else:
            log.msg(u'城市[%s]-类别[%s]的机构列表请求结果异常,原因:%s' % (response.meta['cityname'], response.meta['name'], js['msg']))

    #详情解析
    def parse_info(self, response):
        data = response.body
        data = self.html_parser.unescape(data)
        data = data.replace('\r\n', '')
        data = data.replace('\t', '')
        data = data.replace(' ', '')
        data = data.replace('},]', '}]')
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data, encoding="utf-8")
        except Exception, e:
            log.msg(e.message)
            log.msg(u'城市[%s]-类别[%s]机构[%s]详情请求结果解析异常,非json数据.url=%s' % (response.meta['cityname'], response.meta['name'], response.meta['enterpriceName'], response.url), level = log.INFO)
            return
        if js['status'] == 0:
            js_info = js['result']['info']
            #
            wb = WubaEnterprice()
            wb['category'] = response.meta['category']
            wb['category_name'] = response.meta['name']
            wb['city'] = response.meta['city']
            wb['cityname'] = response.meta['cityname']
            for item in js_info:
                if len(item) == 0:
                    continue
                for child in item:
                    if child.has_key('title_area'):
                        wb['title'] = child['title_area']['title']   #番禺辅导班,单科最高可提升50分,进步率高达98%
                        wb['publish'] = child['title_area']['ext'][0]  #发布时间 15.02.06
                        wb['click_times'] = child['title_area']['ext'][1]  #已有478人浏览
                    #
                    if child.has_key('comment_detail_area'):
                        wb['book_num'] = child['comment_detail_area']['booknum'] #累计1人预约
                        wb['comment_num'] = child['comment_detail_area']['commentnum'] #0人评价
                    #
                    if child.has_key('company_area'):
                        wb['company_name'] = child['company_area']['name']
                        if child['company_area'].has_key('authtitle'):
                            wb['auth_title'] = child['company_area']['authtitle']
                        else:
                            wb['auth_title'] = ''
                        wb['company_address'] = child['company_area']['address']
                        wb['shop_id'] = child['company_area']['shopid']
                        if child['company_area'].has_key('action'):
                            wb['shop_url'] = child['company_area']['action']['content']['url']
                    #
                    if child.has_key('tel_area'):
                        wb['telnum'] = child['tel_area']['telnum']
                        wb['contact'] = child['tel_area']['contact']
                        wb['info_id'] = child['tel_area']['action']['infoid']
                        wb['src_url'] = child['tel_area']['action']['url']
                        wb['username'] = child['tel_area']['action']['username']
                    #
                    if child.has_key('typeItem_area'):
                        if child['typeItem_area']['title'] == u'辅导科目':
                            wb['course'] = child['typeItem_area']['content'] #辅导科目:数学,英语,语文,物理,化学,史地政生
                        #
                        if child['typeItem_area']['title'] == u'服务区域':
                            wb['area_name'] = child['typeItem_area']['content'] #服务区域:番禺
                        #
                        if child['typeItem_area']['title'] == u'辅导阶段':
                            wb['stage'] = child['typeItem_area']['content'] #辅导阶段:小学,初中,高中
                        #
                        if child['typeItem_area']['title'] == u'服务类型':
                            wb['stage'] = child['typeItem_area']['content'] #小学
                        #
                        if child['typeItem_area']['title'] == u'授课形式':
                            wb['form'] = child['typeItem_area']['content'] #一对一,小班,大班,托管班
                        #
                        if child['typeItem_area']['title'] == u'教师身份':
                            wb['teacher_grade'] = child['typeItem_area']['content'] #教师身份:专业教师
                    #
                    if child.has_key('addressItem_area'):
                        wb['address'] = child['addressItem_area']['content'] #地址
                        if child['addressItem_area'].has_key('action'):
                            wb['lat'] = child['addressItem_area']['action']['lat'] #lat
                            wb['lon'] = child['addressItem_area']['action']['lon'] #lon
                    #
                    if child.has_key('desc_area'):
                        wb['desc_area'] = child['desc_area']['text'] #详细信息
                    #
                    if child.has_key('image_area'):
                        images = ''
                        for image in child['image_area']['image_list']:
                            images += image + ';'
                        wb['images'] = images
            if wb['src_url'] != '':
                yield Request(url=wb['src_url'],
                    #headers=self.headers,
                    meta={'wb': wb, 'timeout': 2000},
                    dont_filter=True,
                    callback=self.parse_info_tel)
            if wb['shop_id'] != '':
                #教育机构信息
                link_url = 'http://shop.58.com/app/info/%s/about' % wb['shop_id']
                yield Request(
                    url=link_url,
                    meta={'shopid': wb['shop_id'], 'address': wb['company_address'], 'lat': wb['lat'], 'lon': wb['lon'], 'timeout': 2000},
                    dont_filter=True,
                    callback=self.parse_shop
                    )
                #机构评论信息
                link_url = 'http://shop.58.com/app/info/%s/comment' % wb['shop_id']
                yield Request(
                    url=link_url,
                    meta={'shopid': wb['shop_id']},
                    dont_filter=True,
                    callback=self.parse_comment
                    )
        else:
            log.msg(u'城市[%s]-类别[%s]机构[%s]详情请求结果异常,将重新抓取,原因:%s,url=%s' % (response.meta['cityname'], response.meta['name'], response.meta['enterpriceName'], js['msg'], response.url))
            #yield Request(url=response.url,
            #    headers=self.headers,
            #    meta=response.meta,
            #    dont_filter=True,
            #    callback=self.parse_info)

    #解析电话
    def parse_info_tel(self, response):
        data = response.body
        hxs = Selector(None, data)
        telnum = first_item(hxs.xpath("//ul[@class='contact_area']/li/span[@class='phone']/text()").extract())
        telnum = telnum.replace('\r\n', '')
        telnum = telnum.replace(' ', '')
        wb = response.meta['wb']
        wb['telnum'] = telnum
        yield wb

    #解析商户
    def parse_shop(self, response):
        data = response.body
        shop_id = response.meta['shopid']
        shop_name = self._research(data, r'<li><span>公司名称 :</span>(.+)</li>')
        shop_name = shop_name.replace('\t', '')
        #
        telphone = self._research(data, r'<li><span>商家电话 :</span>\s+(.+)\s+</li>\s+<li><span>注册时间', re.I|re.S)
        telphone = telphone.replace('\r', '')
        telphone = telphone.replace('\n', '')
        telphone = telphone.replace('\t', '')
        telphone = telphone.rstrip('<br/>')
        telphone = telphone.replace('<br/>', '|')
        #
        registe_time = self._research(data, r'<li><span>注册时间 :</span>(.+)</li>')
        open_time = self._research(data, r'<li><span>营业时间:</span>(.+)</li>\t')
        route = self._research(data, r'<li><span>交通路线:</span>(.+)</li>')
        description = self._research(data, r'<h2>公司简介</h2>\s+<p>(.+)</p>', re.I|re.S)
        description = description.replace('\r\n\t', '')
        description = description.lstrip(' ')
        description = description.rstrip(' ')
        address = response.meta['address']
        lat = response.meta['lat']
        lon = response.meta['lon']
        #
        s = WubaShop()
        s['shop_id'] = shop_id
        s['shop_name'] = shop_name
        s['telphone'] = telphone
        s['registe_time'] = registe_time
        s['open_time'] = open_time
        s['route'] = route
        s['description'] = description
        s['address'] = address
        s['lat'] = lat
        s['lon'] = lon
        #
        yield s

    #解析评论
    def parse_comment(self, response):
        data = response.body
        shop_id = response.meta['shopid']
        hxs = Selector(None, data)
        pj = hxs.xpath('//div[@class="pjbox"]/ul[@class="pj_ul"]')
        for item in pj:
            c = WubaComment()
            c['shop_id'] = shop_id
            c['user_name'] = first_item(item.xpath('li/span[@class="dp_t"]/text()').extract())
            c['c_time'] = first_item(item.xpath('li/label/i/text()').extract())
            c['content'] = first_item(item.xpath('li[2]/text()').extract())
            c['content'] = c['content'].lstrip(' ')
            c['content'] = c['content'].rstrip(' ')
            addto = first_item(item.xpath('li/p[@class="addto"]/text()').extract())
            c['content'] += addto
            yield c

    #内部re解析
    def _research(self, data, pattern, flags = re.I):
        match = re.search(pattern, data, flags)
        if match:
            return match.group(1)
        else:
            return ''
