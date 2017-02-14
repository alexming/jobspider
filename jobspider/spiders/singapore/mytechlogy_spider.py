# -*- encoding=utf-8 -*-

#!!!!!!该招聘网站数据来源于JobsDB,Monster等，所以不予抓取


import re
from datetime import datetime
from scrapy import Request, log, Selector
from jobspider.jobsdb_items import JobsDB_Job, JobsDB_Company
from jobspider.utils.tools import first_item, FmtSQLCharater
from jobspider.spiders.base_spider import BaseSpider


class TechlogySpider(BaseSpider):

    name = 'singapore.mytechlogy'

    def __init__(self, settings, category = None, *args, **kwargs):
        super(TechlogySpider, self).__init__(settings, *args, **kwargs)
        #依据settings初始化
        self.headers  = settings.get('MYTECHLOGY_REQUEST_HEADER', '')
        self.base_url = settings.get('MYTECHLOGY_BASE_URL', '')
        self.list_url = settings.get('MYTECHLOGY_LIST_URL', '')
        self.site_id  = 15
        #初始分类
        self.sector_index = 0

    def _list_request_by_pg(self, page):
        link_url = self.list_url.replace('<?page?>', str(page))
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
            positions = hxs.xpath('//ul[@class="article-list"]/li/article/div[@class="entry-content"]/header/h4/a')
            #下一页
            if positions and len(positions) > 0:
                page = response.meta['page'] + 1
                yield self._list_request_by_pg(page)
            #
            for item in positions:
                link_url = first_item(item.xpath('@href').extract())
                yield Request(url=link_url,
                              meta={'sector': response.meta['sector'], 'timeout': 5000},
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
            title = first_item(hxs.xpath('//h1[@class="entry-title mt_title1"]/text()').extract())
            companyname = first_item(hxs.xpath('//span[@class="entry-author"]/text()').extract())
            companyname = companyname.rstrip(' - ')
            #
            match = re.search(r'^<td.+>Location</td>\s+<td.+>(.+)</td>$', data, re.I|re.M)
            if match:
                location = match.group(1)
                if location.find(', ') > 0:
                    location = location.split(',')[0]
            else:
                location = ''
            #
            match = re.search(r'^<td.+>Posted</td>\s+<td.+>(.+)</td>$', data, re.I|re.M)
            if match:
                postdate = match.group(1)
            else:
                postdate = ''
            #
            jobdesc = first_item(hxs.xpath('//div[@class="user-page mt_content1"]/div[@class="mt_content1"]').extract())
            linkid = first_item(hxs.xpath('//input[@id="uid"]/@value').extract())
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
            job['JobName'] = response.meta['sector']
            job['JobDesc'] = FmtSQLCharater(jobdesc)
            job['Salary'] = salary
            job['JobType'] = 1
            job['SrcUrl'] = response.url
            job['Number'] = 'one person'
            #时间格式化
            if postdate == '':
                postdate = datetime.today()
            else:
                postdate = datetime.strptime(postdate, '%d %b %y')
            job['PublishTime'] = postdate
            job['RefreshTime'] = postdate
            job['CityName'] = location
            job['WorkArea'] = job['CityName']
            job['JobAddress'] = address
            job['Mobile'] = phone
            #
            company = JobsDB_Company()
            company['WebSiteID'] = self.site_id
            company['CompanyName'] = companyname
            company['CompanyAddress'] = address
            company['WebSite'] = website
            company['CompanyLogoUrl'] = logourl
            company['AreaName'] = job['CityName']
            company['Mobile'] = phone
            #
            yield company
            yield job
        else:
            log.msg(u'职位详情请求结果解析异常.url=%s' % response.url, level = log.INFO)
