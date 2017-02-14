# -*- encoding=utf-8 -*-


import re
from datetime import datetime
from scrapy import Request, log, Selector
from jobspider.jobsdb_items import JobsDB_Job, JobsDB_Company
from jobspider.utils.tools import first_item, FmtSQLCharater
from jobspider.spiders.base_spider import BaseSpider


#职位类别
filters = [
    'Analyst',
    'Project+Manager',
    'Sales+Executive',
    'Assistant+Manager',
    'Senior+Manager',
    'Sales+Manager',
    'Technician',
    'Account+Executive',
    'Business+Analyst',
    'Accountant',
    'Developer',
    'Software+Engineer',
    'Senior+Executive',
    'Vice+President',
    'Supervisor',
]

class RecruitSpider(BaseSpider):

    name = 'singapore.recruit'

    def __init__(self, settings, category = None, *args, **kwargs):
        super(RecruitSpider, self).__init__(settings, *args, **kwargs)
        #依据settings初始化
        self.headers  = settings.get('RECRUIT_REQUEST_HEADER', '')
        self.base_url = settings.get('RECRUIT_BASE_URL', '')
        self.list_url = settings.get('RECRUIT_LIST_URL', '')
        self.site_id  = 17
        #初始分类
        self.filter_index = 0

    def _list_request_by_pg(self, f, page):
        link_url = self.list_url.replace('<?filter?>', f).replace('<?page?>', str(page))
        log.msg(u'开始抓取职位类别[%s]的第[%d]页列表...' % (f, page))
        return Request(url=self.create_url(link_url),
                       headers=self.headers,
                       meta={'f': f, 'page': page, 'timeout': 10000},
                       callback=self.parse_list,
                       dont_filter=True,
                       #errback=self._requestErrorBack
                       )

        #异常http请求回调
    def _requestErrorBack(self, error):
        log.msg(u'error.请求异常,原因:%s' % error.value.message, level = log.ERROR)

    #抓取入口
    def start_requests(self):
        if self.filter_index >= len(filters):
            self.filter_index = 0
            log.msg(u'所有职位分类已经抓取完成,抓取即将关闭.')
            return
        #
        afilter = filters[self.filter_index]
        self.filter_index += 1
        yield self._list_request_by_pg(afilter, 1)

    #职位列表请求结果解析
    def parse_list(self, response):
        if response.status == 200:
            hxs = Selector(response)
            positions = hxs.xpath('//div[@class="main-job"]/div')
            #职位类别
            f = response.meta['f']
            #下一页
            if positions and len(positions) > 0:
                page = response.meta['page'] + 1
                yield self._list_request_by_pg(f, page)
            #
            for item in positions:
                logourl = first_item(item.xpath('div[@class="mobile-comp-logo"]/div[@class="comp-logo-frame"]/img/@src').extract())
                linkid = first_item(item.xpath('div[@class="job organic"]/@id').extract())
                title = first_item(item.xpath('div[@class="job organic"]/h2[@itemprop="title"]/a/@title').extract())
                link_url = first_item(item.xpath('div[@class="job organic"]/h2[@itemprop="title"]/a/@href').extract())
                link_url = link_url.replace('\r', '')
                link_url = link_url.replace('\n', '')
                link_url = link_url.replace('\t', '')
                location = first_item(item.xpath('div[@class="job organic"]/div[@class="main-content"]/h3/span[@itemprop="jobLocation"]/span[@class="location"]/span/text()').extract())
                postdate = first_item(item.xpath('div[@class="job organic"]/div[@class="main-content"]/div[@class="time"]/@content').extract())
                yield Request(url=link_url,
                              meta=
                                {
                                'f': f,
                                'logourl': logourl,
                                'linkid': linkid,
                                'title': title,
                                'location': location,
                                'postdate': postdate,
                                'timeout': 10000
                                },
                              callback=self.parse_info,
                              dont_filter=True,
                              errback=self._requestErrorBack
                             )
        else:
            log.msg(u'职位列表请求结果解析异常.url=%s' % response.url, level = log.INFO)

    #职位详情请求结果解析
    def parse_info(self, response):
        if response.status == 200:
            data = response.body
            hxs = Selector(None, data)
            #开始解析
            linkid = response.meta['linkid']
            #
            title = response.meta['title']
            #
            logourl = response.meta['logourl']
            #
            location = response.meta['location']
            #
            function = response.meta['f']
            #
            postdate = response.meta['postdate']
            #
            companyname = first_item(hxs.xpath('//div[@class="additional_info"]/span[@class="company"]/a/text()').extract())
            companyname = companyname.lstrip(' ')
            companyname = companyname.rstrip(' ')
            if companyname == '':
                log.msg(u'该职位来源其他网站(%s),无法抓取.' % response.url, level=log.ERROR)
                return
            #
            desc = first_item(hxs.xpath('//div[@class="p-description"]').extract())
            desc = desc.lstrip('<div class="p-description">')
            desc = desc.rstrip('</div>')
            desc = desc.replace('\t', '')
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
            job['JobDesc'] = FmtSQLCharater(desc)
            job['JobType'] = 1
            job['SrcUrl'] = response.url
            job['Number'] = 'one person'
            #时间格式化
            if postdate == '':
                postdate = datetime.today()
            else:
                postdate = datetime.strptime(postdate, '%Y-%m-%d')
            job['PublishTime'] = postdate
            job['RefreshTime'] = postdate
            job['CityName'] = location
            job['WorkArea'] = job['CityName']
            #
            company = JobsDB_Company()
            company['WebSiteID'] = self.site_id
            company['CompanyName'] = companyname
            company['CompanyLogoUrl'] = logourl
            company['AreaName'] = job['CityName']
            #
            yield company
            yield job
        else:
            log.msg(u'职位详情请求结果解析异常.url=%s' % response.url, level = log.INFO)
