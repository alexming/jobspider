# -*- encoding=utf-8 -*-
#!/usr/bin/env python


import json
from time import mktime, localtime, strftime
import datetime
from scrapy import Spider, log, Request, FormRequest
from scrapy.selector import Selector
from jobspider.items import *
from jobspider.scrapy_requests.start_requests import *
from jobspider.utils.tools import *


class BaiCJobSpider(Spider):

    name = 'baic'

    def __init__(self, reqHeaders, baseUrl, jobListUrl, *args, **kwargs):
        super(BaiCJobSpider, self).__init__(*args, **kwargs)
        self.siteID = 9
        self.storeCollection = 'mr138Position'
        self.companyPrefix = 'baic_'
        #
        self.reqHeaders = reqHeaders
        self.baseUrl = baseUrl
        self.jobListUrl = jobListUrl

    @classmethod
    def from_settings(cls, settings):
        reqHeaders = settings.get('BAIC_REQUEST_HEADERS', '')
        baseUrl = settings.get('BAIC_BASEURL', '')
        jobListUrl = settings.get('BAIC_JOBLISTURL', '')
        return cls(reqHeaders, baseUrl, jobListUrl)

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
        ids = []
        rows = get_requests_mongo_by_position(self.storeCollection, self.siteID)
        if rows:
            for row in rows:
                ids.append(row['_id'])
                #时间戳
                publishTime = 0
                if row.has_key('PublishTime'):
                    publishTime = row['PublishTime']
                #linkURL = self.jobListUrl.replace('<?Position?>', str(row['Position'])).replace('<?Page?>', '1')
                linkURL = '/searchjob.ashx?workcity=0&jobtype=42031&job_publish_date=30&ent_industry=0&sex=0&learn=0&money=0&expr=0&jobkind=0&lx=2&medals=&keyword=%20%20&page=1'
                yield Request(url = self.create_url(linkURL),
                    meta = {'use_proxy': False, '_id': row['_id'], 'Position': row['Position'], 'Name': row['Name'], 'PageIndex': 1, 'PublishTime': publishTime},
                    headers = self.reqHeaders,
                    method='GET',
                    dont_filter=True,
                    callback=self.parse_joblist)
            #批次更新LastTime
            if len(ids) > 0:
                update_start_requests(self.storeCollection, ids)

    #职位列表解析
    def parse_joblist(self, response):
        data = '{}'
        try:
            data = response.body.decode('GBK')
        except:
            log.msg(u'职位列表请求失败:url=%s,body=%s' % (response.url, response.body))
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'职位=%s的列表请求结果解析异常,非json数据.url=%s' % (response.meta['Name'], response.url), level = log.INFO)
            return
        #列表解析
        if js['JobInfoList']:
            first_update = False
            if response.meta.has_key('FirstUpdate'):
                first_update = response.meta['FirstUpdate']
            firstPublishTime = 0
            _id = response.meta['_id']
            if response.meta.has_key('FirstPublishTime'):
                firstPublishTime = response.meta['FirstPublishTime']
            PublishTime = response.meta['PublishTime']
            Position = response.meta['Position']
            JobName = response.meta['Name']
            pageIndex = response.meta['PageIndex']
            totalCount = js['Count']
            log.msg(u'Position=%s,pageIndex=%d,pageSize=%d,totalCount=%d' % (JobName, pageIndex, len(js['JobInfoList']), totalCount), level=log.INFO)
            for AJob in js['JobInfoList']:
                LinkID = AJob['JobSn']
                CompanyID = AJob['EntSn']
                postDateTime, postUnixTime = FmtAnnounceDateToDateTime(AJob['JobPublishDate'], '-')
                #
                if firstPublishTime == 0:
                    firstPublishTime = postUnixTime
                if postUnixTime <= PublishTime:
                    return
                elif (not first_update) and (not response.meta.has_key('FirstUpdate') or not response.meta['FirstUpdate']):
                    first_update = True
                    update_publishtime(self.storeCollection, _id, firstPublishTime, 'PublishTime')
                    str_t0 = strftime('%Y-%m-%d %H:%M:%S', localtime(PublishTime))
                    str_t1 = strftime('%Y-%m-%d %H:%M:%S', localtime(firstPublishTime))
                    log.msg(u'0.Position= %s 换词，发布日期:%s->%s' % (JobName, str_t0, str_t1), level = log.INFO)
                if exist_linkid(self.siteID, LinkID, postUnixTime):
                    continue
                #
                webJob = WebJob()
                webJob['SiteID'] = self.siteID
                webJob['PublishTime'] = postDateTime
                webJob['RefreshTime'] = postDateTime
                webJob['JobName'] = JobName
                #依据编码获取线下职位编码
                webJob['JobCode'] = FmtJobPositionWithPrefix('remote_252_1', self.companyPrefix, Position)
                webJob['Salary'] = AJob['JobMoney']
                webJob['SSWelfare'] = AJob['Medals']
                webJob['SBWelfare'] = ''
                webJob['OtherWelfare'] = ''
                webJob['InsertTime'] = datetime.today()
                webJob['Email'] = ''
                webJob['LinkID'] = LinkID
                webJob['Tag'] = ''
                #城市区域分割处理
                cityAreaName = AJob['JobWorkplace']
                cityAreaCodeName = FmtCityAreaCodeWithPrefix('remote_252_1', self.companyPrefix, cityAreaName)
                #
                if cityAreaCodeName == '':
                    log.msg(message = u'没有找到城市[%s]对应的代码' % cityAreaName, _level = log.INFO)
                    continue
                cityCode = cityAreaCodeName.split('#')[0]
                cityName = cityAreaCodeName.split('#')[1]
                areaName = cityAreaCodeName.split('#')[2]
                webJob['ProvinceName'] = ''
                webJob['CityName'] = cityName
                webJob['WorkArea'] = cityName
                #市级
                if len(cityCode) == 4:
                    webJob['AreaCode'] = cityCode
                    webJob['WorkArea1'] = ''
                    webJob['BusinessCode'] = cityCode
                #区级
                elif len(cityCode) == 6:
                    webJob['AreaCode'] = cityCode[0: 4]
                    webJob['WorkArea1'] = areaName
                    webJob['BusinessCode'] = cityCode
                #丢弃没有城市的职位数据
                else:
                    continue
                webJob['WorkArea2'] = ''
                webJob['CompanyLink'] = self.companyPrefix + CompanyID
                webJob['Exercise'] = AJob['ResExprYears']
                webJob['Eduacation'] = AJob['JobLearnLimited']
                webJob['Sex'] = AJob['Sex']
                webJob['Age'] = AJob['Age']
                webJob['JobType'] = 1
                webJob['SyncStatus'] = 0
                webJob['InsertTime'] = datetime.today()
                webJob['SrcUrl'] = self.create_url('/JobDetail.aspx?sn=%s' % LinkID)
                #企业详情
                yield Request(url = self.create_url('/EntDetail.aspx?entsn=%s&sn=%s&loginid=&loginpwd=' % (CompanyID, LinkID)),
                    callback = self.parse_cmp_detail,
                    meta = {'use_proxy': True, 'CompanyLink': webJob['CompanyLink'], 'CompanyID': CompanyID, 'LinkID': LinkID},
                    dont_filter = True
                    )
                #职位详情
                yield Request(url= webJob['SrcUrl'],
                    meta = {'use_proxy': True, 'WebJob': webJob},
                    callback = self.parse_job_detail,
                    dont_filter = True
                    )
            #下页处理
            #下一页,没有下一页该值＝0
            NextPage = js['NextPage']
            if NextPage > 0:
                linkURL = self.jobListUrl.replace('<?Position?>', str(Position)).replace('<?Page?>', str(NextPage))
                yield Request(url = self.create_url(linkURL),
                    meta = {'use_proxy': False, '_id': _id, 'Position': Position, 'Name': JobName, 'PageIndex': NextPage, 'PublishTime': PublishTime},
                    headers = self.reqHeaders,
                    method='GET',
                    dont_filter=True,
                    callback=self.parse_joblist)
        else:
            log.msg(u'职位=%s的列表没有请求到数据.url=%s' % (response.meta['Name'], response.url), level = log.INFO)

    #职位详情解析
    def parse_job_detail(self, response):
        data = ''
        try:
            data = response.body.decode('GBK')
            if data == '':
                log.msg(format= '%jobDetail.(request)s get fail.response is blank.', level = log.ERROR, request = response.url)
                return
        except:
            log.msg(u'返回职位详情结果为非GBK编码网页', level = log.INFO)
            return
        #
        hxs = Selector(None, data)
        #
        webJob = response.meta['WebJob']
        numberStr = clearSpecialAtHtml(first_item(hxs.xpath("//div[@class='entname']/text()").extract()))
        startPos = numberStr.rfind('（')
        endPos = numberStr.rfind('）')
        if startPos >= 0 and endPos >= 1:
            webJob['JobTitle'] = numberStr[0: startPos]
            webJob['Number'] = numberStr[startPos + 1: endPos]
        else:
            webJob['JobTitle'] = numberStr
            webJob['Number'] = u'不限'
        webJob['JobTitle'] = FmtSQLCharater(webJob['JobTitle'])
        #
        cp = hxs.xpath(u"//div[@class='contact'][contains(text(), '所属企业')]")
        webJob['Company'] = first_item(cp.xpath('string(.)').extract())
        webJob['Company'] = webJob['Company'].rstrip(' ')
        startPos = webJob['Company'].find('：')
        if startPos >= 0:
            webJob['Company'] = webJob['Company'][startPos + 1: ]
        #
        webJob['StartDate'] = first_item(hxs.xpath(u"//div[@class='contact'][contains(text(), '更新日期')]/text()").extract())
        startPos = webJob['StartDate'].find('：')
        if startPos >= 0:
            webJob['StartDate'] = webJob['StartDate'][startPos + 1: ]
        #
        webJob['EndDate'] = first_item(hxs.xpath(u"//div[@class='contact'][contains(text(), '有效日期')]/text()").extract())
        startPos = webJob['EndDate'].find('：')
        if startPos >= 0:
            webJob['EndDate'] = webJob['EndDate'][startPos + 1: ]
        #福利待遇
        webJob['SBWelfare'] = first_item(hxs.xpath(u"//div[@class='contact'][contains(text(), '福利待遇')]/text()").extract())
        startPos = webJob['SBWelfare'].find('：')
        if startPos >= 0:
            webJob['SBWelfare'] = webJob['SBWelfare'][startPos + 1: ]
        #提供食宿
        webJob['OtherWelfare'] = first_item(hxs.xpath(u"//div[@class='contact'][contains(text(), '住宿情况')]/text()").extract())
        startPos = webJob['OtherWelfare'].find('：')
        if startPos >= 0:
            webJob['OtherWelfare'] = webJob['OtherWelfare'][startPos + 1: ]
        if webJob['OtherWelfare'] == u'提供住房补贴':
            webJob['OtherWelfare'] == u'房补'
        elif webJob['OtherWelfare'] != u'提供住宿':
            webJob['OtherWelfare'] = ''
        #
        webJob['Relation'] = first_item(hxs.xpath(u"//div[@class='contact'][contains(text(), '联 系 人')]/text()").extract())
        startPos = webJob['Relation'].find('：')
        if startPos >= 0:
            webJob['Relation'] = webJob['Relation'][startPos + 1: ]
        #
        webJob['Mobile'] = clearSpecialAtHtml(first_item(hxs.xpath(u"//div[@class='contact'][contains(., '联系电话')]/a/text()").extract()))
        startPos = webJob['Mobile'].find('：')
        if startPos >= 0:
            webJob['Mobile'] = webJob['Mobile'][startPos + 1: ]
        #未提供联系信息
        if webJob['Mobile'] == '':
            log.msg(u'没有联系信息,%s' % webJob['SrcUrl'], level = log.INFO)
            return
        #
        webJob['JobDesc'] = first_item(hxs.xpath("//div[@class='entcontent']").extract())
        #去除首部
        webJob['JobDesc'] = webJob['JobDesc'].lstrip('''<div class="entcontent">''')
        #去除尾部
        webJob['JobDesc'] = webJob['JobDesc'].rstrip('''</div>''')
        #去除首尾部
        webJob['JobDesc'] = webJob['JobDesc'].lstrip('\r\n')
        webJob['JobDesc'] = webJob['JobDesc'].rstrip('\r\n')
        webJob['JobDesc'] = webJob['JobDesc'].lstrip(' ')
        webJob['JobDesc'] = webJob['JobDesc'].rstrip(' ')
        #特殊符号#63,html转移字符&nbsp;
        webJob['JobDesc'] = webJob['JobDesc'].replace(u' ', '')
        #
        webJob['JobAddress'] = first_item(hxs.xpath(u"//div[@class='contact'][contains(text(), '联系地址')]/text()").extract())
        startPos = webJob['JobAddress'].find('：')
        if startPos >= 0:
            webJob['JobAddress'] = webJob['JobAddress'][startPos + 1: ]
        webJob['JobAddress'] = FmtSQLCharater(webJob['JobAddress'])
        #
        webJob['Require'] = u'招%s|学历%s|经验%s|性别%s' % (webJob['Number'], webJob['Eduacation'], webJob['Exercise'], webJob['Sex'])
        #其他默认信息
        webJob['AnFmtID'] = 0
        webJob['KeyValue'] = ''
        webJob['OtherWelfare'] = ''
        webJob['GisLongitude'] = '0'
        webJob['GisLatitude'] = '0'
        webJob['SalaryType'] = 0
        webJob['Tag'] = ''
        webJob['ClickTimes'] = 0
        webJob['Telphone1'] = ''
        webJob['Telphone2'] = ''
        webJob['ValidDate'] = ''
        webJob['ParentName'] = ''
        webJob['EduacationValue'] = 0
        webJob['SalaryMin'] = 0.0
        webJob['SalaryMax'] = 0.0
        webJob['NumberValue'] = 0
        webJob['SexValue'] = 0
        webJob['OperStatus'] = 0
        webJob['LastModifyTime'] = datetime.today()
        webJob['PropertyTag'] = ''
        webJob['SalaryValue'] = 0
        webJob['ExerciseValue'] = 0
        webJob['Valid'] = 'T'
        webJob['JobWorkTime'] = ''
        webJob['JobComputerSkill'] = ''
        webJob['ForeignLanguage'] = ''
        webJob['JobFunction'] = ''
        webJob['JobRequest'] = ''
        yield webJob

    #企业详情解析
    def parse_cmp_detail(self, response):
        data = ''
        try:
            data = response.body.decode('GBK').encode('utf8')
            if data == '':
                log.msg(format= '%companyDetail.(request)s get fail.response is blank.', level = log.ERROR, request = response.url)
                return
        except:
            log.msg(u'返回企业详情结果为非GBK编码网页', level = log.INFO)
            return
        #
        hxs = Selector(None, data)
        cmp = Company()
        cmp['SiteID'] = self.siteID
        cmp['company_id'] = response.meta['CompanyLink']
        cmp['CompanyName'] = first_item(hxs.xpath("//div[@class='entname']/text()").extract())
        cmp['CompanyName'] = clearSpecialAtHtml(cmp['CompanyName'])
        cmp['ProvinceName'] = ''
        cmp['CityName'] = ''
        cmp['AreaCode'] = ''
        cmp['WorkArea1'] = ''
        cmp['AreaCode1'] = ''
        #
        cmp['Industry'] = first_item(hxs.xpath(u"//div[@class='contact'][contains(text(), '所属行业')]/text()").extract())
        startPos = cmp['Industry'].find('：')
        if startPos >= 0:
            cmp['Industry'] = cmp['Industry'][startPos + 1: ]
        #
        cmp['CompanyType'] = first_item(hxs.xpath(u"//div[@class='contact'][contains(text(), '单位性质')]/text()").extract())
        startPos = cmp['CompanyType'].find('：')
        if startPos >= 0:
            cmp['CompanyType'] = cmp['CompanyType'][startPos + 1: ]
        #
        cmp['CompanyScale'] = first_item(hxs.xpath(u"//div[@class='contact'][contains(text(), '员工人数')]/text()").extract())
        startPos = cmp['CompanyScale'].find('：')
        if startPos >= 0:
            cmp['CompanyScale'] = cmp['CompanyScale'][startPos + 1: ]
        #
        match = re.search(r'''<div class="entcontent">(.*)</div>''', data, re.I|re.M)
        if match:
            cmp['CompanyDesc'] = match.group(1)
        else:
            cmp['CompanyDesc'] = ''
        #去除首尾部
        cmp['CompanyDesc'] = cmp['CompanyDesc'].lstrip('\r\n')
        cmp['CompanyDesc'] = cmp['CompanyDesc'].rstrip('\r\n')
        cmp['CompanyDesc'] = cmp['CompanyDesc'].lstrip(' ')
        cmp['CompanyDesc'] = cmp['CompanyDesc'].rstrip(' ')
        #特殊符号#63,html转移字符&nbsp;
        cmp['CompanyDesc'] = cmp['CompanyDesc'].replace(u' ', '')
        #
        match = re.search(r'''<div class="contact">联&nbsp;系&nbsp;人：(.*)</div>''', data, re.I|re.M)
        if match:
            cmp['Relation'] = match.group(1)
        else:
            cmp['Relation'] = ''
        #
        match = re.search(r'''<div class="contact">电&nbsp;&nbsp;&nbsp;&nbsp;话：<a.*>(.*)</a></div>''', data, re.I|re.M)
        if match:
            cmp['Mobile'] = match.group(1)
        else:
            cmp['Mobile'] = ''
        #
        match = re.search(r'''<div class="contact">公司地址：(.*)\r''', data, re.I|re.M)
        if match:
            cmp['CompanyAddress'] = match.group(1)
        else:
            cmp['CompanyAddress'] = ''
        #
        cmp['CompanyUrl'] = response.url
        cmp['Email'] = ''
        cmp['CompanyLogoUrl'] = ''
        cmp['PraiseRate'] = '0'
        cmp['GisLongitude'] = '0'
        cmp['GisLatitude'] = '0'
        cmp['UserId'] = ''
        cmp['UserName'] = ''
        #获取企业gps数据
        gpsLink = self.create_url('/BaiduMapShow.aspx?entsn=%s&sn=%s&loginid=&loginpwd=' % (response.meta['CompanyID'], response.meta['LinkID']))
        yield Request(url = gpsLink,
            meta = {'Company': cmp},
            callback = self.parse_cmp_gps,
            dont_filter = True
            )

    #企业gps解析
    def parse_cmp_gps(self, response):
        data = ''
        cmp = response.meta['Company']
        try:
            data = response.body.decode('GBK')
            if data == '':
                yield cmp
                log.msg(format= '%companyGps.(request)s get fail.response is blank.', level = log.ERROR, request = response.url)
                return
        except:
            yield cmp
            log.msg(u'返回企业gps结果为非GBK编码网页', level = log.INFO)
            return
        try:
            #
            match = re.search(r'''lng: (.*),\r''', data, re.I|re.M)
            if match:
                cmp['GisLongitude'] = match.group(1)
            #
            match = re.search(r'''lat: (.*),\r''', data, re.I|re.M)
            if match:
                cmp['GisLatitude'] = match.group(1)
            yield cmp
        except:
            yield cmp

