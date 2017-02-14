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


class ChinaHRSpider(Spider):

    name = "chinahr"
    download_delay = 0.1
    randomize_download_delay = True

    def __init__(self, reqHeaders, baseUrl, jobListUrl, category = None, *args, **kwargs):
        super(ChinaHRSpider, self).__init__(*args, **kwargs)
        self.reqHeaders = reqHeaders
        self.baseUrl = baseUrl
        self.jobListUrl = jobListUrl

    @classmethod
    def from_settings(cls, settings):
        reqHeaders = settings.get('CHINAHR_REQUEST_HEADERS', '')
        baseUrl = settings.get('CHINAHR_BASEURL', 'http://www.chinahr.com')
        jobListUrl = settings.get('CHINAHR_JOBLISTURL', '')
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
        rows = get_requests_mongo(7, 0)
        if rows:
            for row in rows:
                ids.append(row['_id'])
                #时间戳
                publishTime = 0
                if row.has_key('PublishTime'):
                    publishTime = row['PublishTime']
                link = self.jobListUrl.replace('<?CityId?>', row['CityId'])
                yield Request(url = link,
                    meta = {'use_proxy': True,
                        '_id': row['_id'],
                        'CityId': row['CityId'],
                        'CityName': row['CityName'],
                        'PublishTime': publishTime,
                        'FirstPage': True,
                        'download_timeout': 50
                        },
                    dont_filter = True,
                    callback = self.parse_joblist)
            #批次更新LastTime
            if len(ids) > 0:
                update_start_requests('CityIndex', ids)

    #职位列表解析
    def parse_joblist(self, response):
        log.msg(u'CityName=%s,url=%s' % (response.meta['CityName'], response.url), level=log.INFO)
        hxs = Selector(response)
        items = hxs.xpath("//div[@class='joblist_showlist']/table/tr/td/label/input[@class='js_jobs_item']")
        if not items:
            log.msg(u'抓取职位列表失败', level = log.INFO)
            return
        maxIndex = len(items)
        if maxIndex == 0:
            log.msg(u'没有职位数据了，可能抓取被封', level=log.INFO)
        #下一页处理
        link = first_item(hxs.xpath("//a[@class='paging_r']/@href").extract())
        if link is not None:
            link = self.create_url(link)
            log.msg(u'下一页:%s' % link)
        #
        for (index, item) in enumerate(items):
            id = first_item(item.xpath("@value").extract())
            #组装formdata
            formdata = {}
            formdata['id'] = id
            formdata['searchType'] = ''
            formdata['keyWord'] = ''
            #请求
            yield FormRequest(url = self.create_url('/modules/jsapply/?c=jobInfo&m=getJobInfo&noblock=1'),
                headers = dict({'X-Requested-With': 'XMLHttpRequest'}, **self.reqHeaders),
                formdata = formdata,
                meta = {'use_proxy': True,
                    '_id': response.meta['_id'],
                    'CityId': response.meta['CityId'],
                    'CityName': response.meta['CityName'],
                    'NextPage': link if (index + 1) == maxIndex else None,
                    'PublishTime': response.meta['PublishTime'],
                    #首页第一条职位
                    'FirstFirst': True if response.meta.has_key('FirstPage') and index == 0 else False,
                    #本页最后一条
                    'Last': True if (index + 1) == maxIndex else False,
                    'download_timeout': 50
                    },
                dont_filter = True,
                callback = self.parse_job)

    #企业职位信息解析(json)
    def parse_job(self, response):
        js = json.loads('{}')
        try:
            js = json.loads(response.body)
        except:
            log.msg(u'职位详情返回非法的json数据,%s' % (response.body, ), level = log.ERROR)
            return
        #
        firstPublishTime = 0
        _id = response.meta['_id']
        if response.meta.has_key('FirstPublishTime'):
            firstPublishTime = response.meta['FirstPublishTime']
        PublishTime = response.meta['PublishTime']
        if js.has_key('refTime'):
            refTime = int(js['refTime'])
        else:
            refTime = int(mktime(datetime.now().timetuple()))
        pauseTime = 0
        if js.has_key('pauseTime'):
            pauseTime = int(js['pauseTime'])
        if firstPublishTime == 0:
            firstPublishTime = refTime
        if refTime <= PublishTime:
            if pauseTime == 0:
                refTime = int(mktime(datetime.now().timetuple()))
            else:
                #本次最大发布时间<=上次抓取时间，直接退出
                if response.meta['Last']:
                    #第一页的发布结束日期＝该职位的发布日期，不是第一条职位的发布日期
                    str_t0 = strftime('%Y-%m-%d %H:%M:%S', localtime(PublishTime))
                    str_t1 = strftime('%Y-%m-%d %H:%M:%S', localtime(firstPublishTime))
                    log.msg(u'0.CityName= %s 结束换词，发布日期:%s->%s' % (response.meta['CityName'], str_t0, str_t1), level = log.INFO)
                return
        elif response.meta['FirstFirst']:
            update_publishtime('CityIndex', _id, firstPublishTime, 'PublishTime')
            str_t0 = strftime('%Y-%m-%d %H:%M:%S', localtime(PublishTime))
            str_t1 = strftime('%Y-%m-%d %H:%M:%S', localtime(firstPublishTime))
            log.msg(u'0.CityName= %s 开始换词，发布日期:%s->%s' % (response.meta['CityName'], str_t0, str_t1), level = log.INFO)
        #下一页处理
        nextPage = response.meta['NextPage']
        if nextPage:
            yield Request(url = nextPage,
                meta = {'use_proxy': True,
                        '_id': _id,
                        'CityId': response.meta['CityId'],
                        'CityName': response.meta['CityName'],
                        'PublishTime': PublishTime,
                        'FirstPublishTime': firstPublishTime,
                        'download_timeout': 10
                        },
                dont_filter = True,
                callback = self.parse_joblist)
        #由于存在本页与上一页职位存在重复内容(新增职位会导致页数变动),需要进行职位去重(依据职位linkID,refTime去重)
        if not js.has_key('id'):
            log.msg(u'该职位没有id,丢弃该职位')
            return
        jobName = ''
        jobCode = ''
        #查找第3级
        for jobType in js['jobType']:
            if jobType.has_key('jobNameId'):
                jobName = jobType['jobName']
                jobCode = '%s_%s_%s' % (jobType['bigId'], jobType['categoryId'], jobType['jobNameId'])
                break
        '''
        #查找第2级
        if jobCode == '':
            log.msg(u'职位所属类别不能明确到第3级')
            for jobType in js['jobType']:
                if jobType.has_key('categoryId'):
                    jobName = jobType['categoryName']
                    jobCode = '%s_%s' % (jobType['bigId'], jobType['categoryId'])
                    break
        #查找第1级
        if jobCode == '':
            for jobType in js['jobType']:
                if jobType.has_key('bigId'):
                    jobCode = jobType['bigId']
                    webJob['JobName'] = jobType['bigName']
                    webJob['JobCode'] = FmtChinahrJobCode('remote_252_1', jobCode)
                    break
        '''
        if jobCode == '':
            log.msg(u'职位所属类别不明确，丢弃该职位[%s]' % js['jobName'])
            return
        LinkID = js['id']
        if exist_linkid(7, LinkID, refTime):
            #log.msg(u'存在相同职位id,重复抓取,LinkID:%s,refTime:%s' % (LinkID, refTime))
            return
        log.msg(u'增加职位:%s' % js['jobName'])
        webJob = WebJob()
        webJob['SiteID'] = 7
        webJob['JobName'] = jobName
        webJob['JobCode'] = FmtChinahrJobCode('remote_252_1', jobCode)
        webJob['JobTitle'] = js['jobName'].replace('/', '').replace(' ','')
        webJob['Company'] = js['comName']
        postTime = datetime.fromtimestamp(refTime)
        webJob['PublishTime'] = postTime
        webJob['RefreshTime'] = postTime
        #
        if js.has_key('salary'):
            webJob['Salary'] = js['salary']
        else:
            webJob['Salary'] = u'面议'
        if js.has_key('minSalary'):
            webJob['SalaryMin'] = js['minSalary']
        else:
            webJob['SalaryMin'] = '0'
        if js.has_key('maxSalary'):
            webJob['SalaryMax'] = js['maxSalary']
        else:
            webJob['SalaryMax'] = '0'
        webJob['Eduacation'] = js['degName']
        webJob['Number'] = js['number']
        webJob['Exercise'] = js['experience']
        webJob['Sex'] = js['gender']
        webJob['SSWelfare'] = ''
        webJob['SBWelfare'] = ''
        webJob['OtherWelfare'] = ''
        if js.has_key('welfare'):
            ret = ''
            for welfare in js['welfare']:
                ret += welfare['name']
                ret += ' '
                #
            if ret.endswith(' '):
                ret = ret[0 : -1]
            webJob['SSWelfare'] = ret
        #
        if js.has_key('contact'):
            webJob['Relation'] = js['contact']
        else:
            webJob['Relation'] = js['comContact']
        webJob['Mobile'] = ''
        if js.has_key('phone'):
            webJob['Mobile'] = js['phone']
        else:
            if js.has_key('telphone'):
                webJob['Mobile'] = js['telphone']
            if js.has_key('mobile'):
                if webJob['Mobile'] != '':
                    webJob['Mobile'] += ','
                webJob['Mobile'] += js['mobile']
        webJob['InsertTime'] = datetime.today()
        if js.has_key('jobEmail'):
            webJob['Email'] = js['jobEmail'] #comEmail,jobEmail, email
        elif js.has_key('email'):
            webJob['Email'] = js['email']
        else:
            webJob['Email'] = js['comEmail']
        #Email有多个，只取第一个
        emailEndPos = webJob['Email'].find(';')
        if emailEndPos > 0:
            webJob['Email'] = webJob['Email'][0: emailEndPos]
        #任职条件 + 岗位职责 + 其他福利
        if js['condition'] != js['jobDesc']:
            webJob['RequirementsDesc'] = js['condition']
        else:
            webJob['RequirementsDesc'] = ''
        webJob['ResponsibilityDesc'] = js['jobDesc']
        if js.has_key('benefits'):
            if js['benefits'] != js['jobDesc']:
                webJob['JobDesc'] = js['benefits']
            else:
                webJob['JobDesc'] = ''
        else:
            webJob['JobDesc'] = ''
        webJob['Require'] = u'招%s人|学历%s|经验%s|性别%s' % (webJob['Number'], webJob['Eduacation'], webJob['Exercise'], webJob['Sex'])
        webJob['JobRequest'] = ''
        webJob['LinkID'] = LinkID
        webJob['Tag'] = ''
        workPlace = js['workPlace']
        #工作地点情况(分单点或多点)
        place = workPlace[0]
        if len(workPlace) > 1:
            for place in workPlace:
                if place.has_key('cityId'):
                    if '%s_%s' % (place['provId'], place['cityId']) == response.meta['CityId']:
                        break
                #0或1级城市
                else:
                    #全国,等于当前搜索城市名
                    if place['provId'] == '-1':
                        place['provName'] = ''
                        place['cityId'] = response.meta['CityId']
                        place['cityName'] = response.meta['CityName']
                        break
                    #直辖市(北京，天津，上海，重庆)
                    elif place['provId'] == response.meta['CityId']:
                        place['cityId'] = response.meta['CityId']
                        place['cityName'] = place['provName']
                        place['provName'] = ''
                        break
                    #职位只填写省级，依据城市仍可搜索出来
                    elif place['provId'] == response.meta['CityId'][0: 2]:
                        place['cityId'] = response.meta['CityId']
                        place['cityName'] = response.meta['CityName']
                        break
        if place.has_key('cityId'):
            CityName = place['cityName']
        #直辖市
        else:
            if place['provId'] == '-1':
                CityName = response.meta['CityName']
            else:
                CityName = place['provName']
        #去除城市最后的'市'
        if CityName[-1: ] == u'市':
            CityName = CityName[0: -1]
        webJob['ProvinceName'] = ''
        if place.has_key('provName'):
            webJob['ProvinceName'] = place['provName']
        webJob['CityName'] = CityName
        webJob['WorkArea'] = CityName
        if place.has_key('distName'):
            webJob['WorkArea1'] = place['distName']
        else:
            webJob['WorkArea1'] = ''
        if js.has_key('ivAddr'):
            webJob['JobAddress'] = js['ivAddr']
        else:
            webJob['JobAddress'] = webJob['ProvinceName'] + CityName + webJob['WorkArea1']
        webJob['WorkArea2'] = ''
        webJob['AreaCode'] = FmtAreaCodeSimple('remote_252_1', CityName)
        webJob['CompanyLink'] = 'cnc_' + js['comId']
        webJob['JobType'] = 1
        webJob['SyncStatus'] = 0
        webJob['SrcUrl'] = self.create_url('/job/%s.html' % webJob['LinkID'])
        webJob['GisLongitude'] = '0'
        webJob['GisLatitude'] = '0'
        if js.has_key('map'):
            webJob['GisLatitude'] = js['map']['yCoord']
            webJob['GisLongitude'] = js['map']['xCoord']
        webJob['ClickTimes'] = js['looked']
        webJob['AnFmtID'] = 0
        webJob['KeyValue'] = ''
        webJob['Industry'] = js['industryNameLong']
        if webJob['Industry'] == '':
            webJob['Industry'] = js['industryName']
        webJob['CompanyType'] = js['typeName']
        webJob['CompanyScale'] = js['size']
        webJob['Telphone1'] = ''
        webJob['Telphone2'] = ''
        webJob['Age'] = js['age']
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
        webJob['SalaryType'] = 0
        webJob['StartDate'] = ''
        webJob['EndDate'] = ''
        webJob['BusinessCode'] = ''
        yield webJob
        #log.msg(str(webJob['JobName']), level = log.INFO)
        #加入企业信息
        cmp = Company()
        cmp['SiteID'] = 7
        cmp['company_id'] = webJob['CompanyLink']
        cmp['Credibility'] = 0
        cmp['Licensed'] = 0
        cmp['Yan'] = 0
        cmp['FangXin'] = 0
        if js.has_key('comAuditVal'):
            if js['comAuditVal'] == u'普审':
                cmp['Yan'] = 1
            if js['comAuditVal'] == u'证审':
                cmp['Licensed'] = 1
                cmp['Yan'] = 1
        cmp['CompanyName'] = js['comName']
        cmp['CityName'] = ''
        if js.has_key('corpLocation'):
            if js['corpLocation'].has_key('cityName'):
                cmp['CityName'] = js['corpLocation']['cityName']
            elif js['corpLocation']['provId'] in ('34', '35', '36', '37'):
                cmp['CityName'] = js['corpLocation']['provName']
            if cmp['CityName'][-1: ] == u'市':
                cmp['CityName'] = cmp['CityName'][0: -1]
        cmp['Industry'] = webJob['Industry']
        cmp['CompanyType'] = webJob['CompanyType']
        cmp['CompanyScale'] = webJob['CompanyScale']
        if js.has_key('addr'):
            cmp['CompanyAddress'] = FmtSQLCharater(js['addr'])
        else:
            cmp['CompanyAddress'] = ''
            if js.has_key('corpLocation'):
                if js['corpLocation'].has_key('provName'):
                    if js['corpLocation']['provId'] not in ('34', '35', '36', '37'):
                        cmp['CompanyAddress'] = js['corpLocation']['provName']
                if js['corpLocation'].has_key('cityName'):
                    cmp['CompanyAddress'] += js['corpLocation']['cityName']
                if js['corpLocation'].has_key('distName'):
                    cmp['CompanyAddress'] += js['corpLocation']['distName']
        #
        cmpRel = js['comContact']
        cmp['CompanyUrl'] = js['comNameUrl']
        if js.has_key('logo_path'):
            cmp['CompanyLogoUrl'] = js['logo_path']
        else:
            cmp['CompanyLogoUrl'] = ''
        cmp['Relation'] = FmtSQLCharater(cmpRel)
        cmp['Mobile'] = ''
        if js.has_key('comPhone'):
            cmp['Mobile'] = js['comPhone']
        if js.has_key('comMobile'):
            if cmp['Mobile'] != '':
                cmp['Mobile'] += ','
            cmp['Mobile'] += js['comMobile']
        if js.has_key('comEmail'):
            cmp['Email'] = js['comEmail']
        else:
            cmp['Email'] = ''
        if js.has_key('compDesc'):
            cmpDesc = js['compDesc']
        else:
            cmpDesc = ''
        cmp['CompanyDesc'] = FmtSQLCharater(cmpDesc)
        cmp['PraiseRate'] = '0'
        cmp['GisLongitude'] = '0'
        cmp['GisLatitude'] = '0'
        cmp['UserId'] = ''
        cmp['UserName'] = ''
        cmp['ProvinceName'] = ''
        cmp['WorkArea1'] = ''
        cmp['AreaCode1'] = ''
        yield cmp
        #log.msg(str(cmp['CompanyName']), level = log.INFO)
