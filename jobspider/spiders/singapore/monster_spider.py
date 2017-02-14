# -*- encoding=utf-8 -*-


import re
from datetime import datetime
from scrapy import Request, log, Selector
from jobspider.jobsdb_items import JobsDB_Job, JobsDB_Company
from jobspider.utils.tools import first_item, FmtSQLCharater
from jobspider.spiders.base_spider import BaseSpider


class MonsterSpider(BaseSpider):

    name = 'singapore.monster'

    def __init__(self, settings, category = None, *args, **kwargs):
        super(MonsterSpider, self).__init__(settings, *args, **kwargs)
        #依据settings初始化
        self.headers  = settings.get('MONSTER_REQUEST_HEADER', '')
        self.base_url = settings.get('MONSTER_BASE_URL', '')
        self.list_url = settings.get('MONSTER_LIST_URL', '')
        self.site_id  = 16

    def _list_request_by_pg(self, page):
        link_url = self.list_url.replace('<?n?>', str(page))
        log.msg(u'开始抓取第[%d]页列表...' % page)
        return Request(url=self.create_url(link_url),
                       headers=self.headers,
                       meta={'page': page, 'timeout': 5000},
                       callback=self.parse_list,
                       dont_filter=True,
                       #errback=self._requestErrorBack
                       )

        #异常http请求回调
    def _requestErrorBack(self, error):
        log.msg(u'error.请求异常,原因:%s,内容:%s' % (error.value.message, error.value.request.url), level = log.ERROR)

    #抓取入口
    def start_requests(self):
        yield self._list_request_by_pg(1)

    #职位列表请求结果解析
    def parse_list(self, response):
        if response.status == 200:
            hxs = Selector(response)
            positions = hxs.xpath('//div[@class="ns_job_wrapper"]/div[@class="ns_lt ns_jobdetails"]/a[@class="ns_joblink"]')
            #下一页
            if positions and len(positions) > 0:
                page = response.meta['page'] + 1
                yield self._list_request_by_pg(page)
            #
            for item in positions:
                link_url = first_item(item.xpath('@href').extract())
                yield Request(url=link_url,
                              meta={'timeout': 5000},
                              callback=self.parse_info,
                              dont_filter=True,
                              #errback=self._requestErrorBack
                             )
        else:
            log.msg(u'职位列表请求结果解析异常.url=%s' % response.url, level = log.INFO)

    #职位详情请求结果解析
    def parse_info(self, response):
        if response.status == 200:
            data = response.body
            hxs = Selector(response)
            #开始解析
            match = re.search(r"^var foldr = '(.+)';", data, re.I|re.M)
            if match:
                linkid = match.group(1)
            else:
                linkid = ''
            if linkid == '':
                log.msg(u'页面没有找到职位ID，丢弃。%s' % response.url, log.ERROR)
                return
            else:
                log.msg(u'找到职位，ID=[%s]' % linkid)
            #
            title = first_item(hxs.xpath('//div[@class="ns_jd_headingbig hl"]/h1/strong/text()').extract())
            title = title.rstrip(' ')
            logourl = first_item(hxs.xpath('//div[@class="ns_jd_comp_logo"]/img/@src').extract())
            companyname = first_item(hxs.xpath('//span[@class="ns_comp_name"]/text()').extract())
            #Locations
            match = re.search(r'<strong>Locations</strong></h2></div>\s+<div class="ns_jobsum_txt">(.+)\s</div>', data, re.I|re.M)
            if match:
                location = match.group(1)
            else:
                location = ''
            #Experience
            match = re.search(r'<strong>Experience </strong></h2></div>\s+<div class="ns_jobsum_txt">(.+)\s</div>', data, re.I|re.M)
            if match:
                experience = match.group(1)
            else:
                experience = ''
            #Keywords / Skills
            match = re.search(r'<strong>Keywords / Skills </strong></h2></div>\s+<div class="ns_jobsum_txt"\s.+>(.+)\s</div>', data, re.I|re.M)
            if match:
                skills = match.group(1)
            else:
                skills = ''
            #Education
            match = re.search(r'<strong>Education </strong></h2></div>\s+<div class="ns_jobsum_txt">(.+)\s</div>', data, re.I|re.M)
            if match:
                education = match.group(1)
            else:
                education = ''
            #Function
            match = re.search(r'<strong>Function </strong></h2></div>\s+<div class="ns_jobsum_txt">(.+)\s</div>', data, re.I|re.M)
            if match:
                function = match.group(1)
                function = function.replace(' &bull; ', '*')
                function = function.replace('<br />', '')
            else:
                function = ''
            #Role
            match = re.search(r'<strong>Role </strong></h2></div>\s+<div class="ns_jobsum_txt">(.+)\s</div>', data, re.I|re.M)
            if match:
                role = match.group(1)
                role = role.replace(' &bull; ', '*')
                role = role.replace('<br />', '')
            else:
                role = ''
            #Industry
            match = re.search(r'<strong>Industry </strong></h2></div>\s+<div class="ns_jobsum_txt">(.+)\s</div>', data, re.I|re.M)
            if match:
                industry = match.group(1)
                industry = industry.replace(' &bull; ', '')
                industry = industry.replace('<br />', ';')
            else:
                industry = ''
            #Summary
            match = re.search(r'<strong>Summary </strong></h2></div>\s+<div class="ns_jobsum_txt">(.+)</div>', data, re.I|re.M)
            if match:
                summary = match.group(1)
            else:
                #存在中途换行的情况
                match = re.search(r'<strong>Summary </strong></h2></div>\s+<div class="ns_jobsum_txt">(.+\s+.+)</div>', data, re.I|re.M)
                if match:
                    summary = match.group(1)
                else:
                    summary = ''
            #
            match = re.search(r'<strong>Posted On </strong></h2></div>\s+<div class="ns_jobsum_txt">\s(.+)\s</div>\t', data, re.I|re.M)
            if match:
                postdate = match.group(1)
            else:
                postdate = ''
            #
            desc = hxs.xpath('//div[@class="ns_jobdesc hl"]').extract()
            if desc:
                jobdesc = hxs.xpath('//div[@class="ns_jobdesc hl"]').extract()[0]
            else:
                jobdesc = ''
            #
            if desc and len(desc) > 1:
                comdesc = hxs.xpath('//div[@class="ns_jobdesc hl"]').extract()[1]
            else:
                comdesc = ''
            #
            title = FmtSQLCharater(title)
            companyname = FmtSQLCharater(companyname)
            location = FmtSQLCharater(location)
            #
            job = JobsDB_Job()
            job['SiteID'] = self.site_id
            job['LinkID'] = linkid
            job['JobTitle'] = title
            job['Company'] = companyname
            job['JobName'] = function
            job['JobDesc'] = FmtSQLCharater(summary + '<p>' + jobdesc)
            job['JobType'] = 1
            job['SrcUrl'] = response.url
            job['Number'] = 'one person'
            #时间格式化
            if postdate == '':
                postdate = datetime.today()
            else:
                postdate = postdate.replace('st', '')
                postdate = postdate.replace('nd', '')
                postdate = postdate.replace('rd', '')
                postdate = postdate.replace('th', '')
                postdate = datetime.strptime(postdate, '%d %b %Y')
            job['PublishTime'] = postdate
            job['RefreshTime'] = postdate
            job['CityName'] = location
            job['WorkArea'] = job['CityName']
            job['JobComputerSkill'] = skills
            job['Exercise'] = experience
            job['Eduacation'] = education
            job['JobFunction'] = role
            job['Industry'] = industry
            #
            company = JobsDB_Company()
            company['WebSiteID'] = self.site_id
            company['CompanyName'] = companyname
            company['Industry'] = industry
            company['CompanyLogoUrl'] = logourl
            company['CompanyDesc'] = FmtSQLCharater(comdesc)
            company['AreaName'] = job['CityName']
            #
            yield company
            yield job
        else:
            log.msg(u'职位详情请求结果解析异常.url=%s' % response.url, level = log.INFO)
