# -*- encoding=utf-8 -*-
#!/usr/bin/env python

# Define your spiders


import json
from time import localtime, strftime
from scrapy import Spider, log, Request, FormRequest
from jobspider.items import *
from jobspider.scrapy_requests.start_requests import *
from jobspider.utils.tools import *
from jobspider.utils.ganji_des import GanJiDES


PAGE_SIZE = 30

class GanJiSpider(Spider):

    name = "ganji"
    #下载延时
    download_delay = 0.1

    def __init__(self, jsonArgs, pageSize, reqHeaders, cmpComment, category = None, *args, **kwargs):
        super(GanJiSpider, self).__init__(*args, **kwargs)
        self.jsonArgs = jsonArgs
        self.pageSize = pageSize
        self.reqHeaders = reqHeaders
        self.cmpComment = cmpComment
        self.groupAtIndex = 0

    @classmethod
    def from_settings(cls, settings):
        jsonArgs = settings.get('JSON_ARGS', '')
        pageSize = settings.get('PAGE_SIZE', PAGE_SIZE)
        reqHeaders = settings.get('GANJI_REQUEST_HEADERS', '')
        cmpComment = settings.get('GANJI_COMMENT', '')
        return cls(jsonArgs, pageSize, reqHeaders, cmpComment)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls.from_settings(settings)

    #入口函数
    def start_requests(self):
        ids = []
        categoryId = 0
        rows = get_requests_mongo(4, self.groupAtIndex)
        if rows:
            for row in rows:
                ids.append(row['_id'])
                #时间戳
                publishTime = 0
                if row.has_key('PublishTime'):
                    publishTime = row['PublishTime']
                jzPublishTime = 0
                if row.has_key('JZPublishTime'):
                    jzPublishTime = row['JZPublishTime']
                #form表单数据
                formdata = {}
                formdata['showtype'] = '0'
                formdata['showType'] = '0'
                #全职
                categoryId = 2
                formdata['jsonArgs'] = self.jsonArgs % {'categoryId': categoryId, 'cityId': int(row['CityId']), 'pageIndex': 0, 'pageSize': self.pageSize}
                cityName = row['CityName']
                yield FormRequest(url= 'http://mobapi.ganji.com/datashare/',
                    headers = dict({'interface': 'SearchPostsByJson2'}, **self.reqHeaders),
                    formdata = formdata,
                    meta = {'_id': row['_id'], 'CityId': int(row['CityId']), 'CityName': cityName, 'PublishTime': publishTime, 'PageIndex': 0},
                    dont_filter = True,
                    callback = self.parse_job_lst)
                '''
                #兼职
                categoryId = 3
                formdata['jsonArgs'] = self.jsonArgs % {'categoryId': categoryId, 'cityId': int(row['CityId']), 'pageIndex': 0, 'pageSize': self.pageSize}
                cityName = row['CityName']
                yield FormRequest(url= 'http://mobapi.ganji.com/datashare/',
                    headers = dict({'interface': 'SearchPostsByJson2'}, **self.reqHeaders),
                    formdata = formdata,
                    meta = {'_id': row['_id'], 'CityId': int(row['CityId']), 'CityName': cityName, 'PublishTime': jzPublishTime, 'PageIndex': 0},
                    dont_filter = True,
                    callback = self.parse_job_lst)
                '''
            #批次更新LastTime
            if len(ids) > 0:
                update_start_requests('CityIndex', ids)

    #职位列表解析函数
    def parse_job_lst(self, response):
        if response.body == '' and response.body == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(response.body)
        except:
            return
        #列表解析
        #
        first_update = False
        if response.meta.has_key('FirstUpdate'):
            first_update = response.meta['FirstUpdate']
        firstPublishTime = 0
        _id = response.meta['_id']
        if response.meta.has_key('FirstPublishTime'):
            firstPublishTime = response.meta['FirstPublishTime']
        #职位总量
        total = js['total']
        PublishTime = response.meta['PublishTime']
        log.msg(u'CityName=%s,pageIndex=%d,pageSize=%d' % (response.meta['CityName'], response.meta['PageIndex'], len(js['posts'])), level=log.INFO)
        CategoryId = 0
        for AJob in js['posts']:
            #职位分类(全职／兼职)
            CategoryId = AJob['CategoryId']
            if not CategoryId in (2, 3):
                continue
            #刷新时间戳判别
            #过滤热门职位
            if AJob['icons']['hot'] == '0':
                #过滤置顶职位
                if AJob['icons']['ding'] == '0':
                    nowPublishTime = int(AJob['postunixtime'])
                    if firstPublishTime == 0:
                        firstPublishTime = nowPublishTime
                    if nowPublishTime <= PublishTime:
                        #本次最大发布时间<=上次抓取时间，直接退出
                        return
                    elif (not first_update) and (not response.meta.has_key('FirstUpdate') or not response.meta['FirstUpdate']):
                        first_update = True
                        #全职
                        if CategoryId == 2:
                            update_publishtime('CityIndex', _id, firstPublishTime, 'PublishTime')
                        elif CategoryId == 3:
                            update_publishtime('CityIndex', _id, firstPublishTime, 'JZPublishTime')
                        str_t0 = strftime('%Y-%m-%d %H:%M:%S', localtime(PublishTime))
                        str_t1 = strftime('%Y-%m-%d %H:%M:%S', localtime(firstPublishTime))
                        log.msg(u'%d.CityName= %s 换词，发布日期:%s->%s' % (CategoryId, response.meta['CityName'], str_t0, str_t1), level = log.INFO)

            #没有企业信息的数据直接丢弃
            if not AJob.has_key('CompanyNameText'):
                continue
            #
            #0407,由于存在本页与上一页职位存在重复内容(新增职位会导致页数变动),需要进行职位去重(依据职位linkID,postunixtime去重)
            LinkID = AJob['puid']
            postUnixTime = int(AJob['postunixtime'])
            if exist_linkid(4, LinkID, postUnixTime):
                continue
            #
            webJob = WebJob()
            webJob['SiteID'] = 4
            jobTitle = AJob['title']
            webJob['JobTitle'] = FmtSQLCharater(jobTitle)
            #去除特殊符号\u200d
            webJob['Company'] = FmtCmpNameCharacter(AJob['CompanyNameText'])
            postTime = datetime.fromtimestamp(postUnixTime)
            webJob['PublishTime'] = postTime
            webJob['RefreshTime'] = postTime
            #依据url从redis中获取
            # webJob['JobName'] = AJob['url']
            # webJob['JobCode'] = AJob['url']
            #职位分类
            if CategoryId == 2:
                webJob['JobType'] = 1
                webJob['SalaryType'] = 0
                webJob['Salary'] = AJob['price']['t']
            elif CategoryId == 3:
                webJob['JobType'] = 2
                #1=小时 2=天 3=周 4=月
                webJob['SalaryType'] = int(AJob['price_unit'])
                webJob['Salary'] = AJob['price']['v']
            webJob['Eduacation'] = AJob['degree']['t']
            webJob['Number'] = AJob['need_num']
            webJob['Exercise'] = AJob['work_years']['t']
            webJob['SSWelfare'] = ''
            webJob['SBWelfare'] = ''
            webJob['OtherWelfare'] = ''
            if AJob.has_key('welfare') and AJob['welfare'] != []:
                if AJob['welfare'].has_key('insurance'):
                    webJob['SSWelfare'] = AJob['welfare']['insurance']
                if AJob['welfare'].has_key('room'):
                    webJob['SBWelfare'] = AJob['welfare']['room']
                if AJob['welfare'].has_key('other'):
                    webJob['OtherWelfare'] = AJob['welfare']['other']
            webJob['Relation'] = AJob['person']
            #联系电话解密
            webJob['Mobile'] = GanJiDES().decrypt(AJob['phone'])
            webJob['InsertTime'] = datetime.today()
            webJob['Email'] = AJob['email']
            if CategoryId == 2:
                jobAddr = AJob['work_address']
            elif CategoryId == 3:
                jobAddr = AJob['CompanyAddress']
            webJob['JobAddress'] = FmtSQLCharater(jobAddr)
            webJob['Sex'] = AJob['sex']['t']
            webJob['LinkID'] = LinkID
            webJob['Tag'] = AJob['tag']
            webJob['Require'] = u'招%s人|学历%s|经验%s|性别%s' % (webJob['Number'], webJob['Eduacation'], webJob['Exercise'], webJob['Sex'])
            #去除城市最后的'市'
            CityName = AJob['city']
            if CityName[-1: ] == u'市':
                CityName = CityName[0: -1]
            webJob['CityName'] = CityName
            webJob['WorkArea'] = CityName
            webJob['WorkArea1'] = AJob['district_name']
            webJob['WorkArea2'] = AJob['street_name']
            webJob['AreaCode'] = FmtAreaCodeSimple('remote_252_1', CityName)
            webJob['CompanyLink'] = 'ganjic_' + AJob['company_id']
            webJob['SyncStatus'] = 0
            #替换\符号
            webJob['SrcUrl'] = AJob['detail_url'].replace('\\', '')
            webJob['GisLongitude'] = '0'
            webJob['GisLatitude'] = '0'
            if AJob.has_key('latlng'):
                if len(AJob['latlng'].split(',')) == 2:
                    webJob['GisLongitude'] = AJob['latlng'].split(',')[1]
                    webJob['GisLatitude'] = AJob['latlng'].split(',')[0]
            #企业认证信息
            yan = 0
            fangxin = 0
            if 'yan' in AJob['icons']:
                if AJob['icons']['yan'] == '1':
                    yan = 1
            if 'tianlv' in AJob['icons']:
                if AJob['icons']['tianlv'] == '1':
                    fangxin = 1
            #职位详情
            formdata = {'d_sign': AJob['d_sign']}
            yield FormRequest(url= 'http://mobapi.ganji.com/datashare/',
                headers = dict({'interface': 'GetPostByPuid', 'puid': AJob['puid']}, **self.reqHeaders),
                formdata = formdata,
                meta = {'WebJob': webJob, 'credibility': AJob['credibility'], 'yan': yan, 'fangxin': fangxin,
                    'CompanyLatLng': AJob['CompanyLatLng'], 'UserId': AJob['user_id']},
                callback = self.parse_job_detail,
                dont_filter = True
                )
        #下页处理
        if len(js['posts']) > 0:
            cityId = response.meta['CityId']
            cityName = response.meta['CityName']
            pageIndex = response.meta['PageIndex'] + 1
            formdata = {}
            formdata['showtype'] = '0'
            formdata['showType'] = '0'
            formdata['jsonArgs'] = self.jsonArgs % {'categoryId': CategoryId, 'cityId': cityId, 'pageIndex': pageIndex, 'pageSize': self.pageSize}
            yield FormRequest(url= 'http://mobapi.ganji.com/datashare/',
                headers = dict({'interface': 'SearchPostsByJson2'}, **self.reqHeaders),
                formdata = formdata,
                meta = {'_id': _id, 'CityId': cityId, 'CityName': cityName, 'PublishTime': PublishTime,
                    'PageIndex': pageIndex, 'FirstPublishTime': firstPublishTime, 'FirstUpdate': first_update},
                dont_filter = True,
                callback = self.parse_job_lst)

    #职位详情解析
    def parse_job_detail(self, response):
        if response.body == '' and response.body == '[]':
            log.msg(format= '%jobDetail.(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(response.body)
        except:
            return
        if js['status'] == 0:
            jsData = js['data']
            #更新职位描述
            webJob = response.meta['WebJob']
            jobDesc = jsData['description']
            jobDesc = jobDesc.replace('\\', '\\\\')
            jobDesc = jobDesc.replace("'", "''")
            webJob['JobDesc'] = jobDesc
            webJob['ClickTimes'] = jsData['view_times']
            #如果职位没有联系号码,则取企业联系号码
            if webJob['Mobile'] == '':
                webJob['Mobile'] = jsData['commentOwnerInfo']['phone']
            #其他默认信息
            webJob['AnFmtID'] = 0
            webJob['KeyValue'] = ''
            webJob['Industry'] = jsData['CompanyBizTypeText']
            webJob['CompanyType'] = jsData['CompanyTypeText']
            webJob['CompanyScale'] = jsData['CompanyScaleText']
            webJob['ProvinceName'] = ''
            webJob['Telphone1'] = ''
            webJob['Telphone2'] = ''
            webJob['Age'] = 0
            webJob['ValidDate'] = ''
            webJob['ParentName'] = ''
            webJob['EduacationValue'] = 0
            webJob['SalaryMin'] = 0.0
            webJob['SalaryMax'] = 0.0
            webJob['NumberValue'] = 0
            webJob['SexValue'] = 0
            webJob['OperStatus'] = 0
            webJob['LastModifyTime'] = datetime.today()
            webJob['PropertyTag'] = ''
            webJob['SalaryValue'] = 0
            webJob['ExerciseValue'] = 0
            webJob['Valid'] = 'T'
            webJob['JobWorkTime'] = ''
            webJob['JobComputerSkill'] = ''
            webJob['ForeignLanguage'] = ''
            webJob['JobFunction'] = ''
            webJob['JobRequest'] = ''
            webJob['StartDate'] = ''
            webJob['EndDate'] = ''
            webJob['BusinessCode'] = ''
            #
            SrcUrl = webJob['SrcUrl']
            citydomain = substring(SrcUrl, 'domain=', '&url=')
            jobnamepy = substring(SrcUrl, '&url=', '&puid')
            jobpuid = substring(SrcUrl, '&puid=', '&from=')
            NewSrcUrl = 'http://{}.ganji.com/{}/{}x.htm'.format(citydomain,jobnamepy,jobpuid)
            #加入企业信息
            cmp = Company()
            cmp['SiteID'] = 4
            cmp['company_id'] = webJob['CompanyLink']
            cmp['Credibility'] = int(response.meta['credibility'])
            cmp['Licensed'] = jsData['company_licensed']
            cmp['Yan'] = response.meta['yan']
            cmp['FangXin'] = response.meta['fangxin']
            cmp['CompanyName'] = FmtCmpNameCharacter(jsData['CompanyNameText'])
            cmp['CityName'] = webJob['CityName']
            cmp['AreaCode'] = webJob['AreaCode']
            cmp['Industry'] = jsData['CompanyBizTypeText']
            cmp['CompanyType'] = jsData['CompanyTypeText']
            cmp['CompanyScale'] = jsData['CompanyScaleText']
            cmpAddr = jsData['CompanyAddress']
            cmp['CompanyAddress'] = FmtSQLCharater(cmpAddr)
            cmpRel = jsData['commentOwnerInfo']['userName']
            cmp['Relation'] = FmtSQLCharater(cmpRel)
            cmp['Mobile'] = jsData['commentOwnerInfo']['phone']
            cmpDesc = jsData['CompanyDescription']
            if cmpDesc == None:
                cmpDesc = ''
            cmp['CompanyDesc'] = FmtSQLCharater(cmpDesc)
            cmp['Email'] = ''
            cmp['CompanyUrl'] = ''
            cmp['CompanyLogoUrl'] = ''
            cmp['PraiseRate'] = jsData['commentOwnerInfo']['praiseRate']
            cmp['GisLongitude'] = '0'
            cmp['GisLatitude'] = '0'
            if response.meta['CompanyLatLng'] is not None:
                if len(response.meta['CompanyLatLng'].split(',')) > 1:
                    cmp['GisLongitude'] = response.meta['CompanyLatLng'].split(',')[1]
                    cmp['GisLatitude'] = response.meta['CompanyLatLng'].split(',')[0]
                    if cmp['GisLatitude'][0: 1] == 'b':
                        cmp['GisLatitude'] = cmp['GisLatitude'][1:]
                    #经纬度判别，兼容经纬度交换问题 modify by tangm at 201504281125
                    #Zh-CN 纬度应该小于经度
                    if float(cmp['GisLatitude']) > float(cmp['GisLongitude']):
                        temporaryGis = cmp['GisLongitude']
                        cmp['GisLongitude'] = cmp['GisLatitude']
                        cmp['GisLatitude'] = temporaryGis
            #
            cmp['UserId'] = response.meta['UserId']
            cmp['UserName'] = jsData['username']
            cmp['ProvinceName'] = ''
            cmp['WorkArea1'] = ''
            cmp['AreaCode1'] = ''
            #
            yield cmp
            yield Request(url = NewSrcUrl, meta = {'WebJob': webJob}, dont_filter = True, callback=self.parse_job_type)
            #企业评论数>0则抓取评论
            #不需要抓取评论 20160317 liu
            """
            if jsData['commentOwnerInfo']['commentNum']['total'] > 0:
                yield Request(url = self.cmpComment % {'company_id': jsData['company_id']},
                    meta = {'CompanyName': cmp['CompanyName'], 'AreaCode': webJob['AreaCode']},
                    dont_filter = True,
                    callback = self.parse_cmp_comment)
            """
        else:
            log.msg(format= 'jobDetail.%(request)s post fail.errMessage:%(errMessage)s,errDetail=%(errDetail)s.',
                level = log.ERROR, request = response.url, errMessage = js['errMessage'], errDetail = js['errDetail'])

    # 依据职位详情获取职位分类
    def parse_job_type(self, response):
        webJob = response.meta['WebJob']
        gc = first_item(response.xpath('//li[@class="fl"]/em/a[@class="nolink"]/@href').extract())
        if gc != '':
            webJob['JobName'] = gc.split('/')[1]
            webJob['JobCode'] = webJob['JobName']
            yield webJob

    #企业评论解析
    def parse_cmp_comment(self, response):
        for review in response.xpath("//div[@class='review-lists']"):
            com = Comment()
            com['SiteID'] = 4
            com['CompanyName'] = response.meta['CompanyName']
            com['AreaCode'] = response.meta['AreaCode']
            review_title = review.xpath("div/div[@class='review-tt h-tile']")
            com['Title'] = first_item(review_title.xpath("div[@class='review-title m-title']/text()").extract())
            if com['Title'] == None:
                com['Title'] = ''
            com['Time'] = first_item(review_title.xpath("div[@class='review-time']/text()").extract())
            review_content = review.xpath("div/div[@class='review-body']/div[@class='review-content']")
            com['Type'] = first_item(review_content.xpath('p/text()').extract())
            if com['Type'] == u'好评':
                com['TotalScore'] = 4
            elif com['Type'] == u'中评':
                com['TotalScore'] = 3
            elif com['Type'] == u'差评':
                com['TotalScore'] = 2
            else:
                com['TotalScore'] = 3
            content = first_item(review_content.xpath('text()[2]').extract())
            content = content.replace("\n\t\t\t\t   \t  \t  ", '')
            content = content.replace("\t\t\t\t   \t  ", '')
            content = content.replace('\\', '\\\\')
            content = content.replace("'", "''")
            com['Content'] = content
            com['SrcUrl'] = response.url
            yield com
