#-*-coding:utf-8-*-
#!/usr/bin/env python


import uuid
import hashlib
import logging
import re
from time import mktime
from datetime import *
from jobspider.scrapy_redis.redis_pool import TQRedis


logger = logging.getLogger("scrapy")

first_item = lambda x : x[0] if x else ''

first_text = lambda node: first_item(node.extract())

def InitLog():
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("scrapy.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.FileHandler("scrapy.err")
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    #logger.addHandler(fh)
    logger.addHandler(ch)

def md5(sourcestr):
    return hashlib.md5(sourcestr).hexdigest()

def FmtCmpNameCharacter(inStr):
    result = inStr
    result = result.replace(u' ', u'') #ASCII 32
    result = result.replace(u' ', u'') #ASCII 63
    result = result.replace(u'?', u'')
    result = result.replace(u'\u3b0c', '')
    result = result.replace(u'（', u'(')
    result = result.replace(u'）', u')')
    result = result.replace(u'‍', u'')
    return result

def FmtSQLCharater(inStr):
    if type(inStr) not in [str, unicode]:
        return inStr
    if not inStr:
        return ''
    result = inStr
    result = result.replace('\\', '\\\\')
    result = result.replace("'", "''")
    return result

#获取32位guid
def getGuid():
    guid = str(uuid.uuid1())
    return guid.replace('-', '')

# 依据关键字查找中间字符
def substring(instr, begin, end):
    idx1 = instr.find(begin)
    idx2 = instr.find(end, idx1 + len(begin))
    return instr[idx1 + len(begin): idx2]

#依据区域名称获取区域编码
#从redis获取
def FmtAreaCodeSimple(redisName, cityName):
    cityCode = ''
    if len(cityName) > 0:
        r0 = TQRedis.GetRedis(redisName)
        cityCode = r0.get('areacode.' + cityName)
        if cityCode == None:
            cityCode = ''
    return cityCode

#依据chinahr的职位编码1001_1002_1008查找线下系统的职位编码
def FmtChinahrJobCode(redisName, jobCode):
    retJobCode = ''
    if len(jobCode) > 0:
        r0 = TQRedis.GetRedis(redisName)
        retJobCode = r0.get('chinahr.jobcode.' + jobCode)
        if retJobCode == None:
            retJobCode = ''
    return retJobCode

#依据百姓网的职位编码m37318查找线下系统的职位编码
def FmtBaiXJobCode(redisName, jobCode):
    retJobCode = ''
    if len(jobCode) > 0:
        r0 = TQRedis.GetRedis(redisName)
        retJobCode = r0.get('baix.jobcode.' + jobCode)
        if retJobCode == None:
            retJobCode = ''
    return retJobCode

#看准企业评论发布时间转义
def FmtKZTime(stime):
    today = date.today()
    pos_month = stime.find('个月内')
    if pos_month > 0:
        month = int(stime[0: pos_month])
        delta = timedelta(days = 30 * month)
        return (today - delta).strftime('%Y-%m-%d')
    else:
        pos_day = stime.find('天内')
        if pos_day > 0:
            day = int(stime[0: pos_day])
            delta = timedelta(days = pos_day)
            return (today - delta).strftime('%Y-%m-%d')
        else:
            pos_year = stime.find('年')
            if pos_year > 0:
                year = stime[0: pos_year]
                year_int = 0
                if year == u'一':
                    year_int = 1
                elif year == u'二':
                    year_int = 2
                elif year == u'三':
                    year_int = 3
                elif year == u'四':
                    year_int = 4
                elif year == u'五':
                    year_int = 5
                elif year == u'六':
                    year_int = 6
                elif year == u'七':
                    year_int = 7
                elif year == u'八':
                    year_int = 8
                elif year == u'九':
                    year_int = 9
                delta = timedelta(days = year_int * 365)
                return (today - delta).strftime('%Y-%m-%d')
    return today.strftime('%Y-%m-%d')

#modify by tommy at 2015.06.01
#百城招聘网
#格式化刷新日期(2015-6-1)
#美容人才网(mr138job)
#格式化职位刷新日期(2015.05.25)
def FmtAnnounceDateToDateTime(sdate, separator = '.'):
    dtoday = datetime.today()
    year = int(dtoday.strftime('%Y'))
    month = int(dtoday.strftime('%m'))
    day = int(dtoday.strftime('%d'))
    #
    dateArray = sdate.split(separator)
    #
    if len(dateArray) == 3 and int(dateArray[0]) == year and int(dateArray[1]) == month and int(dateArray[2]) == day:
        return (dtoday, int(mktime(dtoday.timetuple())))
    else:
        try:
            dateFormater = '%Y' + separator + '%m' + separator + '%d'
            dtoday = datetime.strptime(sdate, dateFormater)
            return (dtoday, int(mktime(dtoday.timetuple())))
        except:
            return (dtoday, int(mktime(dtoday.timetuple())))

def FmtCityAreaCodeWithPrefix(redisName, prefix, cityAreaName):
    cityCode = ''
    if len(cityAreaName) > 0:
        #mr138.xx
        #baic.xx
        key = u'%s%s' % (prefix.replace('_', '.'), cityAreaName)
        r0 = TQRedis.GetRedis(redisName)
        cityCode = r0.get(key)
        if cityCode == None:
            cityCode = ''
    return cityCode

def FmtJobPositionWithPrefix(redisName, prefix, position):
    jobCode = ''
    if position > 0:
        #mr138.position.xx
        #baic.position.xx
        key = u'%sposition.%d' % (prefix.replace('_', '.'), position)
        r0 = TQRedis.GetRedis(redisName)
        jobCode = r0.get(key)
        if jobCode == None:
            jobCode = ''
    return jobCode

#去除html标签中的\r\n与空白
def clearSpecialAtHtml(html):
    return html.replace('\r\n', '').replace(' ', '').replace(u' ', ' ')

#获取指定日期零点unix时间戳
def zeroPointUnixTime(delta = 0):
    if delta < 0:
        raise "func zeroPointUnixTime's parameter delta must greater then zero."
    deltaData = date.replace(date.today() + timedelta(days = delta))
    return int(mktime(deltaData.timetuple()))
