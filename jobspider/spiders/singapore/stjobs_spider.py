# -*- encoding=utf-8 -*-


import re
from datetime import datetime
from scrapy import Request, log
from jobspider.utils.tools import FmtSQLCharater
from jobspider.jobsdb_items import JobsDB_Job, JobsDB_Company
from jobspider.spiders.base_spider import BaseSpider


class STJobsSpider(BaseSpider):

    name = 'singapore.stjobs'

    def __init__(self, settings, category = None, *args, **kwargs):
        #依据settings初始化
        self.headers  = settings.get('STJOBS_REQUEST_HEADERS', '')
        self.base_url = settings.get('STJOBS_BASE_URL', '')
        self.list_url = settings.get('STJOBS_LIST_URL', '')
        self.info_url = settings.get('STJOBS_INFO_URL', '')
        self.site_id  = 13

    def _list_request_by_offset(self, offset):
        link_url = self.create_url(self.list_url.replace('<?offset?>', str(offset)))
        return Request(url=link_url,
                       headers=self.headers,
                       meta={'offset': offset},
                       callback=self.parse_list,
                       dont_filter=True
                       )

    def _info_request_by_jobid(self, jobid):
        link_url = self.create_url(self.info_url.replace('<?jobid?>', jobid))
        return Request(url=link_url,
                       headers=self.headers,
                       callback=self.parse_info,
                       dont_filter=True
                       )

    def start_requests(self):
        yield self._list_request_by_offset(0)

    #职位列表请求结果解析
    def parse_list(self, response):
        data = response.body
        js = BaseSpider.fmt_json(self, data)
        if js:
            #列表解析
            for item in js['jobs']:
                jobid = item['jobid']
                yield self._info_request_by_jobid(jobid)
            #下一页
            if len(js['jobs']) > 0:
                page = response.meta['offset'] + 10
                yield self._list_request_by_offset(page)
        else:
            log.msg(u'职位列表请求结果解析异常,非json数据.url=%s' % response.url, level = log.INFO)

    #职位详情请求结果解析
    def parse_info(self, response):
        data = response.body
        js = BaseSpider.fmt_json(self, data)
        if js:
            job = JobsDB_Job()
            job['SiteID'] = self.site_id
            job['LinkID'] = js['jobid']
            job['JobTitle'] = FmtSQLCharater(js['jobttl'])
            job['Company'] = FmtSQLCharater(js['coym'])
            job['JobDesc'] = FmtSQLCharater(js['dsc'])
            job['SrcUrl'] = js['applyurl']
            ovw = js['ovw']
            ovw = ovw.replace('                            ', '')
            #
            match = re.search(r"<h3 class='jd-label'>Industry</h3>\n<p>(.*)</p>", ovw, re.I|re.M)
            if match:
                job['Industry'] = match.group(1)
            #
            match = re.search(r"<h3 class='jd-label'>Job Function</h3>\n<p>(.*)</p>", ovw, re.I|re.M)
            if match:
                job['JobName'] = match.group(1)
            #
            job['CityName'] = 'Singapore'
            job['WorkArea'] = 'Singapore'
            match = re.search(r"<h3 class='jd-label'>Work Region</h3>\n<p>(.*)</p>", ovw, re.I|re.M)
            if match:
                job['WorkArea1'] = match.group(1).replace('Singapore - ', '')
            #
            match = re.search(r"<h3 class='jd-label'>Job Type</h3>\n<p>(.*)</p>", ovw, re.I|re.M)
            if match:
                if match.group(1).find('Full Time') >= 0:
                    job['JobType'] = 1
                else:
                    job['JobType'] = 0
            #
            match = re.search(r"Min. Education Level : (.*?)</li><li>", ovw, re.I|re.M)
            if match:
                job['Eduacation'] = FmtSQLCharater(match.group(1))
            #
            match = re.search(r"Year of Exp Required : (.*?)</li><li>", ovw, re.I|re.M)
            if match:
                job['Exercise'] = match.group(1)
            #
            match = re.search(r"Skills : (.*?)</li><li>", ovw, re.I|re.M)
            if match:
                job['JobComputerSkill'] = FmtSQLCharater(match.group(1))
            #
            match = re.search(r"Language : (.*?)</li><li>", ovw, re.I|re.M)
            if match:
                job['ForeignLanguage'] = match.group(1)
            #
            match = re.search(r"Salary : (.*?)</span>", ovw, re.I|re.M)
            if match:
                job['Salary'] = match.group(1)
            job['Number'] = 'one person'
            #13-Jul-2015
            PostDate = datetime.strptime(js['pstdttme'], '%d-%b-%Y')
            job['PublishTime'] = PostDate
            job['RefreshTime'] = PostDate
            #
            company = JobsDB_Company()
            company['WebSiteID'] = self.site_id
            company['CompanyName'] = job['Company']
            company['Industry'] = job['Industry']
            company['AreaName'] = 'Singapore'
            company['CompanyDesc'] = ''
            #
            match = re.search(r"Website:</strong> (.*)<br />", ovw, re.I|re.M)
            if match:
                company['CompanyUrl'] = match.group(1)
            #
            yield company
            yield job
        else:
            log.msg(u'职位详情请求结果解析异常,非json数据.url=%s' % response.url, level = log.INFO)