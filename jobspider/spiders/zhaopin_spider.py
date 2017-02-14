# -*- encoding=utf-8 -*-


import json
from time import mktime
from datetime import datetime
from scrapy import Spider, log, Request
from jobspider.items import *
from jobspider.scrapy_requests.start_requests import *
from jobspider.utils.zhaopin_header import ZhaoPinHeader
from jobspider.utils.tools import FmtJobPositionWithPrefix,FmtSQLCharater


class ZhaoPinSpider(Spider):

    name = 'zhaopin'
    download_delay = 2
    randomize_download_delay = True

    def __init__(self, headers, base_url, job_list_url, job_url, *args, **kwargs):
        super(ZhaoPinSpider, self).__init__(*args, **kwargs)
        #
        self.site = 11
        self.store_collection = 'CityIndex'
        self.company_prefix = 'zhaopin_'
        #
        self.headers = headers
        self.base_url = base_url
        self.job_list_url = job_list_url
        self.job_url = job_url

    @classmethod
    def from_settings(cls, settings, *args, **kwargs):
        headers = settings.get('ZHAOPIN_REQUEST_HEADERS', '')
        base_url = settings.get('ZHAOPIN_BASE_URL', '')
        job_list_url = settings.get('ZHAOPIN_JOB_LIST_URL', '')
        job_url = settings.get('ZHAOPIN_JOB_URL', '')
        return cls(headers, base_url, job_list_url, job_url)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls.from_settings(settings, args, kwargs)

    def create_url(self, parameters):
        if parameters is None:
            return ''
        if not parameters.startswith('/'):
            return self.base_url + '/' + parameters
        else:
            return self.base_url + parameters

    #入口函数
    def start_requests(self):
        ids = []
        rows = get_requests_mongo(self.site, 0)
        if rows:
            for row in rows:
                ids.append(row['_id'])
                #时间戳
                publish_time = 0
                if row.has_key('PublishTime'):
                    publish_time = row['PublishTime']
                #
                page = 1
                link_url = self.job_list_url.replace('<?city?>', str(row['CityId'])).replace('<?page?>', str(page))
                link_url = self.create_url(link_url)
                link_url = ZhaoPinHeader().apiDynamicUrl(link_url)
                yield Request(url = link_url,
                              headers = self.headers,
                              meta = {'_id': row['_id'], 'CityId': row['CityId'], 'CityName': row['CityName'], 'PublishTime': publish_time, 'page': page},
                              dont_filter = True,
                              callback = self.parse_job_list)
            #批次更新LastTime
            if len(ids) > 0:
                update_start_requests(self.store_collection, ids)


    #职位列表请求成功后解析
    def parse_job_list(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s get fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'[%s]职位列表请求结果解析异常,非json数据.url=%s' % (response.meta['CityName'], response.url), level = log.INFO)
            return
        #列表解析
        if js['StatusCode'] == 200:
            if js['Positions']:
                for item in js['Positions']:
                    number = item['Number']
                    link_url = self.job_url.replace('<?number?>', number)
                    link_url = self.create_url(link_url)
                    link_url = ZhaoPinHeader().apiDynamicUrl(link_url)
                    yield Request(url = link_url,
                                  headers = self.headers,
                                  dont_filter = True,
                                  callback = self.parse_job)
                #下一页
                if len(js['Positions']) >= 20:
                    page = response.meta['page'] + 1
                    city = response.meta['CityId']
                    name = response.meta['CityName']
                    pub  = response.meta['PublishTime']
                    _id  = response.meta['_id']
                    #
                    link_url = self.job_list_url.replace('<?city?>', str(city)).replace('<?page?>', str(page))
                    link_url = self.create_url(link_url)
                    link_url = ZhaoPinHeader().apiDynamicUrl(link_url)
                    yield Request(url = link_url,
                                  headers = self.headers,
                                  meta = {'_id': _id, 'CityId': city, 'CityName': name, 'PublishTime': pub, 'page': page},
                                  dont_filter = True,
                                  callback = self.parse_job_list)
            else:
                log.msg(u'职位列表请求成功,但是没有职位列表信息.url=%s' % response.url)
        else:
            log.msg(u'职位列表请求失败,原因:%s.url=%s' % (js['StatusDescription'], response.url))

    #职位详情解析
    def parse_job(self, response):
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
        #列表解析
        if js['StatusCode'] == 200:
            #
            pd = js['PositionDetail']
            #过滤没有emaillist的职位
            #if pd['EmailList'] == '':
            #    log.msg(u'职位[%s-%s]没有email地址,丢弃.' % (pd['Number'], pd['Name']))
            #    return
            #
            cd = js['CompanyDetail']
            cr = js['Coordinate']
            #
            publish = pd['DateStart'].replace('T', ' ')
            publish = publish.replace('Z', '')
            pos = publish.rfind('.')
            if pos > 0:
                publish = publish[0: pos - len(publish)]
            publish = datetime.datetime.strptime(publish, '%Y-%m-%d %H:%M:%S')
            #
            if exist_linkid(self.site, pd['Number'], int(mktime(publish.timetuple()))):
                return
            #
            j = WebJob()
            j['SiteID'] = self.site
            j['JobTitle'] = pd['Name']
            j['Company'] = pd['CompanyName']
            j['PublishTime'] = publish
            j['RefreshTime'] = publish
            j['ClickTimes'] = 0
            #依据智联职位类别查找SQL Server职位类别代码与职位名称
            zJob = int(pd['SubJobType'])
            zJobClassName = FmtJobPositionWithPrefix('redis_cache_1', self.company_prefix, zJob)
            if zJobClassName != '':
                j['JobCode'] = zJobClassName.split('#')[0]
                j['JobName'] = zJobClassName.split('#')[1]
            else:
                log.msg(u'职位类别=%d，在redis上没有查找到对应的职位类别代码与职位名称' % zJob, level = log.ERROR)
                return
            #
            j['Salary'] = pd['Salary']
            j['SalaryType'] = 0
            j['Eduacation'] = pd['Education']
            j['Number'] = '%d人' % pd['RecruitNumber']
            j['Exercise'] = pd['WorkingExp']
            if pd.has_key('WelfareTab'):
                j['SSWelfare'] = ','.join(map(lambda wel: wel.values()[0], pd['WelfareTab']))
            else:
                j['SSWelfare'] = ''
            j['SBWelfare'] = ''
            j['OtherWelfare'] = ''
            j['JobDesc'] = pd['Description']
            j['Relation'] = ''
            j['Mobile'] = ''
            j['Email'] = pd['EmailList']
            j['JobAddress'] = FmtSQLCharater(cd['Address'])
            j['InsertTime'] = datetime.datetime.today()
            j['Sex'] = u'不限'
            j['LinkID'] = pd['Number']
            j['Tag'] = ''
            j['ProvinceName'] = ''
            j['CityName'] = pd['WorkCity']
            j['WorkArea'] = pd['WorkCity']
            if pd.has_key('CityDistrict'):
                j['WorkArea1'] = pd['CityDistrict']
            else:
                j['WorkArea1'] = ''
            j['WorkArea2'] = ''
            j['CompanyLink'] = self.company_prefix + pd['CompanyNumber']
            if pd['WorkType'] == u'全职' or pd['WorkType'] == u'实习':
                j['JobType'] = 1
            else:
                j['JobType'] = 2
            j['SyncStatus'] = 0
            j['SrcUrl'] = response.url
            j['GisLongitude'] = cr['Longitude']
            j['GisLatitude'] = cr['Latitude']
            j['StartDate'] = pd['DateStart']
            j['EndDate'] = pd['DateEnd']
            #其他默认信息
            j['AnFmtID'] = 0
            j['KeyValue'] = ''
            if cd['Industry']:
                j['Industry'] = cd['Industry']
            else:
                j['Industry'] = ''
            j['CompanyType'] = cd['Property']
            j['CompanyScale'] = cd['CompanySize']
            j['Require'] = u'招%s|学历%s|经验%s|性别%s' % (j['Number'], j['Eduacation'], j['Exercise'], j['Sex'])
            j['Telphone1'] = ''
            j['Telphone2'] = ''
            j['Age'] = 0
            j['ValidDate'] = ''
            j['ParentName'] = ''
            j['EduacationValue'] = 0
            j['SalaryMin'] = 0.0
            j['SalaryMax'] = 0.0
            j['NumberValue'] = 0
            j['SexValue'] = 0
            j['OperStatus'] = 0
            j['LastModifyTime'] = datetime.datetime.today()
            j['PropertyTag'] = ''
            j['SalaryValue'] = 0
            j['ExerciseValue'] = 0
            j['Valid'] = 'T'
            j['JobWorkTime'] = ''
            j['JobComputerSkill'] = ''
            j['ForeignLanguage'] = ''
            j['JobFunction'] = ''
            j['JobRequest'] = ''
            j['BusinessCode'] = ''
            #企业信息
            c = Company()
            c['SiteID'] = self.site
            c['company_id'] = self.company_prefix + cd['Number']
            c['Credibility'] = ''
            c['Licensed'] = ''
            c['Yan'] = ''
            c['FangXin'] = ''
            c['CompanyName'] = cd['Name']
            c['CityName'] = cd['CityName']
            c['AreaCode'] = ''
            c['Relation'] = ''
            c['Mobile'] = ''
            c['Industry'] = cd['Industry']
            c['CompanyType'] = cd['Property']
            c['CompanyScale'] = cd['CompanySize']
            c['CompanyAddress'] = cd['Address']
            c['CompanyDesc'] = cd['Description']
            c['CompanyUrl'] = cd['Url']
            if cd['companyLogo']:
                c['CompanyLogoUrl'] = cd['companyLogo']
            else:
                c['CompanyLogoUrl'] = ''
            c['Email'] = ''
            c['PraiseRate'] = '0'
            c['GisLongitude'] = cr['Longitude']
            c['GisLatitude'] = cr['Latitude']
            c['UserId'] = ''
            c['UserName'] = ''
            c['ProvinceName'] = ''
            c['WorkArea1'] = cd['CityName']
            c['AreaCode1'] = ''
            # log.msg(j['JobCode'] + '--' + j['JobName'])
            yield c
            yield j
        else:
            log.msg(u'职位详情请求失败,原因:%s.url=%s' % (js['StatusDescription'], response.url))
