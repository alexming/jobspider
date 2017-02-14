# -*- encoding=utf-8 -*-
#!/usr/bin/env python


import json
import time
from jobspider.duox_items import *
from scrapy import Spider, log, Request


#分类
categorys = [
    ( 7, u'语言交流'),
    ( 8, u'美术绘画'),
    ( 9, u'乐器演奏'),
    (10, u'声乐舞蹈'),
    (11, u'模特演艺'),
    (12, u'体育运动'),
    (13, u'科学技术'),
    (14, u'亲子早教'),
    (15, u'国学书法'),
    (16, u'手工才艺'),
    (17, u'情商训练'),
    (18, u'其他')
]

class DuoXSpider(Spider):

    name = 'duox'

    def __init__(self, reqHeaders, baseUrl, schoolListUrl, schoolListParam, schoolInfoUrl, schoolInfoParam, schoolInfoUrl2,
            commentListUrl, commentListParam, courseListUrl, courseListParam, courseInfoUrl, category = None, *args, **kwargs):
        #
        super(DuoXSpider, self).__init__(*args, **kwargs)
        #
        self.reqHeaders = reqHeaders
        self.baseUrl = baseUrl
        self.schoolListUrl = schoolListUrl
        self.schoolListParam = schoolListParam
        self.schoolInfoUrl = schoolInfoUrl
        self.schoolInfoParam = schoolInfoParam
        self.schoolInfoUrl2 = schoolInfoUrl2
        self.commentListUrl = commentListUrl
        self.commentListParam = commentListParam
        self.courseListUrl = courseListUrl
        self.courseInfoUrl = courseInfoUrl
        self.courseListParam = courseListParam
        #初始分类
        self.category = 0

    @classmethod
    def from_settings(cls, settings):
        reqHeaders = settings.get('DUOX_REQUEST_HEADERS', '')
        baseUrl = settings.get('DUOX_BASEURL', '')
        schoolListUrl = settings.get('DUOX_SCHOOL_LIST_URL', '')
        schoolListParam = settings.get('DUOX_SCHOOL_LIST_PARAM', '')
        schoolInfoUrl = settings.get('DUOX_SCHOOL_INFO_URL', '')
        schoolInfoParam = settings.get('DUOX_SCHOOL_INFO_PARAM', '')
        schoolInfoUrl2 = settings.get('DUOX_SCHOOL_INFO_URL2', '')
        commentListUrl = settings.get('DUOX_COMMENT_LIST_URL', '')
        commentListParam = settings.get('DUOX_COMMENT_LIST_PARAM', '')
        courseListUrl = settings.get('DUOX_COURSE_LIST_URL', '')
        courseListParam = settings.get('DUOX_COURSE_LIST_PARAM', '')
        courseInfoUrl = settings.get('DUOX_COURSE_INFO_URL', '')
        return cls(reqHeaders, baseUrl, schoolListUrl, schoolListParam, schoolInfoUrl, schoolInfoParam, schoolInfoUrl2,
            commentListUrl, commentListParam, courseListUrl, courseListParam, courseInfoUrl)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls.from_settings(settings)

    def create_url(self, parameters):
        if parameters is None:
            return ''
        if not parameters.startswith('/'):
            return self.baseUrl + '/' + parameters
        else:
            return self.baseUrl + parameters

    #入口函数
    def start_requests(self):
        if self.category >= len(categorys):
            self.category = 0
            log.msg(u'所有分类已经抓取完成,抓取即将关闭.')
            return
        #
        page = 0
        linkURL = self.schoolListUrl
        category, name = categorys[self.category]
        self.category += 1
        linkBody = self.schoolListParam.replace('<?category?>', str(category)).replace('<?page?>', str(page))
        #
        log.msg(u'开始抓取分类[%s]的学校、课程、教师等数据' % name)
        #
        yield Request(url = self.create_url(linkURL),
            headers = self.reqHeaders,
            method='POST',
            meta={'category': category, 'name': name, 'page': page},
            body=linkBody,
            dont_filter=True,
            callback=self.parse_schools
            )

    def parse_schools(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'北京的学校列表请求结果解析异常,非json数据.url=%s' % response.url, level = log.INFO)
            return
        #列表解析
        if js.has_key('list'):
            #
            log.msg(u'学校列表:总数=%d' % (len(js['list'])))
            #
            for item in js['list']:
                school = DuoXSchool()
                school['id'] = item['id']
                school['fullName'] = item['schoolFullName']
                if item['companyName']:
                    school['companyName'] = item['companyName']
                else:
                    school['companyName'] = ''
                school['mainCourse'] = ''
                for course in eval(item['mainCourse']):
                    school['mainCourse'] += course['name'] + ';'
                school['province'] = item['provinceName']
                school['city'] = item['cityName']
                school['zone'] = item['zoneName']
                school['lng'] = item['schoolGps'].split(',')[0]
                school['lat'] = item['schoolGps'].split(',')[1]
                school['address'] = item['address']
                school['business'] = item['schoolBusiness']
                if item['contactName']:
                    school['contact'] = item['contactName']
                else:
                    school['contact'] = ''
                school['phone'] = item['contactPhone']
                school['discription'] = item['discription']
                #请求学校详情
                linkURL = self.schoolInfoUrl
                linkBody = self.schoolInfoParam.replace('<?id?>', str(school['id']))
                yield Request(url = self.create_url(linkURL),
                    headers = self.reqHeaders,
                    method='POST',
                    meta={'school': school},
                    body=linkBody,
                    dont_filter=True,
                    callback=self.parse_school,
                    errback=self.schoolErrBack
                    )
                #请求学校师资详情
                linkURL = self.schoolInfoUrl2.replace('<?id?>', str(school['id'])).replace('<?unixtime?>', str(int(time.time() * 100)))
                yield Request(url = linkURL,
                    headers = {
                        'Host': 'www.learnmore.com.cn', 'Accept': '*/*',
                        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.2.2; zh-cn; HM NOTE 1TD Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
                        'Accept-Encoding': 'gzip,deflate', 'Accept-Language': 'zh-CN, en-US'
                        },
                    method='GET',
                    meta={'id': school['id']},
                    dont_filter=True,
                    callback=self.parse_school_teacher
                    )
                #请求学校课程列表
                linkURL = self.courseListUrl
                linkBody = self.courseListParam.replace('<?id?>', str(school['id']))
                yield Request(url = self.create_url(linkURL),
                    headers = self.reqHeaders,
                    method='POST',
                    meta={'id': school['id']},
                    body=linkBody,
                    dont_filter=True,
                    callback=self.parse_courses
                    )
                #请求学校评论
                page = 1
                linkURL = self.commentListUrl
                linkBody = self.commentListParam.replace('<?id?>', str(school['id'])).replace('<?page?>', str(page))
                yield Request(url = self.create_url(linkURL),
                    headers = self.reqHeaders,
                    method='POST',
                    meta={'id': school['id'], 'name': school['fullName'], 'page': page},
                    body=linkBody,
                    dont_filter=True,
                    callback=self.parse_comments
                    )
            #下一页
            if len(js['list']) >= 20:
                category = response.meta['category']
                name = response.meta['name']
                page = response.meta['page']
                if page == 0:
                    page += 21
                else:
                    page += 20
                #
                linkURL = self.schoolListUrl
                linkBody = self.schoolListParam.replace('<?category?>', str(category)).replace('<?page?>', str(page))
                #
                log.msg(u'开始抓取分类:%s的学校列表下一页:%d' % (name, page))
                #
                yield Request(url = self.create_url(linkURL),
                    headers = self.reqHeaders,
                    method='POST',
                    meta={'category': category, 'name': name, 'page': page},
                    body=linkBody,
                    dont_filter=True,
                    callback=self.parse_schools
                    )

    #学校详情请求成功回调
    def parse_school(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        school = response.meta['school']
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'学校:%d-%s,详情请求结果解析异常,非json数据.url=%s' % (school['id'], school['fullName'], response.url), level = log.INFO)
            return
        #
        if js.has_key('dts'):
            item = js['dts']
            #品牌
            if item['schoolBrand']:
                school['brandAward'] = item['schoolBrand']['brandAward']
                school['brandHistory'] = item['schoolBrand']['brandHistory']
                school['brandSchoolCount'] = item['schoolBrand']['brandSchoolCount']
                school['brandStudentCount'] = item['schoolBrand']['brandStudentCount']
            else:
                school['brandAward'] = ''
                school['brandHistory'] = ''
                school['brandSchoolCount'] = '0'
                school['brandStudentCount'] = '0'
            #环境
            if item['schoolEnviroment']:
                school['envArea'] = item['schoolEnviroment']['envArea']
                school['envFacilities'] = item['schoolEnviroment']['envFacilities']
                school['envFitment'] = item['schoolEnviroment']['envFitment']
                school['envHealth'] = item['schoolEnviroment']['envHealth']
                school['envPantry'] = item['schoolEnviroment']['envPantry']
                school['envParentRest'] = item['schoolEnviroment']['envParentRest']
                school['envType'] = item['schoolEnviroment']['envType']
            else:
                school['envArea'] = ''
                school['envFacilities'] = ''
                school['envFitment'] = ''
                school['envHealth'] = ''
                school['envPantry'] = ''
                school['envParentRest'] = ''
                school['envType'] = ''
            #服务特色
            if item['schoolService']:
                school['serviceDetail'] = item['schoolService']['serviceDetail']
            else:
                school['serviceDetail'] = ''
            #师资
            if item['schoolTeacher']:
                school['teacherAge'] = item['schoolTeacher']['teacherAge']
                school['teacherCount'] = item['schoolTeacher']['teacherCount']
                school['teacherQualifier'] = item['schoolTeacher']['teacherQualifier']
            else:
                school['teacherAge'] = '0'
                school['teacherCount'] = '0'
                school['teacherQualifier'] = ''
            #学校图片
            school['schoolImage'] = item['schoolImage']
            #展示图片
            if item['imageTurn']:
                school['imageTurn'] = item['imageTurn']
            else:
                school['imageTurn'] = ''
            #
            log.msg(u'学校详情:名称=%s,地址=%s' % (school['fullName'], school['address']))
            yield school

    #学校详情请求失败回调
    def schoolErrBack(self, err):
        school = err.request.meta['school']
        log.msg(u'学校详情请求失败:学校=%s,将依据默认值存储' % school['fullName'])
        school['brandAward'] = ''
        school['brandHistory'] = ''
        school['brandSchoolCount'] = ''
        school['brandStudentCount'] = ''
        school['envArea'] = ''
        school['envFacilities'] = ''
        school['envFitment'] = ''
        school['envHealth'] = ''
        school['envPantry'] = ''
        school['envParentRest'] = ''
        school['envType'] = ''
        school['serviceDetail'] = ''
        school['teacherAge'] = 0
        school['teacherCount'] = 0
        school['teacherQualifier'] = ''
        school['schoolImage'] = ''
        school['imageTurn'] = ''
        yield school

    def parse_school_teacher(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'学校:%d,教师请求结果解析异常,非json数据.url=%s' % (response.meta['id'], response.url), level = log.INFO)
            return
        #列表解析
        if js.has_key('school'):
            s_id = response.meta['id']
            for item in js['school']['teachers']:
                teacher = DuoXTeacher()
                teacher['s_id'] = s_id
                teacher['id'] = item['id']
                teacher['teacherName'] = item['name']
                teacher['image'] = item['image']
                #
                log.msg(u'教师详情:学校=%s,名称=%s' % (js['school']['schoolFullName'], teacher['teacherName']))
                yield teacher

    #学校课程列表请求成功回调
    def parse_courses(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'学校:%d,课程列表请求结果解析异常,非json数据.url=%s' % (response.meta['id'], response.url), level = log.INFO)
            return
        #列表解析
        if js.has_key('list'):
            s_id = response.meta['id']
            log.msg(u'课程列表:学校id=%d, 总数=%d' % (s_id, len(js['list'])))
            for item in js['list']:
                course = DuoXCourse()
                course['s_id'] = s_id
                course['id'] = item['id']
                course['province'] = item['provinceName']
                course['city'] = item['cityName']
                course['zone'] = item['zoneName']
                course['schoolFullName'] = item['schoolFullName']
                course['courseName'] = item['courseName']
                course['lng'] = item['gps'].split(',')[0]
                course['lat'] = item['gps'].split(',')[1]
                course['typeName1'] = item['firstTypeName']
                course['typeName2'] = item['secondTypeName']
                course['ageStart'] = item['propAgeStart']
                course['ageEnd'] = item['propAgeEnd']
                course['perPrice'] = item['perPrice']
                course['packagePrice'] = item['packagePrice']
                course['needBook'] = item['needBook']
                course['studentCount'] = item['studentCount']
                course['courseImage'] = item['courseImage']
                course['discount'] = item['discount']
                #请求课程详情
                linkURL = self.courseInfoUrl.replace('<?id?>', str(course['id'])).replace('<?unixtime?>', str(int(time.time() * 1000)))
                yield Request(url = linkURL,
                    headers = {
                        'Host': 'www.learnmore.com.cn', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
                        'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                        'Cache-Control': 'max-age=0'
                        },
                    method='GET',
                    meta={'course': course},
                    dont_filter=True,
                    callback=self.parse_course_info,
                    errback=self.courseErrBack
                    )

    #学校课程详情请求成功回调
    def parse_course_info(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        course = response.meta['course']
        try:
            js = json.loads(data)
        except:
            log.msg(u'学校:%s 课程:%s 请求结果解析异常,非json数据.url=%s' % (course['schoolFullName'], course['courseName'], response.url), level = log.INFO)
            return
        #
        if js.has_key('course'):
            item = js['course']
            if item:
                if item.has_key('address'):
                    course['address'] = item['address']
                else:
                    course['address'] = ''
                course['business'] = item['business']
                course['courseDes'] = item['courseDes']
                course['imageTurn'] = item['imageTurn']
                course['priceList'] = ''
                #
                log.msg(u'课程详情:学校=%s,名称=%s' % (course['schoolFullName'], course['courseName']))
                yield course
            else:
                log.msg(u'获取学校:%s 课程:%s 请求结果异常,课程详情为空' % (course['schoolFullName'], course['courseName']))

    #学校课程详情请求失败回调
    def courseErrBack(self, err):
        req = err.request
        course = req.meta['course']
        log.msg(u'请求课程详情失败:学校=%s,名称=%s,id=%d,url=%s' % (course['schoolFullName'], course['name'], course['id'], req.url))
        #再次请求课程详情
        linkURL = self.courseInfoUrl.replace('<?id?>', str(course['id'])).replace('<?unixtime?>', str(int(time.time() * 1000)))
        yield Request(url = linkURL,
            headers = {
                'Host': 'www.learnmore.com.cn', 'Accept': '*/*',
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.2.2; zh-cn; HM NOTE 1TD Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
                'Accept-Encoding': 'gzip,deflate', 'Accept-Language': 'zh-CN, en-US', 'Accept-Charset': 'utf-8, utf-16, *;q=0.7',
                },
            method='GET',
            meta={'course': course},
            dont_filter=True,
            callback=self.parse_course_info,
            errback=self.courseErrBack
            )

    def parse_comments(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'学校:%s,评论列表请求结果解析异常,非json数据.url=%s' % (response.meta['name'], response.url), level = log.INFO)
            return
        #列表解析
        if js.has_key('comments'):
            s_id = response.meta['id']
            s_name = response.meta['name']
            #
            for item in js['comments']:
                comment = DuoXComment()
                comment['s_id'] = s_id
                comment['s_name'] = s_name
                comment['id'] = item['id']
                comment['commentText'] = item['commentText']
                comment['commentType'] = item['commentType']
                if item['contactName']:
                    comment['contactName'] = item['contactName']
                else:
                    comment['contactName'] = ''
                comment['contactPhone'] = item['contactPhone']
                comment['createTime'] = item['createTime']
                comment['typeId'] = item['typeId']
                comment['typeName'] = item['typeName']
                #
                log.msg(u'学校评论:学校=%s, 评论人=%s' % (s_name, comment['contactPhone']))
                yield comment
            #下一页
            if len(js['comments']) >= 20:
                page = response.meta['page'] + 20
                linkURL = self.commentListUrl
                linkBody = self.courseListParam.replace('<?id?>', str(s_id)).replace('<?page?>', str(page))
                log.msg(u'请求评论下一页:学校=%s,页数=%d' % (s_name, page))
                yield Request(url = self.create_url(linkURL),
                    headers = self.reqHeaders,
                    method='POST',
                    meta={'id': s_id, 'name': s_name, 'page': page},
                    body=linkBody,
                    dont_filter=True,
                    callback=self.parse_comments
                    )

