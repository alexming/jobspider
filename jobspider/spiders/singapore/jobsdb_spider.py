# -*- coding: utf-8 -*-

import json
from datetime import datetime
from scrapy import Spider, log, Request
from jobspider.jobsdb_items import *
from jobspider.utils.tools import FmtSQLCharater


class JobsDBSpider(Spider):

    name = 'singapore.jobsdb'

    def __init__(self, headers, base_url, list_url, info_url, category = None, *args, **kwargs):
        super(JobsDBSpider, self).__init__(*args, **kwargs)
        self.headers = headers
        self.base_url = base_url
        self.list_url = list_url
        self.info_url = info_url
        self.site_id = 12

    @classmethod
    def from_settings(cls, settings):
        headers = settings.get('JOBSDB_REQUEST_HEADERS', '')
        base_url = settings.get('JOBSDB_BASE_URL', '')
        list_url = settings.get('JOBSDB_LIST_URL', '')
        info_url = settings.get('JOBSDB_INFO_URL', '')
        return cls(headers, base_url, list_url, info_url)

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

    def _list_request_by_page(self, page):
        link_url = self.list_url.replace('<?page?>', str(page))
        return Request(url=self.create_url(link_url),
                      headers=self.headers,
                      meta={'page': page},
                      dont_filter=True,
                      callback=self.parse_list)

    def _info_request_by_AdId(self, AdId):
        link_url = self.info_url.replace('<?JobAdIds?>', AdId)
        return Request(url=self.create_url(link_url),
                      headers=self.headers,
                      meta={'AdId': AdId},
                      dont_filter=True,
                      callback=self.parse_job)

    def _fmt_json(self, data):
        if data == '' or data == '[]':
            return None
        js = json.loads('{}')
        try:
            js = json.loads(data)
            return js
        except:
            return None

    #入口函数
    def start_requests(self):
        yield self._list_request_by_page(1)

    #
    def parse_list(self, response):
        data = response.body
        js = self._fmt_json(data)
        if js:
            #列表解析
            for item in js['JobSearchResultItems']:
                AdId = item['JobAdId']
                yield self._info_request_by_AdId(AdId)
            #下一页
            if len(js['JobSearchResultItems']) > 0:
                page = response.meta['page'] + 1
                yield self._list_request_by_page(page)
        else:
            log.msg(u'职位列表请求结果解析异常,非json数据.url=%s' % response.url, level = log.INFO)

    def parse_job(self, response):
        data = response.body
        js = self._fmt_json(data)
        if js and js.has_key('JobAdDetails'):
            jd = js['JobAdDetails'][0]
            if jd:
                job = JobsDB_Job()
                job['SiteID'] = self.site_id
                job['LinkID'] = jd['Id']
                job['JobTitle'] = jd['JobTitle']
                job['Company'] = jd['Company']
                job['Industry'] = jd['Industry']
                for func in jd['JobFunction']:
                    job['JobName'] += func + '#'
                job['JobDesc'] = FmtSQLCharater(jd['JobDesc'])
                job['Salary'] = jd['Salary']
                if jd['SalaryLow'] <> 'Hidden' and jd['SalaryLow'] <> 'Not Provided':
                    job['SalaryMin'] = float(jd['SalaryLow'].replace(',', '').replace('+', ''))
                if jd['SalaryUp'] <> 'Hidden' and jd['SalaryUp'] <> 'Not Provided':
                    job['SalaryMax'] = float(jd['SalaryUp'].replace(',', '').replace('+', ''))
                '''
                if jd['SalaryUnit'] <> 'Hidden':
                    job['SalaryType'] = jd['SalaryUnit']
                '''
                job['Eduacation'] = jd['Qualification']
                CareerLevel = jd['CareerLevel']
                job['Exercise'] = jd['WorkExperience']
                EmploymentTerm = jd['EmploymentTerm']
                job['JobTypeName'] = EmploymentTerm
                if EmploymentTerm.find('Full Time') >= 0:
                    job['JobType'] = 1
                elif EmploymentTerm.find('Part Time') >= 0:
                    job['JobType'] = 2
                elif EmploymentTerm.find('Permanent') >= 0:
                    job['JobType'] = 3
                elif EmploymentTerm.find('Temporary') >= 0:
                    job['JobType'] = 4
                elif EmploymentTerm.find('Contract') >= 0:
                    job['JobType'] = 5
                elif EmploymentTerm.find('Internship') >= 0:
                    job['JobType'] = 6
                elif EmploymentTerm.find('Freelance') >= 0:
                    job['JobType'] = 7
                elif EmploymentTerm.find('Contract-to-Perm') >= 0:
                    job['JobType'] = 8
                elif EmploymentTerm.find('Temp-to-Perm') >= 0:
                    job['JobType'] = 9
                if js.has_key('DesktopSiteURL'):
                    job['SrcUrl'] = js['DesktopSiteURL']
                Benefits = ''
                for bf in jd['BenefitId']:
                    Benefits += str(bf) + ';'
                    '''
                    if bf == 5:
                        Benefits += 'Double pay;'
                    elif bf == 7:
                        Benefits += 'Free shuttle bus;'
                    elif bf == 1:
                        Benefits += 'Performance bonus;'
                    elif bf == 14:
                        Benefits += 'Dental insurance;'
                    elif bf == 4:
                        Benefits += 'Overtime pay;'
                    elif bf == 10:
                        Benefits += 'Five-day work week;'
                    elif bf == 8:
                        Benefits += 'Medical insurance;'
                    '''
                job['SSWelfare'] = Benefits
                #IsExpired = jd['IsExpired']
                #Summary1 = jd['Summary1']
                #Summary2 = jd['Summary2']
                #Summary3 = jd['Summary3']
                job['Number'] = 'one person'
                PostDate = jd['PostDate'].replace('T', ' ')
                PostDate = PostDate.replace('+08:00', '')
                PostDate = datetime.strptime(PostDate, '%Y-%m-%d %H:%M:%S')
                job['PublishTime'] = PostDate
                job['RefreshTime'] = PostDate
                job['CityName'] = 'Singapore'
                job['WorkArea'] = 'Singapore'
                Location = jd['Location'] #Downtown Core, CBD (Central Area)
                if Location <> 'No Fixed Location':
                    if Location.find(',') > 0:
                        job['WorkArea1'] = Location.split(',')[0]
                        job['WorkArea2'] = Location.split(',')[1]
                    else:
                        job['WorkArea1'] = Location
                #
                '''
                company = JobsDB_Company()
                company['WebSiteID'] = self.site_id
                company['CompanyName'] = jd['Company']
                company['Industry'] = jd['Industry']
                company['AreaName'] = 'Singapore'
                company['CompanyDesc'] = FmtSQLCharater(jd['CompanyDesc'])
                if js.has_key('CompanyLogo'):
                    company['CompanyLogoUrl'] = jd['CompanyLogo']
                #OmnitureJobAdFuncIds = js['OmnitureJobAdFuncIds'] #17|32|128|267
                #OmnitureLocationId = jd['OmnitureLocationId'] #1297
                #AdType = jd['AdType']
                yield company
                '''
                yield job
        else:
            log.msg(u'职位详情请求结果解析异常,非json数据.url=%s' % response.url, level = log.INFO)



