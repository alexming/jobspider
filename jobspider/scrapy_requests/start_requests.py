# -*- encoding=utf-8 -*-

import datetime
import traceback
import json
from scrapy import log
from jobspider.scrapy_mongo.Q_mongo import *
from jobspider.scrapy_redis.redis_pool import TQRedis

try:
    import cPickle as pickle
except ImportError:
    import pickle


#site_id=(4,5,7,10)
def get_requests_mongo(site_id, groupAtIndex):
    m0 = TQMongo.getDb('remote_238')
    d0 = datetime.datetime.today()
    d2 = d0 - datetime.timedelta(minutes = 2)
    t2 = {'$and': [{'LastTime': {'$lte': d2}}, {'Priority': {'$lte': 13}}]}
    d3 = d0 - datetime.timedelta(minutes = 6)
    t3 = {'$and': [{'LastTime': {'$lte': d3}}, {'$and': [{'Priority': {'$gte': 14}}, {'Priority': {'$lte': 26}}]}]}
    d4 = d0 - datetime.timedelta(minutes = 10)
    t4 = {'$and': [{'LastTime': {'$lte': d4}}, {'$and': [{'Priority': {'$gte': 27}}, {'Priority': {'$lte': 39}}]}]}
    d5 = d0 - datetime.timedelta(minutes = 20)
    t5 = {'$and': [{'LastTime': {'$lte': d5}}, {'$and': [{'Priority': {'$gte': 40}}, {'Priority': {'$lte': 63}}]}]}
    d6 = d0 - datetime.timedelta(minutes = 30)
    t6 = {'$and': [{'LastTime': {'$lte': d6}}, {'Priority': {'$gte': 64}}]}
    try:
        return m0['CityIndex'].find({'SiteID': site_id, '$or': [t2, t3, t4, t5, t6], 'Index': groupAtIndex}).limit(10)
    except Exception, e:
        log.msg(format= u'从mongo获取起始url异常.cause=%(cause)s', level = log.ERROR, cause = str(e))
        traceback.print_exc()
        m0.connection.close()

def get_request_mongo_for_wuyao():
    m0 = TQMongo.getDb('remote_238')
    d0 = datetime.datetime.today()
    t1 = {'LastTime': {'$exists': False}}
    d2 = d0 - datetime.timedelta(minutes = 2)
    t2 = {'$and': [{'LastTime': {'$lte': d2}}]}
    d3 = d0 - datetime.timedelta(minutes = 6)
    t3 = {'$and': [{'LastTime': {'$lte': d3}}]}
    d4 = d0 - datetime.timedelta(minutes = 10)
    t4 = {'$and': [{'LastTime': {'$lte': d4}}]}
    d5 = d0 - datetime.timedelta(minutes = 20)
    t5 = {'$and': [{'LastTime': {'$lte': d5}}]}
    d6 = d0 - datetime.timedelta(minutes = 30)
    t6 = {'$and': [{'LastTime': {'$lte': d6}}]}
    try:
        return m0['FuncIndex'].find({'$or': [t1, t2, t3, t4, t5, t6]}).limit(10)
    except Exception, e:
        log.msg(format= u'从mongo获取起始url异常.cause=%(cause)s', level = log.ERROR, cause = str(e))
        traceback.print_exc()
        m0.connection.close()    

def update_start_requests(collection, ids):
    if ids == []:
        return
    m0 = TQMongo.getDb('remote_238')
    d0 = datetime.datetime.today()
    try:
        m0[collection].update({'_id': {'$in': ids}}, {'$set': {'LastTime': d0}}, multi = True)
    except Exception, e:
        log.msg(format= u'更新mongo的起始url的LastTime异常.cause=%(cause)s', level = log.ERROR, cause = str(e))
        traceback.print_exc()
        m0.connection.close()

def update_publishtime(collection, id, postunixtime, fieldName):
    m0 = TQMongo.getDb('remote_238')
    try:
        m0[collection].update({'_id': id}, {'$set': {fieldName: postunixtime}})
    except Exception, e:
        log.msg(format= u'更新mongo的起始url的PublishTime异常.cause=%(cause)s', level = log.ERROR, cause = str(e))
        traceback.print_exc()
        m0.connection.close()

#美容人才网依据职位类别获取请求
def get_requests_mongo_by_position(collection, siteID):
    m0 = TQMongo.getDb('remote_238')
    try:
        return m0[collection].find({'PPosition': {'$gt': 0}, 'SiteID': siteID}).sort([('LastTime', 1)]).limit(10)
    except Exception, e:
        log.msg(format= u'从mongo获取起始url异常.cause=%(cause)s', level = log.ERROR, cause = str(e))
        traceback.print_exc()
        m0.connection.close()

#曝工资依据行业获取请求
#共15个行业
def get_requests_mongo_by_industry(collection):
    m0 = TQMongo.getDb('remote_238')
    try:
        m0[collection].findOne({}).sort([{'LastTime': 1}])
    except Exception, e:
        log.msg(format= u'从mongo获取起始url异常.cause=%(cause)s', level = log.ERROR, cause = str(e))
        traceback.print_exc()
        m0.connection.close()

#依据职位id,发布时间戳查找职位
def exist_linkid(site_id, linkid, post_unixtime):
    ret = False
    m0 = TQMongo.getDb('remote_238')
    try:
        js = m0['DupeJob'].find_one({'SiteID': site_id, 'LinkID': linkid}, {'_id': 1, 'PostUnixTime': 1})
        if js:
            if post_unixtime - js['PostUnixTime'] <= 3600 * 10:
                ret = True
            else:
                m0['DupeJob'].update({'_id': js['_id']}, {'$set': {'PostUnixTime': post_unixtime}})
        else:
            js = json.loads('{}')
            js['SiteID'] = site_id
            js['LinkID'] = linkid
            js['PostUnixTime'] = post_unixtime
            m0['DupeJob'].insert(js)
        return ret
    except Exception, e:
        log.msg(format= u'职位去重模块异常.cause=%(cause)s', level = log.ERROR, cause = str(e))
        traceback.print_exc()
        m0.connection.close()

def alreadyExistsUrl(url):
    ret = False
    m0 = TQMongo.getDb('remote_238')
    try:
        js = m0['KanZhunURI'].update({'_id': url}, {'_id': url}, upsert = True, fsync = True)
        if js:
            if js['updatedExisting']:
                ret = True
            else:
                ret = False
        return ret
    except Exception, e:
        log.msg(format= u'Url去重模块异常.cause=%(cause)s', level = log.ERROR, cause = str(e))
        traceback.print_exc()
        m0.connection.close()

#从redis队列获取序列化的http请求
def get_requests_redis(spidername):
    r = TQRedis.GetRedis('remote_252_0')
    data = r.spop('ganji_sharelink')
    if data:
        row = pickle.loads(data)
        return row
        #
        m0 = TQMongo.getDb('remote_252_webjob')
        try:
            js = m0['webjob2'].find({'SiteID': row['SiteID'], 'LinkID': row['LinkID']})
            if not js:
                r.lpush(SHARE_LINK_QUEUE_KEY % {'spider': spidername}, data)
            else:
                return row
        except Exception, e:
            m0.connection.close()

#删除redis中序列化的http请求
def rem_share_link(member):
    r = TQRedis.GetRedis('remote_252_0')
    r.srem('ganji_sharelink', member)


