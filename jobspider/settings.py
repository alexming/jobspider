# -*- coding: utf-8 -*-

# Scrapy settings for JobSpider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'JobSpider'

SPIDER_MODULES = ['jobspider.spiders']
NEWSPIDER_MODULE = 'jobspider.spiders'
ITEM_PIPELINES = {'jobspider.pipelines.MongoPipeline': 100}
#全局并发数 应该选择一个能使CPU占用率在80%-90%的并发数
CONCURRENT_REQUESTS = 100
#单爬虫的最大并行请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 1000
#爬取的质量更高，尽量使用宽度优先的策略
SCHEDULER_ORDER = 'BFO'
CONCURRENT_REQUESTS_PER_IP = 0
DEPTH_LIMIT = 0
DEPTH_PRIORITY = 0
#是否收集最大深度数据
DEPTH_STATS = False
#DNS缓存
DNSCACHE_ENABLED = True
#下载下一页面等待时间
DOWNLOAD_DELAY = 0
DOWNLOADER_DEBUG = True
#AutoThrottle extension
#AUTOTHROTTLE_ENABLED = True
#AUTOTHROTTLE_START_DELAY = 3.0
#AUTOTHROTTLE_CONCURRENCY_CHECK_PERIOD = 10#How many responses should pass to perform concurrency adjustments.
#日志级别(开发＝DEBUG 生产=INFO)
LOG_LEVEL = 'DEBUG'
#禁止重试
RETRY_ENABLED = False
#禁用cookies
COOKIES_ENABLED = False
#
DOWNLOADER_MIDDLEWARES = {
#    'woaidu_crawler.contrib.downloadmiddleware.google_cache.GoogleCacheMiddleware':50,
#    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
#scrapy默认代理中间件
#    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
#http动态随机代理池
#    'jobspider.contrib.downloadmiddleware.rotate_httpproxy_bgz.RotateHttpProxyMiddlewareForBGZ': 100,
#http代理池
#    'jobspider.contrib.downloadmiddleware.rotate_httpproxy.RotateHttpProxyMiddleware': 100,
#http请求轮询user-agent
#    'jobspider.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware': 90
}
#动态轮询请求头
ROTATE_HTTP_USERAGENT_MIDDLEWARE = {'jobspider.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware': 90}
#动态轮询代理下载中间件
ROTATE_HTTP_PROXY_MIDDLEWARE_FOR_BGZ = {'jobspider.contrib.downloadmiddleware.rotate_httpproxy_bgz.RotateHttpProxyMiddlewareForBGZ': 100}

#---------------------赶集网------------------------------#

#默认http请求头
GANJI_REQUEST_HEADERS = {
    'Accept': '*/*',
    'AcceptEncoding': 'gzip',
    'AcceptLanguage': 'zh-cn',
    'Connection': 'keep-alive',
    'Host': 'mobapi.ganji.com',
    'ContentType': 'application/x-www-form-urlencoded',
    #'UserAgent': 'HouseRent/6.0.0 CFNetwork/672.1.15 Darwin/14.0.0',
    #客户自定义头
    #'agency': 'appstore',
    'agency': 'web',
    #'cityScriptIndex': '401',
    #'clientAgent': 'iphone#320*480',
    'clientAgent': 'MI 3C#1080*1920#3.0',
    #'ClientTimeStamp': '2015-01-28 16:21:56',
    'contentformat': 'json2',
    'customerId': '801',
    #'GjData-Version': '1.0',
    #'model': 'Generic/iphone',
    'model': 'Generic/AnyPhone',
    #'SeqId': '195F5ACB-3A4A-44DC-8E06-4E370AE4E623',
    'userId': 'E6A29CB31C12113553B4CFDF5DDB90BC',
    #'userId': '86EE11518F9AF902734D09AD926600A9',
    'versionId': '6.1.1'
    #'versionId': '6.0.0'
}
#post-json参数
PAGE_SIZE = 30
JSON_ARGS = '''{"sortKeywords":[{"field": "post_at", "sort": "desc"}], "categoryId": %(categoryId)d, "andKeywords": [], \
"customerId": "801", "cityScriptIndex": %(cityId)d, "pageIndex": %(pageIndex)d, "pageSize": %(pageSize)d, "queryFilters":[]}'''
GANJI_COMMENT = 'http://webapp.ganji.com/wanted/mobile/comment.php?company_id=%(company_id)s&client_type=1'

