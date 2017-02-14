# -*- coding: utf-8 -*-


import os
from datetime import datetime
from scrapy import Field
from jobspider.scrapy_dao.item_dao import ItemDao


#新加坡JobsDB存储结构定义
class JobsDB_Job(ItemDao):

    SiteID = Field()
    JobTitle = Field()
    Company = Field()
    PublishTime = Field()
    RefreshTime = Field()
    ClickTimes = Field()
    JobName = Field()
    Salary = Field()
    Eduacation = Field()
    Number = Field()
    Exercise = Field()
    SSWelfare = Field()
    SBWelfare = Field()
    OtherWelfare = Field()
    JobDesc = Field()
    Relation = Field()
    Mobile = Field()
    Email = Field()
    JobAddress = Field()
    Age = Field()
    Sex = Field()
    LinkID = Field()
    JobCode = Field()
    Require = Field()
    Tag = Field()
    ProvinceName = Field()
    CityName = Field()
    WorkArea = Field()
    WorkArea1 = Field()
    WorkArea2 = Field()
    CompanyLink = Field()
    JobType = Field()
    JobTypeName = Field()
    SyncStatus = Field()
    SrcUrl = Field()
    GisLongitude = Field()
    GisLatitude = Field()
    #
    AnFmtID = Field()
    KeyValue = Field()
    Industry = Field()
    CompanyType = Field()
    CompanyScale = Field()
    Telphone1 = Field()
    Telphone2 = Field()
    ValidDate = Field()
    ParentName = Field()
    EduacationValue = Field()
    SalaryMin = Field()
    SalaryMax = Field()
    NumberValue = Field()
    SexValue = Field()
    OperStatus = Field()
    LastModifyTime = Field()
    AreaCode = Field()
    PropertyTag = Field()
    SalaryValue = Field()
    ExerciseValue = Field()
    Valid = Field()
    JobWorkTime = Field()
    JobComputerSkill = Field()
    ForeignLanguage = Field()
    JobFunction = Field()
    SalaryType = Field()
    JobRequest = Field()
    RequirementsDesc = Field()
    ResponsibilityDesc = Field()
    #
    BusinessCode = Field()

    DBKey = 'Foreign'
    StoreTable = 'JWebJob_SyncLog'

    def __init__(self):
        super(JobsDB_Job, self).__init__()
        self['SiteID'] = 0
        self['AnFmtID'] = 0
        self['EduacationValue'] = 0
        self['SalaryMin'] = 0
        self['SalaryMax'] = 0
        self['NumberValue'] = 0
        self['JobType'] = 1
        self['ClickTimes'] = 0
        self['SalaryType'] = 0
        self['NumberValue'] = 0
        self['SexValue'] = 0
        self['OperStatus'] = 0
        self['SalaryValue'] = 0
        self['EduacationValue'] = 0
        self['SalaryValue'] = 0
        self['ExerciseValue'] = 0
        self['Valid'] = 'T'
        self['SyncStatus'] = 0
        self['GisLongitude'] = '0.00'
        self['GisLatitude'] = '0.00'
        self['LastModifyTime'] = datetime.today()

    def object2sql(self):
        command = '''if not exists(select top 1 LinkID from %s where LinkID='%s' and SiteID=%d)%s''' \
            % (self.StoreTable, self['LinkID'], self['SiteID'], os.linesep)
        command += super(JobsDB_Job, self).object2sql()
        return command

    #仅更新
    #def object2sql(self):
        return 'update %s set JobType=%d,JobTypeName=\'%s\' where LinkID=\'%s\'' % (self.StoreTable, self['JobType'], self['JobTypeName'], self['LinkID'])

class JobsDB_Company(ItemDao):

    WebSiteID = Field()
    CompanyLink = Field()
    CompanyName = Field()
    AreaName = Field()
    Relation = Field()
    Mobile = Field()
    Industry = Field()
    CompanyType = Field()
    CompanyScale = Field()
    CompanyAddress = Field()
    CompanyDesc = Field()
    CompanyUrl = Field()
    CompanyLogoUrl = Field()
    Email = Field()
    GisLongitude = Field()
    GisLatitude = Field()
    UserId = Field()
    UserName = Field()
    #增加省份与区
    ProvinceName = Field()
    WorkArea1 = Field()
    AreaCode1 = Field()
    #
    GisLongitude = Field()
    GisLatitude = Field()
    WebSite = Field()
    OtherInfo = Field()

    DBKey = 'Foreign'
    StoreTable = 'JWebCompany'

    def __init__(self):
        super(JobsDB_Company, self).__init__()
        self['WebSiteID'] = 0
        self['GisLongitude'] = '0.00'
        self['GisLatitude'] = '0.00'

    def object2sql(self):
        command = '''if not exists(select top 1 CompanyName from %s where lower(CompanyName)='%s')%s''' \
            % (self.StoreTable, self['CompanyName'].lower(), os.linesep)
        command += super(JobsDB_Company, self).object2sql()
        return command

