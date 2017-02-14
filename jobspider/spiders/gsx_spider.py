# -*- encoding=utf-8 -*-
#!/usr/bin/env python


import json
from time import mktime, localtime, strftime, sleep
import datetime
from scrapy import Spider, log, Request, Item, Field
from jobspider.scrapy_db.db_pool import TQDbPool


#课程列表
courses = (
    #(21, u'早教'),
    (22, u'早教益智'),
    (23, u'早教潜能开发'),
    (25, u'早教亲子'),
    (26, u'早教启蒙'),
    (24, u'早教感统训练'),
    (27, u'早教才艺'),
    #(28, u'幼儿园'),
    (31, u'幼儿园语言'),
    (36, u'幼儿园数学'),
    (41, u'幼儿园英语'),
    (46, u'幼儿园艺术'),
    (51, u'幼儿园科学'),
    (56, u'幼儿园社会教育'),
    (66, u'幼儿园体育'),
    (76, u'幼儿园智能'),
    (61, u'幼儿园健康'),
    (71, u'幼儿园创意'),
    (81, u'幼儿园手工活动'),
    #(86, u'学前艺术'),
    (88, u'学前艺体'),
    (87, u'奥尔夫音乐'),
    (89, u'蒙氏教育'),
    #(90, u'幼升小'),
    (92, u'幼升小咨询'),
    (95, u'幼升小语言'),
    (96, u'幼升小数学'),
    (97, u'幼升小英语'),
    (98, u'幼升小艺术'),
    (99, u'幼升小科学'),
    (103, u'幼升小创意'),
    (91, u'幼升小择校'),
    (101, u'幼升小健康'),
    (102, u'幼升小体育'),
    (105, u'幼升小习惯养成'),
    #(108, u'小学数学'),
    (110, u'一年级数学'),
    (111, u'二年级数学'),
    (112, u'三年级数学'),
    (113, u'四年级数学'),
    (114, u'五年级数学'),
    (115, u'六年级数学'),
    #(116, u'小学语文'),
    (118, u'一年级语文'),
    (119, u'二年级语文'),
    (120, u'三年级语文'),
    (121, u'四年级语文'),
    (122, u'五年级语文'),
    (123, u'六年级语文'),
    #(124, u'小学英语'),
    (126, u'一年级英语'),
    (127, u'二年级英语'),
    (128, u'三年级英语'),
    (129, u'四年级英语'),
    (130, u'五年级英语'),
    (131, u'六年级英语'),
    #(132, u'小学奥数'),
    (134, u'一年级奥数'),
    (136, u'三年级奥数'),
    (137, u'四年级奥数'),
    (138, u'五年级奥数'),
    (139, u'六年级奥数'),
    (1119, u'小学国学'),
    (1120, u'小学国学'),
    #(1149, u'能力提升'),
    (1150, u'小学能力提升'),
    (1159, u'安全培训'),
    (1160, u'安全培训'),
    #(1161, u'财商培训'),
    (1162, u'财商培训'),
    #(1243, u'小学学习方法'),
    (1244, u'小学学习方法'),
    #(141, u'小升初数学'),
    (142, u'小升初数学'),
    #(143, u'小升初语文'),
    (144, u'小升初语文'),
    #(145, u'小升初英语'),
    (146, u'小升初英语'),
    #(147, u'小升初择校'),
    (148, u'小升初择校'),
    #(151, u'小升初咨询'),
    (152, u'小升初咨询'),
    #(149, u'小升初政策分析'),
    (150, u'小升初政策分析'),
    #(157, u'小升初特长'),
    (158, u'小升初特长')
)