#---------------------58同城------------------------------#

WUBA_REQUEST_HEADERS = {
    'Connection' : 'Keep-Alive',
    'Host' : 'app.58.com',
    'Cookie2' : '$Version=1',
    'Accept-Encoding' : 'gzip,deflate',
    'imei' : '863361022674370',
    'uuid' : '013c0646-3a42-465f-b468-6bae8efda231',
    'productorid' : '1',
    'ua' : 'MI 3C',
    'platform' : 'android',
    'version' : '6.0.5.0',
    'osv' : '4.4.4',
    'channelid' : '496',
    'apn' : 'WIFI',
    'cid' : '4',
    'tn' : '',
    'uid' : '',
    'brand' : 'Xiaomi',
    'm' : '68:df:dd:6a:b4:6e',
    'PPU' : '',
    'netType' : 'wifi',
    'bangbangid' : '',
    'lat' : '22.547083',
    'lon' : '113.939188',
    'id58' : '91391477678574'
}

WUBA_BASEURL = 'http://app.58.com/api'

WUBA_LISTINFO = '/list/<?category?>/?action=getListInfo&appId=3&ct=filter&curVer=6.1.2&isNeedAd=1&localname=<?city?>&os=android&page=<?page?>&tabkey=allcity'

WUBA_INFO = '/detail/<?category?>/<?infoID?>/?appId=3&format=json&localname=<?city?>&platform=android&version=6.1.2'

#--------------------看准网------------------------------#

KANZHUN_REQUEST_HEADERS = {
    'Host' : 'www.kanzhun.com',
    'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept' : 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding' : 'gzip, deflate',
    'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Cache-Control' : 'no-cache',
    'Connection' : 'keep-alive'
}

KANZHUN_BASEURL = 'http://www.kanzhun.com'

#-------------------中华英才网------------------------------#

CHINAHR_REQUEST_HEADERS = {
    'Host' : 'www.chinahr.com',
    'Content-Type' : 'application/x-www-form-urlencoded',
    'Accept' : 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding' : 'gzip, deflate',
    'Accept-Language' : 'zh-CN,zh;q=0.8',
    'Connection' : 'keep-alive',
    'Origin' : 'http://www.chinahr.com',
    'Referer' : 'http://www.chinahr.com/',
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
}

CHINAHR_BASEURL = 'http://www.chinahr.com'
#第7位1表示按照刷新时间进行排序,只查询当天刷新的职位
CHINAHR_JOBLISTURL = 'http://www.chinahr.com/so/0/1-0-0-0-0-0-1-0-0-0-0-0-0-0-<?CityId?>-0/p0'

#------------------138美容人才网---------------------------#

MR138JOB_REQUEST_HEADERS = {
    'Host' : 'apijob.138mr.com',
    'Content-Type' : 'application/json;charset=UTF-8',
    'Connection' : 'Keep-Alive',
    'User-Agent' : 'imgfornote',
    'Authorization': '138apk20140210job138'
}

MR138JOB_BASEURL = 'http://apijob.138mr.com/Job'

MR138JOB_JOBLISTURL = 'http://apijob.138mr.com/Job/SearchHire/<?PageIndex?>/15/1'

#--------------------百城人才网---------------------------#

BAIC_REQUEST_HEADERS = {
    'Host': 'www.bczp.cn',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-cn',
    #百城求职宝/4.5 CFNetwork/672.1.15 Darwin/14.0.0
    'User-Agent': '%E7%99%BE%E5%9F%8E%E6%B1%82%E8%81%8C%E5%AE%9D/4.5 CFNetwork/672.1.15 Darwin/14.0.0'
}

BAIC_BASEURL = 'http://www.bczp.cn/3g/jw'
#搜索全国发布日期在30天以内的全职职位
BAIC_JOBLISTURL = '/searchjob.ashx?workcity=0&jobtype=<?Position?>&job_publish_date=30&ent_industry=0&sex=0&learn=0&money=0&expr=0&jobkind=0&lx=2&medals=&keyword=  &page=<?Page?>'

