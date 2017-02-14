# -*- encoding=utf-8 -*-
#!/usr/bin/env python


import json
from time import mktime, localtime, strftime
import datetime
from scrapy import Spider, log, Request
from jobspider.items import *
from jobspider.scrapy_requests.start_requests import *
from jobspider.utils.tools import *
from jobspider.utils.baix_header import BaixHeader


class BaiXJobSpider(Spider):

    name = 'baix'
    download_delay = 1
    randomize_download_delay = True

    def __init__(self, reqHeaders, baseUrl, jobListUrl, jobUrl, category = None, *args, **kwargs):
        super(BaiXJobSpider, self).__init__(*args, **kwargs)
        self.siteID = 10
        self.storeCollection = 'CityIndex'
        self.companyPrefix = 'baix_'
        #
        self.reqHeaders = reqHeaders
        self.baseUrl = baseUrl
        self.jobListUrl = jobListUrl
        self.jobUrl = jobUrl

    @classmethod
    def from_settings(cls, settings):
        reqHeaders = settings.get('BAIX_REQUEST_HEADERS', '')
        baseUrl = settings.get('BAIX_BASEURL', '')
        jobListUrl = settings.get('BAIX_JOBLISTURL', '')
        jobUrl = settings.get('BAIX_JOBURL', '')
        return cls(reqHeaders, baseUrl, jobListUrl, jobUrl)

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
        rows = get_requests_mongo(self.siteID, 0)
        if rows:
            for row in rows:
                ids.append(row['_id'])
                #时间戳
                PublishTime = 0
                if row.has_key('PublishTime'):
                    PublishTime = row['PublishTime']
                #
                linkURL = self.jobListUrl.replace('<?city?>', row['CityId']).replace('<?from?>', '0')
                linkURL = self.create_url(linkURL)
                #
                apiHash = BaixHeader().apiDynamicHash(linkURL)
                #
                yield Request(url = linkURL,
                    meta = {
                        'use_proxy': False, '_id': row['_id'], \
                        'CityId': row['CityId'], 'CityName': row['CityName'], \
                        'from': 0, 'PublishTime': PublishTime
                        },
                    headers = dict(apiHash, **self.reqHeaders),
                    method='GET',
                    dont_filter=True,
                    callback=self.parse_joblist,
                    errback=self.errBack)
            #批次更新LastTime
            if len(ids) > 0:
                update_start_requests(self.storeCollection, ids)

    def errBack(self, error):
        log.msg(u'error.请求异常,原因:%s,内容:%s' % (error.value.message, error.value.response.body), level = log.ERROR)

    #职位列表解析
    def parse_joblist(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s get fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'城市=%s的列表请求结果解析异常,非json数据.url=%s' % (response.meta['CityName'], response.url), level = log.INFO)
            return
        #列表解析
        if js['result']:
            first_update = False
            if response.meta.has_key('FirstUpdate'):
                first_update = response.meta['FirstUpdate']
            firstPublishTime = 0
            if response.meta.has_key('FirstPublishTime'):
                firstPublishTime = response.meta['FirstPublishTime']
            _id = response.meta['_id']
            PublishTime = response.meta['PublishTime']
            CityId = response.meta['CityId']
            CityName = response.meta['CityName']
            pageFrom = response.meta['from']
            log.msg(u'城市=%s,pageFrom=%d,pageSize=%d' % (CityName, pageFrom, len(js['result'])), level=log.INFO)
            for AJob in js['result']:
                #刷新时间戳判别
                #过滤推广职位
                highlights = ''
                for highlight in AJob['highlights']:
                    highlights += highlight['text'] + '#'
                if highlights.find(u'火急') == -1 and highlights.find(u'顶') == -1 and highlights.find(u'插播') == -1:
                    nowPublishTime = int(AJob['createdTime'])
                    if firstPublishTime == 0:
                        firstPublishTime = nowPublishTime
                    if nowPublishTime <= PublishTime:
                        #本次最大发布时间<=上次抓取时间，直接退出
                        return
                    elif (not first_update) and (not response.meta.has_key('FirstUpdate') or not response.meta['FirstUpdate']):
                        first_update = True
                        #全职
                        update_publishtime(self.storeCollection, _id, firstPublishTime, 'PublishTime')
                        str_t0 = strftime('%Y-%m-%d %H:%M:%S', localtime(PublishTime))
                        str_t1 = strftime('%Y-%m-%d %H:%M:%S', localtime(firstPublishTime))
                        log.msg(u'城市= %s 换词，发布日期:%s->%s' % (CityName, str_t0, str_t1), level = log.INFO)
                #
                LinkID = AJob['config']['adId']
                postUnixTime = int(AJob['createdTime'])
                if exist_linkid(self.siteID, LinkID, postUnixTime):
                    continue
                #职位详情
                linkURL = self.jobUrl.replace('<?adId?>', str(LinkID))
                linkURL = self.create_url(linkURL)
                #
                apiHash = BaixHeader().apiDynamicHash(linkURL)
                #
                yield Request(url = linkURL, callback=self.parse_job_detail, method='GET',
                             headers = dict(apiHash, **self.reqHeaders),
                             encoding='utf-8',
                             dont_filter=True,
                             errback=None)
            #下页处理
            if len(js['result']) >= 30:
                pageFrom += 30
                #
                linkURL = self.jobListUrl.replace('<?city?>', CityId).replace('<?from?>', str(pageFrom))
                linkURL = self.create_url(linkURL)
                #
                apiHash = BaixHeader().apiDynamicHash(linkURL)
                #
                yield Request(url = linkURL,
                    meta = {
                        'use_proxy': False, '_id': _id, \
                        'CityId': CityId, 'CityName': CityName, \
                        'from': pageFrom, 'PublishTime': PublishTime, \
                        'FirstPublishTime': firstPublishTime, 'FirstUpdate': first_update
                        },
                    headers = dict(apiHash, **self.reqHeaders),
                    method='GET',
                    dont_filter=True,
                    callback=self.parse_joblist)
        else:
            log.msg(u'城市=%s的列表没有请求到数据.url=%s' % (response.meta['CityName'], response.url), level = log.INFO)

    #职位详情解析
    def parse_job_detail(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s get fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'职位详情请求结果解析异常,非json数据.url=%s' % response.url, level = log.INFO)
            return
        #
        if js and js['result']:
            js = js['result'][0]
        #
        postUnixTime = int(js['createdTime'])
        postTime = datetime.fromtimestamp(postUnixTime)
        #
        try:
            webJob = WebJob()
            webJob['SiteID'] = self.siteID
            webJob['LinkID'] = js['id']
            webJob['PublishTime'] = postTime
            webJob['RefreshTime'] = postTime
            webJob['JobTitle'] = js['title']
            webJob['SrcUrl'] = js['link']
            #企业名称
            webJob['Company'] = ''
            if js['metaData'].has_key(u'公司名称'):
                webJob['Company'] = js['metaData'][u'公司名称']['label']
            else:
                return
            #职位类别
            baiXJobCode = u''
            if js['metaData'].has_key(u'分类'):
                webJob['JobName'] = js['metaData'][u'分类']['label']
                baiXJobCode = js['metaData'][u'分类']['value']
            else:
                return
            webJob['JobCode'] = FmtBaiXJobCode('remote_252_1', baiXJobCode)
            webJob['JobType'] = 1
            webJob['SalaryType'] = 0
            if js['metaData'].has_key(u'工资'):
                webJob['Salary'] = js['metaData'][u'工资']['label']
            else:
                webJob['Salary'] = u'面议'
            if js['metaData'].has_key(u'福利待遇'):
                webJob['SSWelfare'] = js['metaData'][u'福利待遇']['label']
            else:
                webJob['SSWelfare'] = ''
            webJob['SBWelfare'] = ''
            webJob['OtherWelfare'] = ''
            if js['metaData'].has_key(u'联系人'):
                webJob['Relation'] = js['metaData'][u'联系人']['label']
            else:
                webJob['Relation'] = ''
            webJob['Mobile'] = js['contact']
            webJob['JobDesc'] = js['content']
            if not webJob['JobDesc']:
                webJob['JobDesc'] = u''
            webJob['JobAddress'] = js[u'具体地点']
            webJob['Email'] = ''
            if js['lng']:
                webJob['GisLongitude'] = js['lng']
                webJob['GisLatitude'] = js['lat']
            else:
                webJob['GisLongitude'] = '0.00'
                webJob['GisLatitude'] = '0.00'
            webJob['ClickTimes'] = js['count']
            #城市区域分割处理
            cityName = ''
            WorkArea1 = ''
            WorkArea2 = ''
            cityAreaName = js['areaNames']
            if len(cityAreaName) >= 1:
                cityName = cityAreaName[0]
            if len(cityAreaName) >= 2:
                WorkArea1 = cityAreaName[1]
            if len(cityAreaName) >= 3:
                WorkArea2 = cityAreaName[2]
            webJob['ProvinceName'] = ''
            webJob['CityName'] = cityName
            webJob['WorkArea'] = cityName
            webJob['WorkArea1'] = WorkArea1
            webJob['WorkArea2'] = WorkArea2
            webJob['CompanyLink'] = ''
            if js['metaData'].has_key(u'招聘人数'):
                webJob['Number'] = js['metaData'][u'招聘人数']['label']
            else:
                webJob['Number'] = u'若干'
            if js['metaData'].has_key(u'工作年限'):
                webJob['Exercise'] = js['metaData'][u'工作年限']['label']
            else:
                webJob['Exercise'] = u'不限'
            if js['metaData'].has_key(u'学历'):
                webJob['Eduacation'] = js['metaData'][u'学历']['label']
            else:
                webJob['Eduacation'] = u'不限'
            webJob['Sex'] = '不限'
            webJob['Age'] = ''
            webJob['SyncStatus'] = 0
            webJob['InsertTime'] = datetime.today()
            webJob['StartDate'] = ''
            webJob['EndDate'] = ''
            webJob['Require'] = u'招%s|学历%s|经验%s|性别%s' % (webJob['Number'], webJob['Eduacation'], webJob['Exercise'], webJob['Sex'])
            #其他默认信息
            webJob['AnFmtID'] = 0
            webJob['KeyValue'] = ''
            webJob['AreaCode'] = ''
            webJob['Tag'] = ''
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
            webJob['PropertyTag'] = ''
            webJob['SalaryValue'] = 0
            webJob['ExerciseValue'] = 0
            webJob['Valid'] = 'T'
            webJob['JobWorkTime'] = ''
            webJob['JobComputerSkill'] = ''
            webJob['ForeignLanguage'] = ''
            webJob['JobFunction'] = ''
            webJob['JobRequest'] = ''
            webJob['InsertTime'] = datetime.today()
            webJob['LastModifyTime'] = datetime.today()
            yield webJob
        finally:
            #log.msg(u'CompanyName:%s,JobTitle:%s,JobName:%s,AreaName:%s' % (webJob['Company'], webJob['JobTitle'], webJob['JobName'], ','.join(cityAreaName)))
            #log.msg(u'src:%s' % webJob['SrcUrl'])
            pass