class GSXSpider(Spider):

    name = 'gsx'

    def __init__(self, reqHeaders, baseUrl, teacherUrl, commentUrl, category = None, *args, **kwargs):
        super(GSXSpider, self).__init__(*args, **kwargs)
        #
        self.reqHeaders = reqHeaders
        self.baseUrl = baseUrl
        self.teacherUrl = teacherUrl
        self.commentUrl = commentUrl

    @classmethod
    def from_settings(cls, settings):
        reqHeaders = settings.get('GSX_REQUEST_HEADERS', '')
        baseUrl = settings.get('GSX_BASEURL', '')
        teacherUrl = settings.get('GSX_TEACHER', '')
        commentUrl = settings.get('GSX_COMMENT', '')
        return cls(reqHeaders, baseUrl, teacherUrl, commentUrl)

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

    #获取种子请求
    def get_requests_mysql(self):
        rows = TQDbPool.query('GSX', 'select * from gsx_city order by last_time limit 10')
        if rows is None:
            sleep(1)
            self.get_requests_mysql()
        else:
            return rows

    #更新种子请求状态
    def update_start_requests_mysql(self, ids):
        TQDbPool.execute('GSX', 'update gsx_city set last_time=UNIX_TIMESTAMP() where city_id in (%s)' % ','.join(ids))

    #入口函数
    def start_requests(self):
        ids = []
        rows = self.get_requests_mysql()
        if rows:
            for row in rows:
                ids.append(str(row['city_id']))
            #批次更新LastTime
            if len(ids) > 0:
                self.update_start_requests_mysql(ids)
            #
            for row in rows:
                for course, name in courses:
                    linkURL = self.teacherUrl.replace('<?city_id?>', str(row['city_id'])).replace('<?course?>', str(course)).replace('<?page?>', '1')
                    yield Request(url = self.create_url(linkURL),
                        meta = {'use_proxy': False, 'city_id': row['city_id'], 'city_name': row['city_name'], 'course': course, 'course_name': name, 'page': 1},
                        headers = self.reqHeaders,
                        method='GET',
                        dont_filter=True,
                        callback=self.parse_tearchers
                        )

    #教师解析
    def parse_tearchers(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'城市:%s, 课程:%s 的教师列表请求结果解析异常,非json数据.url=%s' % (response.meta['city_name'], response.meta['course_name'], response.url), level = log.INFO)
            return
        #列表解析
        if js['code'] == 1:
            #
            log.msg(u'城市:%s, 课程:%s 的教师列表请求ok' % (response.meta['city_name'], response.meta['course_name']), level = log.INFO)
            if js['result'] and js['result']['teacher_list']:
                city_id = response.meta['city_id']
                city_name = response.meta['city_name']
                course = response.meta['course']
                course_name = response.meta['course_name']
                #
                for teacher in js['result']['teacher_list']:
                    if teacher['comment_count'] > 0:
                        teacher_id = teacher['number']
                        teacher_name = teacher['name']
                        #
                        linkURL = self.commentUrl.replace('<?teacher_id?>', str(teacher_id)).replace('<?page?>', '1')
                        yield Request(self.create_url(linkURL), callback=self.parse_comments, method='GET',
                                     headers=self.reqHeaders,
                                     meta={'use_proxy': False, 'teacher_id': teacher_id, 'teacher_name': teacher_name, 'city_name': city_name, 'course_name': course_name, 'page': 1},
                                     encoding='utf-8',
                                     dont_filter=True
                                     )
                #下一页
                if js['result']['has_more'] == 1:
                    nextPage = js['result']['next_cursor']
                    #
                    linkURL = self.teacherUrl.replace('<?city_id?>', str(city_id)).replace('<?course?>', str(course)).replace('<?page?>', str(nextPage))
                    yield Request(url = self.create_url(linkURL),
                        meta = {'use_proxy': False, 'city_id': city_id, 'city_name': city_name, 'course': course, 'course_name': course_name, 'page': nextPage},
                        headers = self.reqHeaders,
                        method='GET',
                        dont_filter=True,
                        callback=self.parse_tearchers
                        )
        else:
            log.msg(u'城市:%s, 课程:%s 的教师列表请求失败,原因:%s' % (response.meta['city_name'], response.meta['course_name'], js['message']))

    #评论解析
    def parse_comments(self, response):
        data = response.body
        if data == '' or data == '[]':
            log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
            return
        #
        teacher_id = response.meta['teacher_id']
        teacher_name = response.meta['teacher_name']
        course_name = response.meta['course_name']
        city_name = response.meta['city_name']
        js = json.loads('{}')
        try:
            js = json.loads(data)
        except:
            log.msg(u'城市:%s, 课程:%s, 教师:%s 评论请求结果解析异常,非json数据.url=%s' % (city_name, course_name, teacher_name, response.url), level = log.INFO)
            return
        if js['code'] == 1:
            log.msg(u'城市:%s, 课程:%s, 教师:%s 评论请求ok' % (city_name, course_name, teacher_name), level = log.INFO)
            if js['result'] and js['result']['list']:
                for cc in js['result']['list']:
                    #存储
                    comment = GSXComment()
                    comment['c_id'] = cc['id']
                    comment['info'] = cc['info']
                    comment['c_time'] = cc['create_time']
                    comment['user_name'] = cc['user']['realname']
                    comment['mobile'] = cc['user']['mobile']
                    comment['city_name'] = city_name
                    comment['course_name'] = course_name
                    comment['teacher_name'] = teacher_name
                    yield comment
                    #yield存储
                #下一页
                if js['result']['has_more'] == 1:
                    nextPage = js['result']['next_cursor']
                    #
                    linkURL = self.commentUrl.replace('<?teacher_id?>', str(teacher_id)).replace('<?page?>', str(nextPage))
                    yield Request(self.create_url(linkURL), callback=self.parse_comments, method='GET',
                                  headers=self.reqHeaders,
                                  meta={'use_proxy': False, 'teacher_id': teacher_id, 'teacher_name': teacher_name, 'city_name': city_name, 'course_name': course_name, 'page': nextPage},
                                  encoding='utf-8',
                                  dont_filter=True
                                  )
        else:
            log.msg(u'城市:%s, 课程:%s, 教师:%s 评论请求结果失败,原因:%s' % (city_name, course_name, teacher_name, js['message']))

#定义存储结构
class GSXComment(Item):
    c_id = Field()
    info = Field()
    c_time = Field()
    user_name = Field()
    mobile = Field()
    city_name = Field()
    course_name = Field()
    teacher_name = Field()