#----------------------百姓网----------------------------#
#请求头
BAIX_REQUEST_HEADERS = {
    'Host': 'www.baixing.com',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN, en-us, en',
    'User-Agent': 'BaixingMobileApi',
    'User-Agent': 'com.quanleimu.activity/6.1.0;Xiaomi;Xiaomi;HM NOTE 1TD;4.2.2;720x1280;360;qq;',
    'BAPI-APP-KEY': 'api_androidbaixing'
    #'APP_VERSION': '6.1.0'
}
#基础地址
BAIX_BASEURL = 'http://www.baixing.com/api/mobile'
#全职职位
BAIX_JOBLISTURL = '/gongzuo/ad?apiFormatter=AdList&suggestOn=1&area=<?city?>&from=<?from?>&size=30'
#兼职职位
BAIX_JZ_JOBLISTURL = '/jianzhi/ad?apiFormatter=AdList&suggestOn=1&area=<?city?>&from=<?from?>&size=30'
#职位详情
BAIX_JOBURL = '/Ad.ads/?adIds=<?adId?>'

#----------------------智联招聘------------------------#

ZHAOPIN_REQUEST_HEADERS = {
    'Host': 'mi.zhaopin.com',
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/json',
    'Accept-Language': 'zh-Hans;q=1, en;q=0.9, fr;q=0.8, de;q=0.7, ja;q=0.6, nl;q=0.5',
    'Accept': 'application/json',
    'User-Agent': 'kooxiv'
}

ZHAOPIN_BASE_URL = 'http://mi.zhaopin.com/android/Position'
#城市city,今日发布
ZHAOPIN_JOB_LIST_URL = '/Search?pageIndex=<?page?>&SF_2_100_4=<?city?>&pageSize=20&d=<?uuid?>&channel=zhilian&v=4.3&key=135486907212185&t=<?unixtime?>'

ZHAOPIN_JOB_URL = '/Detail?channel=zhilian&d=<?uuid?>&key=135486907212185&number=<?number?>&v=4.3&t=<?unixtime?>'


#----------------------51Job------------------------#

WUYAO_REQUEST_HEADERS = {
    'Host': 'api.51job.com',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': '51job-iphone-client'
}

WUYAO_BASE_URL = 'http://api.51job.com/api/job'
# 职位类别
WUYAO_JOB_LIST_URL = '/search_job_list.php?postchannel=0000&jobarea=000000&funtype=<?func?>&pagesize=2&pageno=<?page?>&accountid=&key=&productname=51job'

WUYAO_JOB_URL = '/get_job_info.php?jobid=<?jid?>&accountid=&key=&productname=51job'

WUYAO_CO_URL = '/get_co_info.php?coid=<?coid?>&productname=51job'

#-----------------------JobsDB------------------------#

