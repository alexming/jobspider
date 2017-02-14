# -*- coding: utf-8 -*-


from scrapy import log
from jobspider.scrapy_db.db_pool import TQDbPool
from jobspider.utils.tools import FmtSQLCharater


try:
    import cPickle as pickle
except ImportError:
    import pickle


class DuoXPipeline(object):

    def process_item(self, item, spider):
        item_name = item.__class__.__name__
        commandtext = ''
        #学校
        if item_name == 'DuoXSchool':
            commandtext = '''insert ignore into duox_school(id, fullName, companyName, mainCourse, province,
city, zone, lat, lng, address, business, contact, phone, discription,
brandAward, brandHistory, brandSchoolCount, brandStudentCount,
envArea, envFacilities, envFitment, envHealth, envPantry, envParentRest, envType,
serviceDetail, teacherAge, teacherCount, teacherQualifier, schoolImage, imageTurn)
values(%s, '%s', '%s', '%s', '%s',
'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
'%s', '%s', '%s', '%s',
'%s', '%s', '%s', '%s', '%s', '%s', '%s',
'%s', '%s', '%s', '%s', '%s', '%s')''' % (item['id'], item['fullName'], item['companyName'], item['mainCourse'], item['province'],
                item['city'], item['zone'], item['lat'], item['lng'], item['address'], item['business'], item['contact'], item['phone'], FmtSQLCharater(item['discription']),
                item['brandAward'], item['brandHistory'], item['brandSchoolCount'], item['brandStudentCount'],
                item['envArea'], item['envFacilities'], item['envFitment'], item['envHealth'], item['envPantry'], item['envParentRest'], item['envType'],
                item['serviceDetail'], item['teacherAge'], item['teacherCount'], item['teacherQualifier'], item['schoolImage'], item['imageTurn'])
        #教师
        elif item_name == 'DuoXTeacher':
            commandtext = "insert ignore into duox_teacher(s_id, id, teacherName, image) values(%s, %s, '%s', '%s')" % (item['s_id'], item['id'], item['teacherName'], item['image'])
        #课程
        elif item_name == 'DuoXCourse':
            commandtext = '''insert ignore into duox_course(s_id, id, province, city, zone, schoolFullName,
courseName, lat, lng, typeName1, typeName2, ageStart, ageEnd, perPrice, packagePrice, needBook,
studentCount, courseImage, discount, address, business, courseDes, imageTurn, priceList)
values(%s, %s, '%s', '%s', '%s', '%s',
'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')''' % (item['s_id'], item['id'], item['province'], item['city'], item['zone'], item['schoolFullName'],
                FmtSQLCharater(item['courseName']), item['lat'], item['lng'], item['typeName1'], item['typeName2'], item['ageStart'], item['ageEnd'], item['perPrice'], item['packagePrice'], item['needBook'],
                item['studentCount'], item['courseImage'], item['discount'], item['address'], item['business'], FmtSQLCharater(item['courseDes']), item['imageTurn'], item['priceList'])
        #评论
        elif item_name == 'DuoXComment':
            commandtext = '''insert ignore into duox_comment(s_id, s_name, id, commentText, commentType,
contactName, contactPhone, createTime, typeId, typeName) values(%s, '%s', %d, '%s', %s,
'%s', '%s', %s, %s, '%s')''' % (item['s_id'], item['s_name'], item['id'], FmtSQLCharater(item['commentText']), item['commentType'],
                item['contactName'], item['contactPhone'], item['createTime'], item['typeId'], FmtSQLCharater(item['typeName']))
        #
        if commandtext != '':
            ret = TQDbPool.execute('GSX', commandtext)
            if ret is None:
                log.msg(u'sql指令执行失败,出现异常:dbname=%s,commamd=%s' % ('GSX', commandtext), level=log.ERROR)
            elif ret == -2:
                log.error(u'数据库连接失败导致执行失败:dbname=%s,commamd=%s' % ('GSX', commandtext), level=log.ERROR)
        return item
