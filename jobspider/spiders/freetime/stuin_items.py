# -*- coding: utf-8 -*-


from scrapy import Field
from jobspider.scrapy_dao.item_dao_mysql import ItemDaoMysql


class Job(ItemDaoMysql):

    JobId = Field()
    Title = Field()
    CityId = Field()
    CityName = Field()
    CategoryId = Field()
    CategoryName = Field()
    Term = Field()
    Published = Field()
    IncludeDinner = Field()
    IncludeRoom = Field()
    IncludeCommission = Field()
    Gender = Field()
    Wage = Field()
    WageUnit = Field()
    Region = Field()
    Applies = Field()
    PeopleRequired = Field()
    Description = Field()
    Address = Field()
    Contact = Field()
    ContactPhone = Field()
    DateCreated = Field()
    CompanyName = Field()
    DateFrom = Field()
    DateExpire = Field()
    WorkFrom = Field()
    WorkEnd = Field()
    ViewTimes = Field()
    FullName = Field()
    Verified = Field()
    Deposit = Field()
    Reptile = Field()
    Sticky = Field()
    SourceWebSite = Field()
    Favorite = Field()
    Group1 = Field()
    Group2 = Field()
    Group3 = Field()
    Group4 = Field()
    Applied = Field()

    DBKey = 'GSX'
    StoreTable = 'stuin_job'
