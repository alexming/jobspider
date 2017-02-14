# -*- encoding=utf-8 -*-


import re
from datetime import datetime
from scrapy import Request, log, Selector
from jobspider.jobsdb_items import JobsDB_Job, JobsDB_Company
from jobspider.utils.tools import first_item, FmtSQLCharater
from jobspider.spiders.base_spider import BaseSpider


#职位类别
sectors = [
    'ACCOUNTING_FINANCE__AUDIT',
    'ACCOUNTING_FINANCE__FD_CFO',
    'ACCOUNTING_FINANCE__FINANCIAL_ADVISORY_SERVICES',
    'ACCOUNTING_FINANCE__FINANCIAL_CONTROL',
    'ACCOUNTING_FINANCE__FINANCIAL_MGMT_ACCOUNTING',
    'ACCOUNTING_FINANCE__FUND_ADMINISTRATION',
    'ACCOUNTING_FINANCE__NEWLY_PART_QUALIFIED',
    'ACCOUNTING_FINANCE__OTHER',
    'ACCOUNTING_FINANCE__PRACTICE',
    'ACCOUNTING_FINANCE__PRODUCT_CONTROL',
    'ACCOUNTING_FINANCE__REGULATORY_REPORTING',
    'ACCOUNTING_FINANCE__TAX',
    'ACCOUNTING_FINANCE__TREASURY',
    'ACCOUNTING_FINANCE__VALUATIONS',
    'ASSET_MANAGEMENT__ANALYST',
    'ASSET_MANAGEMENT__CIO',
    'ASSET_MANAGEMENT__DEALER',
    'ASSET_MANAGEMENT__INVESTMENT_WRITER',
    'ASSET_MANAGEMENT__OTHER',
    'ASSET_MANAGEMENT__PORTFOLIO_MANAGER',
    'ASSET_MANAGEMENT__PRODUCT_MANAGER',
    'ASSET_MANAGEMENT__SALES_CLIENT_SERVICES',
    'ASSET_MANAGEMENT__STRATEGIST_ECONOMIST',
    'CAPITAL_MARKETS__DOCUMENTATION_STRUCTURING',
    'CAPITAL_MARKETS__EXECUTION',
    'CAPITAL_MARKETS__ORIGINATION',
    'CAPITAL_MARKETS__OTHER',
    'CAPITAL_MARKETS__SECURITISATION',
    'CAPITAL_MARKETS__SYNDICATION',
    'COMMODITIES__ENERGY',
    'COMMODITIES__OTHER',
    'COMMODITIES__RESEARCH',
    'COMMODITIES__SALES',
    'COMMODITIES__TRADING',
    'COMPLIANCE_LEGAL__COMPLIANCE_REGULATORY',
    'COMPLIANCE_LEGAL__IN_HOUSE_LEGAL',
    'COMPLIANCE_LEGAL__OTHER',
    'CONSULTANCY',
    'CORPORATE_BANKING__ACQUISITION_FINANCE',
    'CORPORATE_BANKING__ASSET_FINANCE_LEASING',
    'CORPORATE_BANKING__LEVERAGED_FINANCE',
    'CORPORATE_BANKING__LOANS_SYNDICATION',
    'CORPORATE_BANKING__OTHER',
    'CORPORATE_BANKING__PROJECT_FINANCE_PFI',
    'CORPORATE_BANKING__RELATIONSHIP_MANAGEMENT',
    'CORPORATE_BANKING__STRUCTURED_TAX_FINANCE',
    'CORPORATE_BANKING__TRADE_FINANCE',
    'CORPORATE_BANKING__TRANSACTION_BANKING',
    'CREDIT',
    'DEBT_FIXED_INCOME__OTHER',
    'DEBT_FIXED_INCOME__RESEARCH',
    'DEBT_FIXED_INCOME__SALES',
    'DEBT_FIXED_INCOME__SALES_TRADING',
    'DEBT_FIXED_INCOME__TRADING',
    'DERIVATIVES__OTHER',
    'DERIVATIVES__RESEARCH',
    'DERIVATIVES__SALES_MARKETING',
    'DERIVATIVES__STRUCTURING',
    'DERIVATIVES__TRADING',
    'EQUITIES__OTHER',
    'EQUITIES__RESEARCH',
    'EQUITIES__SALES',
    'EQUITIES__SALES_TRADING',
    'EQUITIES__TRADING',
    'FX_MONEY_MARKETS__OTHER',
    'FX_MONEY_MARKETS__RESEARCH',
    'FX_MONEY_MARKETS__SALES',
    'FX_MONEY_MARKETS__SALES_TRADING',
    'FX_MONEY_MARKETS__TRADING',
    'GLOBAL_CUSTODY__CLIENT_SERVICES',
    'GLOBAL_CUSTODY__OTHER',
    'GLOBAL_CUSTODY__PRODUCT_DEVELOPMENT_MANAGEMENT',
    'GLOBAL_CUSTODY__RELATIONSHIP_MANAGEMENT',
    'GLOBAL_CUSTODY__SALES_MARKETING',
    'GLOBAL_CUSTODY__SETTLEMENTS',
    'GRADUATES_INTERNSHIPS__GRADUATE_TRAINEE',
    'GRADUATES_INTERNSHIPS__INTERNSHIPS',
    'GRADUATES_INTERNSHIPS__OTHER',
    'HEDGE_FUNDS__FINANCE_OPERATIONS',
    'HEDGE_FUNDS__IT_QUANT',
    'HEDGE_FUNDS__OTHER',
    'HEDGE_FUNDS__PORTFOLIO_MANAGER',
    'HEDGE_FUNDS__PRIME_BROKERAGE',
    'HEDGE_FUNDS__RESEARCH_ANALYSIS',
    'HEDGE_FUNDS__RISK_MANAGEMENT',
    'HEDGE_FUNDS__SALES_MARKETING',
    'HEDGE_FUNDS__STRUCTURING',
    'HEDGE_FUNDS__TRADING',
    'HR_RECRUITMENT__COMPENSATION_BENEFITS',
    'HR_RECRUITMENT__HR_GENERALIST',
    'HR_RECRUITMENT__OTHER',
    'HR_RECRUITMENT__RECRUITMENT',
    'HR_RECRUITMENT__RESEARCH',
    'HR_RECRUITMENT__TRAINING_DEVELOPMENT',
    'INDUSTRY_COMMERCE',
    'INFORMATION_SERVICES',
    'INFORMATION_TECHNOLOGY__DEVELOPMENT',
    'INFORMATION_TECHNOLOGY__OTHER',
    'INFORMATION_TECHNOLOGY__PROJECT_MANAGEMENT',
    'INFORMATION_TECHNOLOGY__SALES_MARKETING',
    'INFORMATION_TECHNOLOGY__STRATEGY_BUSINESS_ANALYST',
    'INFORMATION_TECHNOLOGY__SYSTEM_ADMINISTRATION_SUPPORT',
    'INSURANCE__ACTUARIAL',
    'INSURANCE__BROKER',
    'INSURANCE__CLAIMS',
    'INSURANCE__INVESTMENT',
    'INSURANCE__OTHER',
    'INSURANCE__SALES',
    'INSURANCE__UNDERWRITING',
    'INVESTMENT_BANKING_M_A__M_A_CORPORATE_FINANCE',
    'INVESTMENT_BANKING_M_A__ORIGINATION',
    'INVESTMENT_CONSULTING',
    'INVESTOR_RELATIONS_PR__COMMUNICATIONS_PR',
    'INVESTOR_RELATIONS_PR__INVESTOR_RELATIONS',
    'INVESTOR_RELATIONS_PR__OTHER',
    'ISLAMIC_FINANCE',
    'OPERATIONS__DOCUMENTATION',
    'OPERATIONS__OTHER',
    'OPERATIONS__RECONCILIATION',
    'OPERATIONS__SETTLEMENTS',
    'OPERATIONS__TRADE_SUPPORT',
    'PRIVATE_BANKING_WEALTH_MANAGEMENT__CLIENT_RELATIONS',
    'PRIVATE_BANKING_WEALTH_MANAGEMENT__FINANCIAL_PLANNING',
    'PRIVATE_BANKING_WEALTH_MANAGEMENT__INFRASTRUCTURE',
    'PRIVATE_BANKING_WEALTH_MANAGEMENT__PORTFOLIO_MANAGEMENT',
    'PRIVATE_BANKING_WEALTH_MANAGEMENT__PRIVATE_CLIENT',
    'PRIVATE_BANKING_WEALTH_MANAGEMENT__PRODUCT_SPECIALISATION',
    'PRIVATE_BANKING_WEALTH_MANAGEMENT__SUPERANNUATION',
    'PRIVATE_EQUITY_VENTURE_CAPITAL',
    'PUBLIC_SECTOR',
    'QUANTITATIVE_ANALYTICS__COMMODITIES',
    'QUANTITATIVE_ANALYTICS__CREDIT',
    'QUANTITATIVE_ANALYTICS__EQUITY',
    'QUANTITATIVE_ANALYTICS__FX',
    'QUANTITATIVE_ANALYTICS__INTEREST_RATES',
    'QUANTITATIVE_ANALYTICS__OTHER',
    'REAL_ESTATE',
    'RESEARCH',
    'RETAIL_BANKING__BRANCH_AND_RETAIL_SERVICES',
    'RETAIL_BANKING__BUSINESS_BANKING',
    'RETAIL_BANKING__CALL_CENTERS_AND_CUSTORMER_SERVICES',
    'RETAIL_BANKING__DEPOSITS_AND_SAVINGS',
    'RETAIL_BANKING__INSURANCE_AND_INVESTMENT',
    'RETAIL_BANKING__LOANS_AN_CREDIT',
    'RETAIL_BANKING__RELATIONSHIP_MANAGEMENT',
    'RISK_MANAGEMENT__COUNTRY',
    'RISK_MANAGEMENT__CREDIT',
    'RISK_MANAGEMENT__MARKET',
    'RISK_MANAGEMENT__OPERATIONAL',
    'RISK_MANAGEMENT__OTHER',
    'SALES_MARKETING',
    'TRADING',
]


