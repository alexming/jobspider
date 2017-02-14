# -*- coding: utf-8 -*-


import scrapy


#企业信息
class Salary(scrapy.Item):
    company_code = scrapy.Field()
    company_name = scrapy.Field()
    company_logo = scrapy.Field()
    praise_rate = scrapy.Field()
    job_name = scrapy.Field()
    #工资条数量
    job_count = scrapy.Field()
    low = scrapy.Field()
    high = scrapy.Field()
    average = scrapy.Field()
    #靠谱数
    mark = scrapy.Field()
    src_url = scrapy.Field()
    company_url = scrapy.Field()
    comment_url = scrapy.Field()