JOBSDB_REQUEST_HEADERS = {
    'Host': 'sg.jobsdb.com',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': '*/*',
    'Accept-Language': 'zh-cn',
    'User-Agent': 'jobsDB/22 CFNetwork/672.1.15 Darwin/14.0.0'
}

JOBSDB_BASE_URL = 'http://sg.jobsdb.com/sg/en/mobileappapi'
JOBSDB_LIST_URL = '''/JobSearch?request=
{
  "IndustryId" : "0",
  "EmploymentTermId" : "0",
  "PagingCriteria" : {
    "ItemsPerPage" : "20",
    "CurrentPageIdx" : "<?page?>"
  },
  "CareerLevelFromId" : "0",
  "JobFunctionId" : "0",
  "Keyword" : "",
  "CareerLevelToId" : "0",
  "SalaryType" : "0",
  "SalaryF" : "0",
  "SalaryT" : "0",
  "LocationId" : "0"
}
'''
JOBSDB_INFO_URL = '/JobAdDetail?JobAdIds=<?JobAdIds?>'

#-----------------------STJobs------------------------#

STJOBS_REQUEST_HEADERS = {
    'Host': 'www.stjobs.sg',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
    'Accept-Language': 'zh-cn',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257 (342051168)'
}

STJOBS_BASE_URL = 'http://www.stjobs.sg/mob'
STJOBS_LIST_URL = '/searchjob?keyword=&jc=0&ex=&ttl=&t=0&dt=1&advanced_mode=1&limit=11&offset=<?offset?>'
STJOBS_INFO_URL = '/jobdetail?jobid=<?jobid?>'

#-----------------------JobStreet------------------------#

JOBSTREET_REQUEST_HEADERS = {
    'Host': 'job-search.jobstreet.com.sg',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
}

JOBSTREET_LIST_URL = 'http://job-search.jobstreet.com.sg/singapore/job-opening.php?specialization=<?specialization?>&pg=<?pg?>'

#-----------------------efinancialcareers--------------#
FINANCE_REQUEST_HEADER = {
    'Host': 'www.efinancialcareers.sg'
}

FINANCE_BASE_URL = 'http://www.efinancialcareers.sg'

FINANCE_LIST_URL = '/search?page=<?page?>&filterGroupForm.subSectors=<?sector?>'

#-----------------------mytechlogy--------------------#
MYTECHLOGY_REQUEST_HEADER = {
    'Host': 'www.mytechlogy.com'
}

MYTECHLOGY_BASE_URL = 'http://www.mytechlogy.com/IT-jobs-careers'

MYTECHLOGY_LIST_URL = '/?page=<?page?>&location=Singapore&date=30'

#-----------------------monster--------------------#
MONSTER_REQUEST_HEADER = {
    'Host': 'jobsearch.monster.com.sg'
}

MONSTER_BASE_URL = 'http://jobsearch.monster.com.sg'

MONSTER_LIST_URL = '/searchresult.html?rfr=;day=60;srt=pst;ref=http:%2F%2Fjobsearch%2Emonster%2Ecom%2Esg%2Fsearch%2Ehtml;show_omit=1;res_cnt=40;n=<?n?>'

#-----------------------recruit--------------------#
RECRUIT_REQUEST_HEADER = {
    'Host': 'singapore.recruit.net'
}

RECRUIT_BASE_URL = 'http://singapore.recruit.net'

RECRUIT_LIST_URL = '/search.html?query=<?filter?>&postdate=30&hitsPerPage=10&dedup=true&sortby=date&d=r&pageNo=<?page?>'

#-----------------------曝工资-------------------------#

BGZ_REQUEST_HEADERS = {
    'Host': 'baogz.com',
    'Accept-Encoding': 'gzip',
    'Connection': 'keep-alive',
    'User-Agent': 'Android bgz_app/6.1.50420'
}
#初始设备id号
BGZ_INSTRUMENTID = 'xa376aa2f1p8adq0xglz'
#主入口
BGZ_BASEURL = 'http://114.215.183.235/api/4'
#全国企业
BGZ_JOBLISTURL = '/industry/<?industry?>/companies?city=%E5%85%A8%E5%9B%BD&page=<?page?>&' + 'instrument_id=%s&fr=app_xiaomi' % BGZ_INSTRUMENTID
#企业所有职位
#设备id需要随机获取
#需要使用代理请求
BGZ_CMPJOBS = '/company/<?company?>/jobs?instrument_id=<?instrumentid?>&fr=app_xiaomi'
#设备id需要随机获取
#需要使用代理请求
BGZ_JOBDETAIL = '/job/<?sid?>/detail?instrument_id=<?instrumentid?>&fr=app_xiaomi'
#评论
BGZ_COMMENT = '/company/<?company?>/comment?page=<?page?>&instrument_id=x034bfa25u8d1o84f9cp&fr=app_xiaomi'

#----------------------跟我学---------------------------#

GSX_REQUEST_HEADERS = {
    'Host': 'sapi.genshuixue.com',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-cn'
}

#初始认证信息
AUTH_TOKEN_T = 'E34lZ2h5bGZoYmxnJT01OTc8NzUwJnl3aXZ4fXRpJj4xNTAmZ3gmPzY5ODg9Nzc5PjsxJ3hmcXknPyhyaVBofFJfWiiD'
SIGNATURE_T = '3d5d5b5441d4ecdfbc7f5b16e42f58f3'
TIMESTAMP_T = 1433828855
#
AUTH_SIGN_T = 'auth_token=%s&signature=%s&timestamp=%d' % (AUTH_TOKEN_T, SIGNATURE_T, TIMESTAMP_T)
#初始认证信息
AUTH_TOKEN_C = 'E34lZ2h5bGZoYmxnJT01OTc8NzUwJnl3aXZ4fXRpJj4xNTAmZ3gmPzY5ODg9Nzc5PjsxJ3hmcXknPyhyaVBofFJfWiiD'
SIGNATURE_C = 'b715ce21d9a601284576329eafefb1e5'
TIMESTAMP_C = 1434091336
#
AUTH_SIGN_C = 'auth_token=%s&signature=%s&timestamp=%d' % (AUTH_TOKEN_C, SIGNATURE_C, TIMESTAMP_C)
#
GSX_BASEURL = 'http://sapi.genshuixue.com'
#老师列表<依据评论数排序>
GSX_TEACHER = '/teacher/search?city_id=<?city_id?>&version=2.1.0&sort=comment&source=ios&platform=iPhone&course=<?course?>&next_cursor=<?page?>&%s' % AUTH_SIGN_T
#老师评论
GSX_COMMENT = '/comment/teacherComment?version=2.1.0&teacher_id=<?teacher_id?>&next_cursor=<?page?>&%s' % AUTH_SIGN_C

#---------------------多学网---------------------------#

#公共请求头
DUOX_REQUEST_HEADERS = {
    'Host': 'api.learnmore.com.cn',
    'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
    'Content-Type': 'application/x-www-form-urlencoded'
}
#基础请求URL
DUOX_BASEURL = 'http://api.learnmore.com.cn'
#学校列表参数
#param={"gps":"22.546676,113.939783","category":12,"area":"4_-9999999","order":"4","keyword":""}&device=[DN]#lcsh92_wet_tdd[V]#4.2.2[appversion]#1.1.34[channel]#xiaom[phone]#null[imsi]#null[imei]#865316024468880[loc]#[gps]#22.546676,113.939783
DUOX_SCHOOL_LIST_URL = '/school/list.json'
DUOX_SCHOOL_LIST_PARAM = 'param={"gps":"","category":<?category?>,"area":"4_-9999999","startIndex":<?page?>,"order":"4","keyword":""}&device=[DN]#lcsh92_wet_tdd[V]#4.2.2[appversion]#1.1.34[channel]#xiaom[phone]#null[imsi]#null[imei]#865316024468880[loc]#[gps]#'
#学校详情参数
#param={"id":"264"}&device=[DN]#lcsh92_wet_tdd[V]#4.2.2[appversion]#1.1.34[channel]#xiaom[phone]#null[imsi]#null[imei]#865316024468880[loc]#[gps]#22.546676,113.939783
DUOX_SCHOOL_INFO_URL = '/school/info.json'
DUOX_SCHOOL_INFO_PARAM = 'param={"id":"<?id?>"}&device=[DN]#lcsh92_wet_tdd[V]#4.2.2[appversion]#1.1.34[channel]#xiaom[phone]#null[imsi]#null[imei]#865316024468880[loc]#[gps]#'
DUOX_SCHOOL_INFO_URL2 = 'http://www.learnmore.com.cn/h5/schoolInfo?id=<?id?>&_=<?unixtime?>&callback='
#学校评论列表
#param={"count":20,"id":"264","type":"3","startIndex":0}
DUOX_COMMENT_LIST_URL = '/comment/list.json'
DUOX_COMMENT_LIST_PARAM = 'param={"count":20,"id":"<?id?>","type":"3","startIndex":"<?page?>"}'
#学校课程列表
#param={"school":"264"}&device=[DN]#lcsh92_wet_tdd[V]#4.2.2[appversion]#1.1.34[channel]#xiaom[phone]#null[imsi]#null[imei]#865316024468880[loc]#[gps]#22.546676,113.939783
DUOX_COURSE_LIST_URL = '/course/list.json'
DUOX_COURSE_INFO_URL = 'http://www.learnmore.com.cn/h5/courseDetail?id=<?id?>&_=<?unixtime?>&callback='
DUOX_COURSE_LIST_PARAM = 'param={"school":"<?id?>"}&device=[DN]#lcsh92_wet_tdd[V]#4.2.2[appversion]#1.1.34[channel]#xiaom[phone]#null[imsi]#null[imei]#865316024468880[loc]#[gps]#'

#----------------------------------------------------#

#REDIS_HOST = '192.168.1.233'
#REDIS_PORT = 6379

#DUPEFILTER_CLASS = 'jobspider.scrapy_redis.dupefilter.RFPDupeFilter'
#SCHEDULER = 'scrapy.core.scheduler.Scheduler'
#SCHEDULER = "jobspider.scrapy_redis.rotate_scheduler.RotateScheduler"
#SCHEDULER_PERSIST = False
#SCHEDULER_QUEUE_CLASS = 'JobSpider.scrapy_redis.queue.SpiderQueue'


#http_proxy
PROXY_DBNAME = 'remote_253'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'JobSpider (+http://www.yourdomain.com)'
