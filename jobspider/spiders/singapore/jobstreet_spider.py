# -*- encoding=utf-8 -*-


import re
from datetime import datetime
from scrapy import Request, log, Selector
from jobspider.jobsdb_items import JobsDB_Job, JobsDB_Company
from jobspider.utils.tools import first_item, FmtSQLCharater
from jobspider.spiders.base_spider import BaseSpider


#职位类别
specializations = [
    ('130', 'Audit & Taxation'),
    ('135', 'Banking/Financial'),
    ('132', 'Corporate Finance/Investment'),
    ('131', 'General/Cost Accounting'),
    ('133', 'Clerical/Administrative'),
    ('137', 'Human Resources'),
    ('146', 'Secretarial'),
    ('148', 'Top Management'),
    ('100', 'Advertising'),
    ('101', 'Arts/Creative Design'),
    ('106', 'Entertainment'),
    ('141', 'Public Relations'),
    ('180', 'Architect/Interior Design'),
    ('184', 'Civil Engineering/Construction'),
    ('150', 'Property/Real Estate'),
    ('198', 'Quantity Surveying'),
    ('192', 'IT - Hardware'),
    ('193', 'IT - Network/Sys/DB Admin'),
    ('191', 'IT - Software'),
    ('105', 'Education'),
    ('121', 'Training & Dev.'),
    ('185', 'Chemical Engineering'),
    ('187', 'Electrical Engineering'),
    ('186', 'Electronics Engineering'),
    ('189', 'Environmental Engineering'),
    ('200', 'Industrial Engineering'),
    ('195', 'Mechanical/Automotive Engineering'),
    ('190', 'Oil/Gas Engineering'),
    ('188', 'Other Engineering'),
    ('113', 'Doctor/Diagnosis'),
    ('112', 'Pharmacy'),
    ('111', 'Nurse/Medical Support'),
    ('107', 'Food/Beverage/Restaurant'),
    ('114', 'Hotel/Tourism'),
    ('115', 'Maintenance'),
    ('194', 'Manufacturing'),
    ('196', 'Process Design & Control'),
    ('140', 'Purchasing/Material Mgmt'),
    ('197', 'Quality Assurance'),
    ('142', 'Sales - Corporate'),
    ('139', 'Marketing/Business Dev'),
    ('149', 'Merchandising'),
    ('145', 'Retail Sales'),
    ('143', 'Sales - Eng/Tech/IT'),
    ('144', 'Sales - Financial Services'),
    ('151', 'Telesales/Telemarketing'),
    ('103', 'Actuarial/Statistics'),
    ('102', 'Agriculture'),
    ('181', 'Aviation'),
    ('182', 'Biotechnology'),
    ('183', 'Chemistry'),
    ('108', 'Food Tech/Nutritionist'),
    ('109', 'Geology/Geophysics'),
    ('199', 'Science & Technology'),
    ('119', 'Security/Armed Forces'),
    ('134', 'Customer Service'),
    ('147', 'Logistics/Supply Chain'),
    ('138', 'Law/Legal Services'),
    ('118', 'Personal Care'),
    ('120', 'Social Services'),
    ('152', 'Tech & Helpdesk Support'),
    ('110', 'General Work'),
    ('104', 'Journalist/Editors'),
    ('117', 'Publishing'),
    ('116', 'Others')
]


