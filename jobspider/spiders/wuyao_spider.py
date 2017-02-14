# -*- encoding=utf-8 -*-


try: 
    import xml.etree.cElementTree as ET 
except ImportError: 
    import xml.etree.ElementTree as ET
from datetime import datetime
from scrapy import Spider, log, Request
from jobspider.items import *
from jobspider.scrapy_requests.start_requests import *
from jobspider.utils.tools import FmtAreaCodeSimple, FmtAnnounceDateToDateTime, FmtCmpNameCharacter, FmtSQLCharater


def text_(ele):
    return ele.text if ele.text else ''


class WuYaoSpider(Spider):

    name = 'wuyao'

    def __init__(self, headers, base_url, job_list_url, job_url, co_url, *args, **kwargs):
        super(WuYaoSpider, self).__init__(*args, **kwargs)
        #
        self.site = 12
        self.store_collection = 'FuncIndex'
        #
        self.headers = headers
        self.base_url = base_url
        self.job_list_url = job_list_url
        self.job_url = job_url
        self.co_url = co_url

    @classmethod
    def from_settings(cls, settings, *args, **kwargs):
        headers = settings.get('WUYAO_REQUEST_HEADERS', '')
        base_url = settings.get('WUYAO_BASE_URL', '')
        job_list_url = settings.get('WUYAO_JOB_LIST_URL', '')
        job_url = settings.get('WUYAO_JOB_URL', '')
        co_url = settings.get('WUYAO_CO_URL', '')
        return cls(headers, base_url, job_list_url, job_url, co_url)

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
        rows = get_request_mongo_for_wuyao()
        if rows:
            for row in rows:
                ids.append(row['_id'])
                #时间戳
                publish_time = 0
                if row.has_key('PublishTime'):
                    publish_time = row['PublishTime']
                #
                page = 1
                link_url = self.job_list_url.replace('<?func?>', row['func']).replace('<?page?>', str(page))
                link_url = self.create_url(link_url)
                yield Request(url = link_url,
                    headers = self.headers,
                    meta = {'_id': row['_id'], 'func': row['func'], 'funcName': row['func_name'], 'PublishTime': publish_time, 'page': page},
                    dont_filter = True,
                    callback = self.parse_job_list)
            #批次更新LastTime
            if len(ids) > 0:
                update_start_requests(self.store_collection, ids)

    #职位列表请求成功后解析
    def parse_job_list(self, response):
        try:
            msg = ET.fromstring(response.body)
        except BaseException as e:
            log.msg(u'职位类别<{}>,页数<{}>返回结果非法!'.format(response.meta['funcName'], response.meta['page']), level = log.ERROR)
            return
        #
        _id = response.meta['_id']
        func = response.meta['func']
        funcName = response.meta['funcName']
        pubTime = response.meta['PublishTime']
        page = response.meta['page']
        #
        if msg.find('result').text == '1':
            for item in msg.find('resultbody').findall('item'):
                jobid = item.find('jobid').text
                jobname = item.find('jobname').text
                issuedate = item.find('issuedate').text
                if not response.meta.get('firstPublishTime', None):
                    response.meta['firstPublishTime'] = issuedate
                if issuedate <= pubTime:
                    firstPublishTime = response.meta['firstPublishTime']
                    update_publishtime(self.store_collection, _id, firstPublishTime, 'PublishTime')
                    log.msg(u'职位类别 = %s 换词，发布日期:%s->%s' % (funcName, issuedate, pubTime), level = log.INFO)
                    return
                link_url = self.job_url.replace('<?jid?>', jobid)
                link_url = self.create_url(link_url)
                yield Request(link_url, meta = {'func': func, 'funcName': funcName, 'jobid': jobid}, dont_filter = True, callback = self.parse_job)
            else:
                if page < 20:
                    page += 1
                    link_url = self.job_list_url.replace('<?func?>', func).replace('<?page?>', str(page))
                    link_url = self.create_url(link_url)
                    log.msg(u'采集<{}>,<{}>-><{}>'.format(funcName, response.meta['firstPublishTime'], pubTime))
                    yield Request(url = link_url,
                        headers = self.headers,
                        meta = {'_id': _id, 'func': func, 'funcName': funcName, 'PublishTime': pubTime, 'page': page, 'firstPublishTime': response.meta['firstPublishTime']},
                        dont_filter = True,
                        callback = self.parse_job_list)                

    def parse_job(self, response):
        try:
            msg = ET.fromstring(response.body)
        except BaseException as e:
            log.msg(u'职位类别<{}>,职位编号<{}>返回结果非法!'.format(response.meta['funcName'], response.meta['jobid']), level = log.ERROR)
            return
        #
        func = response.meta['func']
        funcName = response.meta['funcName']
        jobid = response.meta['jobid']
        #
        if msg.find('result').text == '1':
            item = msg.find('resultbody')
            webJob = WebJob()
            webJob['SiteID'] = self.site
            webJob['JobTitle'] = FmtSQLCharater(text_(item.find('jobname')))
            webJob['Company'] = FmtCmpNameCharacter(text_(item.find('coname')))
            webJob['PublishTime'] = FmtAnnounceDateToDateTime(text_(item.find('issuedate')), '-')[0]
            webJob['RefreshTime'] = webJob['PublishTime']
            webJob['JobType'] = 1
            webJob['SalaryType'] = 0
            webJob['Salary'] = text_(item.find('providesalary'))
            webJob['Eduacation'] = text_(item.find('degree'))
            webJob['Number'] = text_(item.find('jobnum'))
            webJob['Exercise'] = text_(item.find('workyear'))
            webJob['SSWelfare'] = text_(item.find('welfare'))
            webJob['SBWelfare'] = text_(item.find('jobtag'))
            webJob['LinkID'] = jobid
            webJob['JobCode'] = str(int(func))
            webJob['JobName'] = funcName
            webJob['Sex'] = u'不限'
            webJob['Require'] = u'招%s人|学历%s|经验%s|性别%s' % (webJob['Number'], webJob['Eduacation'], webJob['Exercise'], webJob['Sex'])
            jobarea = text_(item.find('jobarea')).split('-')
            CityName = jobarea[0]
            webJob['CityName'] = CityName
            webJob['WorkArea'] = CityName
            webJob['WorkArea1'] = ''
            webJob['WorkArea2'] = ''
            if len(jobarea) > 1:
                webJob['WorkArea1'] = jobarea[1]
            if len(jobarea) > 2:
                webJob['WorkArea2'] = jobarea[2]
            webJob['AreaCode'] = FmtAreaCodeSimple('remote_252_1', CityName)
            webJob['JobAddress'] = FmtSQLCharater(item.find('address').text)
            coid = item.find('coid').text
            webJob['CompanyLink'] = 'wuyao_' + coid
            webJob['SyncStatus'] = 0
            webJob['AnFmtID'] = 0
            webJob['KeyValue'] = ''
            webJob['ClickTimes'] = 0
            webJob['SBWelfare'] = ''
            webJob['OtherWelfare'] = ''
            webJob['Relation'] = ''
            webJob['Mobile'] = ''
            webJob['Email'] = ''
            webJob['Tag'] = ''
            webJob['ProvinceName'] = ''
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
            webJob['PropertyTag'] = ''
            webJob['SalaryValue'] = 0
            webJob['ExerciseValue'] = 0
            webJob['Valid'] = 'T'
            webJob['JobWorkTime'] = ''
            webJob['JobComputerSkill'] = ''
            webJob['ForeignLanguage'] = ''
            webJob['JobFunction'] = ''
            webJob['JobRequest'] = ''
            webJob['BusinessCode'] = ''
            webJob['InsertTime'] = datetime.datetime.today()
            webJob['LastModifyTime'] = datetime.datetime.today()
            #替换\符号
            webJob['SrcUrl'] = text_(item.find('share_url'))
            webJob['GisLongitude'] = text_(item.find('joblon'))
            webJob['GisLatitude'] = text_(item.find('joblat'))
            webJob['JobDesc'] = text_(item.find('jobinfo'))
            webJob['CompanyType'] = text_(item.find('cotype'))
            webJob['CompanyScale'] = text_(item.find('cosize'))
            #
            link_url = self.co_url.replace('<?coid?>', coid)
            link_url = self.create_url(link_url)
            yield Request(link_url, meta = {'coid': coid, 'job': webJob}, callback = self.parse_co)

    def parse_co(self, response):
        try:
            msg = ET.fromstring(response.body)
        except BaseException as e:
            log.msg(u'企业编号<{}>返回结果非法!'.format(response.meta['coid']), level = log.ERROR)
            return
            #
        job = response.meta['job']
        if text_(msg.find('result')) == '1':
            item = msg.find('resultbody')
            co = Company()
            co['SiteID'] = self.site
            co['company_id'] = text_(item.find('coid'))
            co['CompanyName'] = FmtCmpNameCharacter(text_(item.find('coname')))
            co['Industry'] = ''
            if item.find('indtype1').text:
            	co['Industry'] = text_(item.find('indtype1'))
            if item.find('indtype2').text:
            	co['Industry'] += ',' + text_(item.find('indtype2'))
            co['CompanyType'] = text_(item.find('cotype'))
            co['CompanyScale'] = text_(item.find('cosize'))
            co['CompanyAddress'] = FmtSQLCharater(text_(item.find('caddr')))
            co['CompanyDesc'] = FmtSQLCharater(text_(item.find('coinfo')))
            co['CompanyUrl'] = text_(item.find('cojumpurl'))
            co['CompanyLogoUrl'] = text_(item.find('logo'))
            co['GisLongitude'] = text_(item.find('lon'))
            co['GisLatitude'] = text_(item.find('lat'))
            co['CityName'] = job['CityName']
            co['AreaCode'] = job['AreaCode']
            co['Relation'] = ''
            co['Mobile'] = ''
            co['Credibility'] = ''
            co['Licensed'] = ''
            co['Yan'] = ''
            co['FangXin'] = ''
            co['Email'] = ''
            co['PraiseRate'] = '0'
            co['UserId'] = ''
            co['UserName'] = ''
            co['ProvinceName'] = ''
            co['WorkArea1'] = ''
            co['AreaCode1'] = ''
            yield co
        yield job