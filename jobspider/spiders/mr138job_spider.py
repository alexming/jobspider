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


class MR138JobSpider(Spider):

    name = "mr138Job"
    #download_delay = 0.1
    #randomize_download_delay = True

    def __init__(self, reqHeaders, baseUrl, jobListUrl, category = None, *args, **kwargs):
        super(MR138JobSpider, self).__init__(*args, **kwargs)
        self.siteID = 8
        self.storeCollection = 'mr138Position'
        self.companyPrefix = 'mr138_'
        #
        self.reqHeaders = reqHeaders
        self.baseUrl = baseUrl
        self.jobListUrl = jobListUrl

    @classmethod
    def from_settings(cls, settings):
        reqHeaders = settings.get('MR138JOB_REQUEST_HEADERS', '')
        baseUrl = settings.get('MR138JOB_BASEURL', '')
        jobListUrl = settings.get('MR138JOB_JOBLISTURL', '')
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
                body = '''{"KeywordType": "1", "Position": "%s", "Area": "0", "Keyword": ""}''' % row['Position']
                yield Request(url = self.jobListUrl.replace('<?PageIndex?>', '1'),
                    meta = {'use_proxy': False, '_id': row['_id'], 'Position': row['Position'], 'Name': row['Name'], 'PageIndex': 1, 'PublishTime': publishTime},
                    headers = self.reqHeaders,
                    method='POST',
                    body=body,
                    dont_filter=True,
                    callback=self.parse_joblist)
                    #批次更新LastTime
            if len(ids) > 0:
                update_start_requests(self.storeCollection, ids)

    #职位列表解析
    def parse_joblist(self, response):
        if response.body == '' or response.body == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(response.body)
        except:
            return
        #列表解析
        #
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
        if js['State'] and js['Value'] and js['Value']['ListSearchModel']:
            log.msg(u'Position=%s,pageIndex=%d,pageSize=%d' % (JobName, pageIndex, len(js['Value']['ListSearchModel'])), level=log.INFO)
            for AJob in js['Value']['ListSearchModel']:
                LinkID = str(AJob['HireId'])
                postDateTime, postUnixTime = FmtAnnounceDateToDateTime(AJob['AnnounceDate'])
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
                #企业详情
                yield Request(url = self.create_url('/Company/1/%s?' % AJob['CompanyId']),
                    callback = self.parse_cmp_detail,
                    dont_filter = True
                    )
                if exist_linkid(self.siteID, LinkID, postUnixTime):
                    continue
                #
                webJob = WebJob()
                webJob['SiteID'] = self.siteID
                webJob['JobTitle'] = AJob['HireName']
                webJob['Company'] = AJob['CompanyName']
                webJob['PublishTime'] = postDateTime
                webJob['RefreshTime'] = postDateTime
                webJob['JobName'] = JobName
                #依据美容人才网职位编码获取线下职位编码
                webJob['JobCode'] = FmtJobPositionWithPrefix('remote_252_1', self.companyPrefix, Position)
                webJob['Salary'] = AJob['Pay']
                webJob['SSWelfare'] = ''
                webJob['SBWelfare'] = ''
                webJob['OtherWelfare'] = ''
                webJob['InsertTime'] = datetime.today()
                webJob['Email'] = ''
                webJob['LinkID'] = LinkID
                webJob['Tag'] = ''
                #城市区域分割处理
                cityAreaName = AJob['Area']
                cityAreaCode = FmtCityAreaCodeWithPrefix('remote_252_1', self.companyPrefix, cityAreaName)
                provName = ''
                cityName = ''
                areaName = ''
                #市级
                if len(cityAreaCode) == 4:
                    #湖北武汉 湖南长沙
                    #内蒙古与黑龙江 省份中文名长度＝3,其他省份＝2
                    if cityAreaCode[0: 2] in ('15', '23'):
                        provName = cityAreaName[0: 3]
                        cityName = cityAreaName[3: ]
                    else:
                        provName = cityAreaName[0: 2]
                        cityName = cityAreaName[2: ]
                    webJob['ProvinceName'] = provName
                    webJob['CityName'] = cityName
                    webJob['WorkArea'] = cityName
                    webJob['AreaCode'] = cityAreaCode
                    webJob['WorkArea1'] = ''
                    webJob['BusinessCode'] = ''
                #区级
                elif len(cityAreaCode) == 6:
                    cityName = cityAreaName[0: 2]
                    areaName = cityAreaName[2: ]
                    webJob['ProvinceName'] = ''
                    webJob['CityName'] = cityName
                    webJob['WorkArea'] = cityName
                    webJob['AreaCode'] = cityAreaCode[0: 4]
                    webJob['WorkArea1'] = areaName
                    webJob['BusinessCode'] = cityAreaCode
                #丢弃没有城市的职位数据
                else:
                    continue
                webJob['WorkArea2'] = ''
                webJob['CompanyLink'] = self.companyPrefix + str(AJob['CompanyId'])
                webJob['JobType'] = 1
                webJob['SyncStatus'] = 0
                webJob['InsertTime'] = datetime.today()
                #替换\符号
                webJob['SrcUrl'] = self.create_url('/Hire/1/%s?' % LinkID)
                #职位详情
                yield Request(url= self.create_url('/Hire/1/%s?' % LinkID),
                    meta = {'WebJob': webJob},
                    callback = self.parse_job_detail,
                    dont_filter = True
                    )
            #下页处理
            if len(js['Value']['ListSearchModel']) > 0:
                body = '''{"KeywordType": "1", "Position": "%s", "Area": "0", "Keyword": ""}''' % Position
                yield Request(url = self.jobListUrl.replace('<?PageIndex?>', str(pageIndex)),
                    meta = {'use_proxy': False, '_id': _id, 'Position': Position, 'Name': JobName, 'PageIndex': pageIndex + 1, 'FirstUpdate': first_update, 'PublishTime': PublishTime},
                    headers = self.reqHeaders,
                    method='POST',
                    body=body,
                    dont_filter=True,
                    callback=self.parse_joblist)

    #职位详情解析
    def parse_job_detail(self, response):
        if response.body == '' or response.body == '[]':
            log.msg(format= '%jobDetail.(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(response.body)
        except:
            return
        if js['State']:
            jv = js['Value']
            webJob = response.meta['WebJob']
            webJob['Relation'] = jv['Contact']
            if jv['Tel'] == None:
                webJob['Mobile'] = ''
            else:
                webJob['Mobile'] = jv['Tel']
            if jv['Address'] == None:
                webJob['JobAddress'] = ''
            else:
                webJob['JobAddress'] = jv['Address']
            webJob['StartDate'] = jv['AnnounceDate']
            webJob['EndDate'] = jv['EndDate']
            webJob['Number'] = jv['Number']
            webJob['Exercise'] = jv['Experience']
            webJob['JobDesc'] = jv['Introduce']
            webJob['Eduacation'] = ''
            webJob['Sex'] = u'不限'
            webJob['Require'] = u'招%s人|学历%s|经验%s|性别%s' % (webJob['Number'], webJob['Eduacation'], webJob['Exercise'], webJob['Sex'])
            #其他默认信息
            webJob['AnFmtID'] = 0
            webJob['KeyValue'] = ''
            webJob['SSWelfare'] = ''
            webJob['SBWelfare'] = ''
            webJob['OtherWelfare'] = ''
            webJob['GisLongitude'] = '0'
            webJob['GisLatitude'] = '0'
            webJob['SalaryType'] = 0
            webJob['Tag'] = ''
            webJob['ClickTimes'] = 0
            webJob['Telphone1'] = ''
            webJob['Telphone2'] = ''
            webJob['Age'] = 0
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
        else:
            log.msg(u'职位详情抓取异常,原因:%s' % js['Message'], level = log.INFO)

    #企业详情解析
    def parse_cmp_detail(self, response):
        if response.body == '' and response.body == '[]':
            log.msg(format= '%jobDetail.(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(response.body)
        except:
            return
        if js['State']:
            jv = js['Value']
            cmp = Company()
            cmp['SiteID'] = self.siteID
            cmp['company_id'] = self.companyPrefix + str(jv['Id'])
            cmp['CompanyName'] = jv['CompanyName']
            #
            cityAreaName = jv['Area']
            cityAreaCode = FmtCityAreaCodeWithPrefix('remote_252_1', self.companyPrefix, u'%s%s' % (self.companyPrefix.replace('_', '.'), cityAreaName))
            provName = ''
            cityName = ''
            areaName = ''
            #市级
            if len(cityAreaCode) == 4:
                #湖北武汉 湖南长沙
                #内蒙古与黑龙江 省份中文名长度＝3,其他省份＝2
                if cityAreaCode[0: 2] in ('15', '23'):
                    provName = cityAreaName[0: 3]
                    cityName = cityAreaName[3: ]
                else:
                    provName = cityAreaName[0: 2]
                    cityName = cityAreaName[2: ]
                cmp['ProvinceName'] = provName
                cmp['CityName'] = cityName
                cmp['AreaCode'] = cityAreaCode
                cmp['WorkArea1'] = ''
                cmp['AreaCode1'] = ''
            #区级
            elif len(cityAreaCode) == 6:
                cityName = cityAreaName[0: 2]
                areaName = cityAreaName[2: ]
                cmp['ProvinceName'] = ''
                cmp['CityName'] = cityName
                cmp['AreaCode'] = cityAreaCode[0: 4]
                cmp['WorkArea1'] = areaName
                cmp['AreaCode1'] = cityAreaCode
            else:
                cmp['ProvinceName'] = ''
                cmp['CityName'] = ''
                cmp['AreaCode'] = ''
                cmp['WorkArea1'] = ''
                cmp['AreaCode1'] = ''
            cmp['Industry'] = u'美容美发'
            cmp['CompanyType'] = u'其他'
            cmp['CompanyScale'] = jv['Worker']
            if jv['Address'] == None:
                cmp['CompanyAddress'] = ''
            else:
                cmp['CompanyAddress'] = jv['Address']
            cmp['Relation'] = jv['Contact']
            if jv['Tel'] == None:
                cmp['Mobile'] = ''
            else:
                cmp['Mobile'] = jv['Tel']
            cmp['CompanyDesc'] = jv['Introduce']
            cmp['Email'] = ''
            cmp['CompanyUrl'] = ''
            cmp['CompanyLogoUrl'] = jv['Logo']
            cmp['PraiseRate'] = '0'
            cmp['GisLongitude'] = '0'
            cmp['GisLatitude'] = '0'
            cmp['UserId'] = ''
            cmp['UserName'] = ''
            #
            if jv['Map'] == 0:
                yield cmp
            else:
                yield Request(url = self.create_url('/Map/1/%s?' % jv['Id']),
                    meta = {'Company': cmp},
                    callback = self.parse_cmp_gps,
                    dont_filter = True
                    )

    #企业gps解析
    def parse_cmp_gps(self, response):
        cmp = response.meta['Company']
        if response.body == '' and response.body == '[]':
            yield cmp
            log.msg(format= '%jobDetail.(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        try:
            js = json.loads(response.body)
            if js['State']:
                jv = js['Value']
                cmp['GisLongitude'] = str(jv['x'])
                cmp['GisLatitude'] = str(jv['y'])
            yield cmp
        except:
            yield cmp
