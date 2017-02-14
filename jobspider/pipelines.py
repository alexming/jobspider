# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import traceback
import datetime
import json
from scrapy import log
from jobspider.scrapy_db.db_pool import TQDbPool
from jobspider.scrapy_mongo.Q_mongo import *
from jobspider.scrapy_redis.redis_pool import TQRedis
from jobspider.scrapy_file.db_file import DbFile
from jobspider.utils.tools import md5, logger, FmtSQLCharater


try:
    import cPickle as pickle
except ImportError:
    import pickle


class MongoPipeline(object):

    def open_spider(self, spider):
        self.db = TQMongo.getDb('remote_252_webjob')
        self.dupedb = TQMongo.getDb('remote_238')
        self.dbFile = DbFile()

    def close_spider(self, spider):
        self.db.connection.close()
        self.dupedb.connection.close()

    def process_item(self, item, spider):
        item_name = item.__class__.__name__
        if item_name == 'WebJob':
            if item['JobType'] == 1:
                self.db['webjob2'].insert(dict(item))
            else:
                self.db['webjob2_jz'].insert(dict(item))
        elif item_name == 'Company':
            item = dict(item)
            #企业数据去重判别
            try:
                LastModifyTime = datetime.datetime.today()
                js = self.dupedb['DupeCompany'].find_one({'SiteID': item['SiteID'], 'CompanyLink': item['company_id']})
                if js:
                    LastModifyTime = js['LastModifyTime']
                
                if ((datetime.datetime.today() - LastModifyTime).seconds >= 3600 * 200) or (not js):
                    if not js:
                        js = json.loads('{}')
                        js['SiteID'] = item['SiteID']
                        js['CompanyLink'] = item['company_id']
                        js['LastModifyTime'] = datetime.datetime.today()
                        self.dupedb['DupeCompany'].insert(js)
                    else:
                        self.dupedb['DupeCompany'].update({'_id': js['_id']},{'$set':{'LastModifyTime': datetime.datetime.today()}})
                    #
                    cmd = u'''insert into JWebCompany(CompanyName,Industry,CompanyType,CompanyScale,CompanyAddress,
AreaName,Relation,Mobile,CompanyDesc,WebSiteID,CompanyLink,GisLongitude,GisLatitude,UserId,UserName,Email,CompanyUrl,CompanyLogoUrl,
ProvinceName,WorkArea1,AreaCode1) values(
'%s','%s','%s','%s','%s',
'%s','%s','%s','%s',%d,'%s',
%s,%s,'%s','%s','%s','%s','%s',
'%s','%s','%s');''' % (
                    FmtSQLCharater(item['CompanyName']),item['Industry'],item['CompanyType'],item['CompanyScale'],item['CompanyAddress'],
                    item['CityName'],FmtSQLCharater(item['Relation']),item['Mobile'],FmtSQLCharater(item['CompanyDesc']),item['SiteID'],item['company_id'],
                    item['GisLongitude'],item['GisLatitude'],item['UserId'],item['UserName'],item['Email'],item['CompanyUrl'],item['CompanyLogoUrl'],
                    item['ProvinceName'], item['WorkArea1'], item['AreaCode1'])
                    """
                    #企业认证信息
                    if item['SiteID'] == 4:
                        cmd += u'''delete from JobDataSpiderCompany..JWebCompany_Verify where CompanyName='%s';''' % FmtSQLCharater(item['CompanyName'])
                        cmd += u'''insert into JobDataSpiderCompany..JWebCompany_Verify(SiteID,CompanyName,CompanyCode,
IsVerify,IsSafe,CreditValue,SyncStatus) values(%d,'%s','%s',%d,%d,%d,0)''' % (item['SiteID'],FmtSQLCharater(item['CompanyName']),item['company_id'],
                            item['Yan'],item['FangXin'],item['Credibility'])
                        #
                        """
                    ret = TQDbPool.execute('remote_253', cmd)
                    if ret is None:
                        logger.error(u'sql指令执行失败,出现异常:dbname=%s,commamd=%s' % ('remote_253', cmd))
                    elif ret == -2:
                        logger.error(u'数据库连接失败导致执行失败:dbname=%s,commamd=%s' % ('remote_253', cmd))
                        
                    #self.dbFile.addCommand('remote_253', cmd)
            except Exception, e:
                self.dupedb.connection.close()
                log.msg(message= u'mongo 连接异常,mongoname=remote_238.DupeCompany,%s' % e.message, level=log.ERROR)
                traceback.print_exc()
        elif item_name == 'Comment':
            item = dict(item)
            #评论去重
            md5_company_link = ''
            try:
                js = self.db['Company'].find_one({'CompanyName': item['CompanyName'], 'AreaCode': item['AreaCode']})
                if js:
                    md5_company_link = js['MD5CompanyLink']
                else:
                    js = self.db['Company'].find_one({'CompanyName': item['CompanyName']})
                    if js:
                        md5_company_link = js['MD5CompanyLink']
            except Exception, e:
                self.db.connection.close()
                log.msg(message= u'mongo 连接异常,mongoname=remote_252_webjob.Company,%s' % str(e.message), level=log.ERROR)
                traceback.print_exc()
            #
            comment_key = md5(item['CompanyName'] + item['Title'] + item['Type'] + item['Content'])
            OperStatus = 0
            if md5_company_link != '':
                OperStatus = 1
            #
            cmd = u'''if not exists(select top 1 SiteID from JobDataSpiderCompany..JWebCompanyComment where UniqueKey='%s') ''' % comment_key
            cmd += u'''insert into JobDataSpiderCompany.dbo.JWebCompanyComment(SiteID,CompanyName,Title,Time,Type,Content,SrcUrl,TotalScore,UniqueKey,MD5CompanyLink,OperStatus) values(%d,'%s','%s','%s',
'%s','%s','%s',%d,'%s','%s',%d)''' % (item['SiteID'],FmtSQLCharater(item['CompanyName']),item['Title'],item['Time'],
                item['Type'],item['Content'],item['SrcUrl'],item['TotalScore'],comment_key,md5_company_link,OperStatus)
            ret = TQDbPool.execute('remote_253', cmd)
            if ret is None:
                logger.error(u'sql指令执行失败,出现异常:dbname=%s,commamd=%s' % ('remote_253', cmd))
            elif ret == -2:
                logger.error(u'数据库连接失败导致执行失败:dbname=%s,commamd=%s' % ('remote_253', cmd))
            #self.dbFile.addCommand('remote_253', cmd)
        elif item_name == 'Salary':
            cmd = u'''insert into JobDataSpiderCompany..JWebCompany_Salary_Info(company_code,company_name,company_logo,
job_name,job_count,average,high,low,praise_rate,mark,src_url,company_url,comment_url) values('%s','%s','%s',
'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' % (item['company_code'],item['company_name'],item['company_logo'],
item['job_name'],item['job_count'],item['average'],item['high'],item['low'],
item['praise_rate'],item['mark'],item['src_url'],item['company_url'],item['comment_url'])
            #
            ret = TQDbPool.execute('remote_253', cmd)
            if ret is None:
                logger.error(u'sql指令执行失败,出现异常:dbname=%s,commamd=%s' % ('remote_253', cmd))
            elif ret == -2:
                logger.error(u'数据库连接失败导致执行失败:dbname=%s,commamd=%s' % ('remote_253', cmd))
        elif item_name == 'GSXComment':
            cmd = '''insert ignore into gsx_comment(c_id,info,c_time,user_name,mobile,city_name,course_name,teacher_name,create_time) 
values (%s,'%s','%s','%s','%s','%s','%s','%s',UNIX_TIMESTAMP())''' % (item['c_id'], item['info'], item['c_time'], item['user_name'], 
            item['mobile'], item['city_name'], item['course_name'],item['teacher_name'])
            #
            ret = TQDbPool.execute('GSX', cmd)
            if ret is None:
                logger.error(u'sql指令执行失败,出现异常:dbname=%s,commamd=%s' % ('GSX', cmd))
            elif ret == -2:
                logger.error(u'数据库连接失败导致执行失败:dbname=%s,commamd=%s' % ('GSX', cmd))
        return item