class EFinancialSpider(BaseSpider):

    name = 'singapore.efinancial'

    def __init__(self, settings, category = None, *args, **kwargs):
        super(EFinancialSpider, self).__init__(settings, *args, **kwargs)
        #依据settings初始化
        self.headers  = settings.get('FINANCE_REQUEST_HEADER', '')
        self.base_url = settings.get('FINANCE_BASE_URL', '')
        self.list_url = settings.get('FINANCE_LIST_URL', '')
        self.site_id  = 14
        #初始分类
        self.sector_index = 0

    def _list_request_by_pg(self, sector, page):
        link_url = self.list_url.replace('<?sector?>', sector).replace('<?page?>', str(page))
        log.msg(u'开始抓取职位类别[%s]的第[%d]页列表...' % (sector, page))
        return Request(url=self.create_url(link_url),
                       headers=self.headers,
                       meta={'page': page, 'sector': sector, 'timeout': 5000},
                       callback=self.parse_list,
                       dont_filter=True,
                       #errback=self._requestErrorBack
                       )

        #异常http请求回调
    def _requestErrorBack(self, error):
        log.msg(u'error.请求异常,原因:%s,内容:%s' % (error.value.message, error.value.request.url), level = log.ERROR)

    #抓取入口
    def start_requests(self):
        if self.sector_index >= len(sectors):
            self.sector_index = 0
            log.msg(u'所有职位分类已经抓取完成,抓取即将关闭.')
            return
        #
        sector = sectors[self.sector_index]
        self.sector_index += 1
        yield self._list_request_by_pg(sector, 1)

    #职位列表请求结果解析
    def parse_list(self, response):
        if response.status == 200:
            hxs = Selector(response)
            positions = hxs.xpath('//h3/a')
            #下一页
            if positions and len(positions) > 0:
                page = response.meta['page'] + 1
                yield self._list_request_by_pg(response.meta['sector'], page)
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
            title = first_item(hxs.xpath('//h1[@itemprop="title"]/text()').extract())
            salary = first_item(hxs.xpath('//span[@itemprop="baseSalary"]/text()').extract())
            location = first_item(hxs.xpath('//span[@itemprop="address"]/text()').extract())
            jobtype = first_item(hxs.xpath('//span[@itemprop="employmentType"]/text()').extract())
            companyname = first_item(hxs.xpath('//span[@itemprop="name"]/text()').extract())
            postdate = first_item(hxs.xpath('//span[@itemprop="datePosted"]/text()').extract())
            jobdesc = first_item(hxs.xpath('//section[@class="description"]/div[@class="well"]').extract())
            logourl = first_item(hxs.xpath('//section[@class="brandInfo"]/div[@class="well"]/h2/img/@src').extract())
            if logourl != '':
                logourl = self.create_url(logourl)
            #
            match = re.search(r'<label>Contact:</label>\s*(.+)</li>', data, re.I|re.M)
            if match:
                contact = match.group(1)
            else:
                contact = ''
            #
            match = re.search(r'<label>Address:</label>\s*(.+)</li>', data, re.I|re.M)
            if match:
                address = match.group(1)
            else:
                address = ''
            #
            match = re.search(r'<label>Phone:</label>\s*(.+)</li>', data, re.I|re.M)
            if match:
                phone = match.group(1)
            else:
                phone = ''
            #
            match = re.search(r'<label>Email:</label>\s*(.+)</li>', data, re.I|re.M)
            if match:
                email = match.group(1)
            else:
                email = ''
            #
            match = re.search(r'<label>Website:</label>\s*<a href="(.+)" ', data, re.I|re.M)
            if match:
                website = match.group(1)
            else:
                website = ''
            title = FmtSQLCharater(title)
            companyname = FmtSQLCharater(companyname)
            location = FmtSQLCharater(location)
            address = FmtSQLCharater(address)
            #
            job = JobsDB_Job()
            job['SiteID'] = self.site_id
            match = re.search(r'\.id(.+)\?', response.url, re.I|re.M)
            if match:
                job['LinkID'] = str(int(match.group(1)))
            job['JobTitle'] = title
            job['Company'] = companyname
            job['JobName'] = response.meta['sector']
            job['JobDesc'] = FmtSQLCharater(jobdesc)
            job['Salary'] = salary
            if jobtype.find('Full time') > 0:
                job['JobType'] = 1
            else:
                job['JobType'] = 0
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