class JobStreetSpider(BaseSpider):

    name = 'singapore.jobstreet'

    def __init__(self, settings, category = None, *args, **kwargs):
        #依据settings初始化
        self.headers  = settings.get('JOBSTREET_REQUEST_HEADERS', '')
        self.list_url = settings.get('JOBSTREET_LIST_URL', '')
        self.site_id  = 13
        #初始分类
        self.special = 0

    def _list_request_by_pg(self, id, name, pg):
        link_url = self.list_url.replace('<?specialization?>', id).replace('<?pg?>', str(pg))
        log.msg(u'开始抓取职位类别[%s]的第[%d]页列表...' % (name, pg))
        return Request(url=link_url,
                       headers=self.headers,
                       meta={'pg': pg, 'id': id, 'name': name, 'timeout': 5000},
                       callback=self.parse_list,
                       dont_filter=True,
                       errback=self.requestErrorBack
                       )

    #抓取入口
    def start_requests(self):
        if self.special >= len(specializations):
            self.special = 0
            log.msg(u'所有职位分类已经抓取完成,抓取即将关闭.')
            return
        #
        id, name = specializations[self.special]
        self.special += 1
        yield self._list_request_by_pg(id, name, 1)

    #职位列表请求结果解析
    def parse_list(self, response):
        if response.status == 200:
            hxs = Selector(response)
            positions = hxs.xpath('//h4[@class="position-title "]/a[@class="position-title-link"]')
            #下一页
            if positions and len(positions) > 0:
                pg = response.meta['pg'] + 1
                yield self._list_request_by_pg(response.meta['id'], response.meta['name'], pg)
            #
            for item in positions:
                link_url = first_item(item.xpath('@href').extract())
                yield Request(url=link_url,
                              meta={'name': response.meta['name'], 'timeout': 5000},
                              callback=self.parse_info,
                              dont_filter=True,
                              errback=self.requestErrorBack
                             )
        else:
            log.msg(u'职位列表请求结果解析异常.url=%s' % response.url, level = log.INFO)

    #职位详情请求结果解析
    def parse_info(self, response):
        if response.status == 200:
            data = response.body
            hxs = Selector(response)
            #页面解析
            #企业横幅
            company_banner = first_item(hxs.xpath('//img[@id="company_banner"]/@data-original').extract())
            #企业logo
            company_logo = first_item(hxs.xpath('//img[@id="company_logo"]/@data-original').extract())
            #职位名称
            position_title = first_item(hxs.xpath('//h1[@id="position_title"]/text()').extract())
            position_title = FmtSQLCharater(position_title)
            #企业名称
            company_name = first_item(hxs.xpath('//h2[@id="company_name"]/a/text()').extract())
            if company_name == '':
                company_name = first_item(hxs.xpath('//h2[@id="company_name"]/text()').extract())
            company_name = company_name.replace('\n', '')
            company_name = company_name.replace('\t', '')
            company_name = company_name.lstrip(' ')
            company_name = company_name.rstrip(' ')
            company_name = FmtSQLCharater(company_name)
            if company_name == '':
                log.msg(u'企业名称为空，url=%s' % response.url)
                return
            #企业SrcUrl地址
            company_url = first_item(hxs.xpath('//h2[@id="company_name"]/a/@href').extract())
            #薪资
            salary = first_item(hxs.xpath('//div[@id="salary"]/p/a/text()').extract())
            #经验
            experience = first_item(hxs.xpath('//div[@id="experience"]/p[@id="years_of_experience"]/span[@id="years_of_experience"]/text()').extract())
            experience = experience.replace('\n', '')
            experience = experience.replace('\t', '')
            #Location
            location = first_item(hxs.xpath('//div[@id="location"]/p/span[@id="single_work_location"]/text()').extract())
            location = location.replace('\n', '')
            location = location.replace('\t', '')
            #职位描述(可能包含岗位职责、职位要求)
            job_desc = first_item(hxs.xpath('//div[@id="job_description"]').extract())
            #企业信息
            company_registration_number = first_item(hxs.xpath('//span[@id="company_registration_number"]/text()').extract())
            company_industry = first_item(hxs.xpath('//p[@id="company_industry"]/text()').extract())
            company_website = first_item(hxs.xpath('//a[@id="company_website"]/text()').extract())
            company_contact = first_item(hxs.xpath('//p[@id="company_contact"]/text()').extract())
            company_size = first_item(hxs.xpath('//p[@id="company_size"]/text()').extract())
            work_environment_working_hours = first_item(hxs.xpath('//p[@id="work_environment_working_hours"]/text()').extract())
            work_environment_dress_code = first_item(hxs.xpath('//p[@id="work_environment_dress_code"]/text()').extract())
            work_environment_benefits = first_item(hxs.xpath('//p[@id="work_environment_benefits"]/text()').extract())
            work_environment_spoken_language = first_item(hxs.xpath('//p[@id="work_environment_spoken_language"]/text()').extract())
            #gallery
            gallery = ''
            thumbs = hxs.xpath('//ul[@class="gallery-thumb"]/li')
            for item in thumbs:
                gallery += first_item(item.xpath('img/@data-original').extract()) + ';'
            #企业描述
            company_overview_all = first_item(hxs.xpath('//div[@id="company_overview_all"]').extract())
            #work location
            match = re.search(r'&center=(.*?)&', data, re.I|re.M)
            if match:
                gps_location = match.group(1)
                lat = gps_location.split(',')[0]
                lng = gps_location.split(',')[1]
            else:
                lat = '0.0'
                lng = '0.0'
            #
            address = first_item(hxs.xpath('//p[@id="address"]/text()').extract())
            address = FmtSQLCharater(address)
            #Advertised: 23-June-2015
            posting_date = first_item(hxs.xpath('//p[@id="posting_date"]/text()').extract())
            posting_date = posting_date.replace('Advertised:', '')
            posting_date = posting_date.replace(' ', '')
            #
            job = JobsDB_Job()
            job['SiteID'] = self.site_id
            #http://jobs.jobstreet.com/sg/jobs/4712859?fr=J
            job['LinkID'] = response.url[34: -5]
            job['JobTitle'] = position_title
            job['Company'] = company_name
            job['Industry'] = company_industry
            job['JobName'] = response.meta['name']
            job['JobDesc'] = FmtSQLCharater(job_desc)
            job['Salary'] = salary
            job['Exercise'] = experience
            job['JobType'] = 1
            job['SrcUrl'] = response.url
            job['SSWelfare'] = work_environment_benefits
            job['Number'] = 'one person'
            #时间格式化
            PostDate = datetime.strptime(posting_date, '%d-%B-%Y')
            job['PublishTime'] = PostDate
            job['RefreshTime'] = PostDate
            if location <> '' and len(location.split('-')) > 1:
                job['CityName'] = location.split('-')[0].replace(' ', '')
                job['WorkArea1'] = location.split('-')[1].replace(' ', '')
            else:
                job['CityName'] = location
            job['WorkArea'] = job['CityName']
            job['ForeignLanguage'] = work_environment_spoken_language
            job['JobWorkTime'] = work_environment_working_hours
            job['GisLongitude'] = lng
            job['GisLatitude'] = lat
            job['JobAddress'] = address
            job['Mobile'] = company_contact
            #
            company = JobsDB_Company()
            company['WebSiteID'] = self.site_id
            company['CompanyName'] = company_name
            company['Industry'] = company_industry
            company['CompanyScale'] = company_size
            company['CompanyAddress'] = address
            company['CompanyUrl'] = company_url
            company['WebSite'] = company_website
            company['CompanyLogoUrl'] = company_logo
            company['AreaName'] = job['CityName']
            company['CompanyDesc'] = FmtSQLCharater(company_overview_all)
            company['Mobile'] = company_contact
            company['GisLongitude'] = lng
            company['GisLatitude'] = lat
            company['OtherInfo'] = company_banner + '#' + gallery
            #
            yield company
            yield job
        else:
            log.msg(u'职位详情请求结果解析异常.url=%s' % response.url, level = log.INFO)
