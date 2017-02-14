# -*- encoding=utf-8 -*-


import json
from scrapy import FormRequest, Request, log
from jobspider.spiders.base_spider import BaseSpider
from jobspider.spiders.freetime.stuin_items import Job
from jobspider.utils.tools import FmtSQLCharater


class StuinSpider(BaseSpider):

    name = 'freetime.stuin'

    headers = {
        'Host': 'api.stuin.com',
        'Authorization': '',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    root_url = 'http://api.stuin.com'

    login_url = root_url + '/account/user_login'
    login_arg = {
        'DownloadFromApplicationId': '14',
        'CityId': '0',
        'Device': 'Android',
        'Password': '147258',
        'Mobile': '13823636595',
        'DeviceToken': '00000000-17c7-0779-ffff-ffff946e3ee1',
        'VersionNumber': '2.2.7'
    }

    list_url = root_url + '/job/search'
    list_arg = {
        'CategoryId': '0',
        'TermId': '0',
        'PageSize': '10',
        'Gender': '0',
        'RegionId': '0',
        'OrderById': '0',
        'PageIndex': '1'
    }

    info_url = root_url + '/job/detail/<?id?>'

    all_region = [
        {'id': 1128, 'name': u'直辖市-北京'},
        {'id': 1145, 'name': u'直辖市-天津'},
        {'id': 1162, 'name': u'直辖市-重庆'},
        {'id': 1201, 'name': u'直辖市-上海'},
        {'id': 111, 'name': u'浙江省-杭州'},
        {'id': 1, 'name': u'浙江省-宁波'},
        {'id': 125, 'name': u'浙江省-温州'},
        {'id': 136, 'name': u'浙江省-绍兴'},
        {'id': 143, 'name': u'浙江省-湖州'},
        {'id': 149, 'name': u'浙江省-嘉兴'},
        {'id': 157, 'name': u'浙江省-金华'},
        {'id': 167, 'name': u'浙江省-衢州'},
        {'id': 174, 'name': u'浙江省-舟山'},
        {'id': 179, 'name': u'浙江省-台州'},
        {'id': 189, 'name': u'浙江省-丽水'},
        {'id': 199, 'name': u'安徽省-芜湖'},
        {'id': 1497, 'name': u'安徽省-合肥'},
        {'id': 208, 'name': u'江苏省-镇江'},
        {'id': 225, 'name': u'江苏省-南京'},
        {'id': 1424, 'name': u'江苏省-无锡'},
        {'id': 1433, 'name': u'江苏省-徐州'},
        {'id': 1444, 'name': u'江苏省-常州'},
        {'id': 1452, 'name': u'江苏省-苏州'},
        {'id': 1462, 'name': u'江苏省-南通'},
        {'id': 1471, 'name': u'江苏省-淮安'},
        {'id': 1480, 'name': u'江苏省-盐城'},
        {'id': 1490, 'name': u'江苏省-扬州'},
        {'id': 215, 'name': u'江西省-南昌'},
        {'id': 1219, 'name': u'河北省-石家庄'},
        {'id': 1242, 'name': u'河北省-唐山'},
        {'id': 1257, 'name': u'河北省-邯郸'},
        {'id': 1276, 'name': u'河北省-保定'},
        {'id': 1302, 'name': u'河北省-沧州'},
        {'id': 1319, 'name': u'河北省-廊坊'},
        {'id': 1330, 'name': u'山西省-太原'},
        {'id': 1341, 'name': u'辽宁省-沈阳'},
        {'id': 1355, 'name': u'辽宁省-大连'},
        {'id': 1366, 'name': u'辽宁省-鞍山'},
        {'id': 1374, 'name': u'吉林省-长春'},
        {'id': 1385, 'name': u'吉林省-吉林'},
        {'id': 1395, 'name': u'黑龙江省-哈尔滨'},
        {'id': 1414, 'name': u'黑龙江省-大庆'},
        {'id': 1507, 'name': u'福建省-福州'},
        {'id': 1520, 'name': u'福建省-厦门'},
        {'id': 1527, 'name': u'福建省-泉州'},
        {'id': 1540, 'name': u'山东省-济南'},
        {'id': 1551, 'name': u'山东省-青岛'},
        {'id': 1562, 'name': u'山东省-淄博'},
        {'id': 1571, 'name': u'山东省-东营'},
        {'id': 1577, 'name': u'山东省-烟台'},
        {'id': 1590, 'name': u'山东省-潍坊'},
        {'id': 1603, 'name': u'山东省-济宁'},
        {'id': 1615, 'name': u'山东省-泰安'},
        {'id': 1622, 'name': u'山东省-威海'},
        {'id': 1627, 'name': u'山东省-德州'},
        {'id': 1639, 'name': u'山东省-临沂'},
        {'id': 1652, 'name': u'河南省-郑州'},
        {'id': 1667, 'name': u'河南省-洛阳'},
        {'id': 1683, 'name': u'河南省-南阳'},
        {'id': 1701, 'name': u'湖北省-武汉'},
        {'id': 1713, 'name': u'湖南省-长沙'},
        {'id': 1722, 'name': u'湖南省-岳阳'},
        {'id': 1732, 'name': u'湖南省-常德'},
        {'id': 1742, 'name': u'广东省-广州'},
        {'id': 1754, 'name': u'广东省-深圳'},
        {'id': 1761, 'name': u'广东省-珠海'},
        {'id': 1765, 'name': u'广东省-佛山'},
        {'id': 1771, 'name': u'广东省-惠州'},
        {'id': 1777, 'name': u'广东省-东莞'},
        {'id': 1810, 'name': u'广东省-中山'},
        {'id': 1835, 'name': u'海南省-海口'},
        {'id': 1840, 'name': u'四川省-成都'},
        {'id': 1860, 'name': u'四川省-绵阳'},
        {'id': 1870, 'name': u'贵州省-贵阳'},
        {'id': 1881, 'name': u'云南省-昆明'},
        {'id': 1896, 'name': u'陕西省-西安'},
        {'id': 1910, 'name': u'陕西省-宝鸡'},
        {'id': 2019, 'name': u'陕西省-安康'},
        {'id': 1923, 'name': u'甘肃省-兰州'},
        {'id': 1933, 'name': u'青海省-西宁'},
        {'id': 1941, 'name': u'内蒙古-呼和浩特'},
        {'id': 1951, 'name': u'内蒙古-包头'},
        {'id': 1961, 'name': u'广西省-南宁'},
        {'id': 1974, 'name': u'广西省-柳州'},
        {'id': 1985, 'name': u'广西省-桂林'},
        {'id': 2003, 'name': u'宁夏-银川'},
        {'id': 2010, 'name': u'新疆-乌鲁木齐'}
    ]

    current_region_index = 0

    def start_requests(self):
        if '' == self.headers['Authorization']:
            yield FormRequest(url=self.login_url, method='POST', formdata=self.login_arg, callback=self.app_login, dont_filter=True, meta={'name': u'登录请求'}, errback=self.requestErrorBack)
        else:
            #请求列表
            yield self._enum_region_for_request()

    def requestErrorBack(self, error):
        print(error)

    def app_login(self, response):
        (result, js) = self._validate_response(response)
        if result:
            if 1 == js['jsonStatus']:
                self.headers['Authorization'] = js['token']
                log.msg(u'%s成功,token=%s,tokenExpire=%s,userId=%s' % (response.meta['name'], js['token'], js['tokenExpire'], js['userId']))
                #请求列表
                yield self._enum_region_for_request()
            else:
                self.headers['Authorization'] = ''
                self.did_failed_request(response, js['message'])
        else:
            self.headers['Authorization'] = ''

    def _enum_region_for_request(self):
        if self.current_region_index == len(self.all_region):
            log.msg(u'数据采集完成')
            self.current_region_index = 0
        page = 1
        region = self.all_region[self.current_region_index]
        self.current_region_index += 1
        return self.request_list(region, page)


    def request_list(self, region, page):
        body_arg = self.list_arg
        body_arg['RegionId'] = str(region['id'])
        body_arg['PageIndex'] = str(page)
        log.msg(u'开始请求城市[%s]的第[%d]页数据' % (region['name'], page))
        return FormRequest(url=self.list_url, method='POST', formdata=body_arg, headers=self.headers,
                           callback=self.parse_list, dont_filter=True,
                           errback=self.requestErrorBack,
                           meta={'name': u'列表请求', 'region': region, 'page': page})

    def parse_list(self, response):
        (result, js) = self._validate_response(response)
        if result:
            if 1 == js['jsonStatus']:
                page = response.meta['page']
                region = response.meta['region']
                for item in js['results']:
                    yield FormRequest(url=self.info_url.replace('<?id?>', str(item['JobId'])), method='POST',
                                  headers=self.headers,
                                  formdata={'JobId': str(item['JobId'])},
                                  callback=self.parse_info,
                                  errback=self.requestErrorBack,
                                  dont_filter=True, meta={'name': u'详情请求', 'published': item['DatePublished'], 'region': region})
                if 10 == len(js['results']) and page < 50:
                    yield self.request_list(region, page + 1)
                else:
                    self.did_success_request(response)
            else:
                self.did_failed_request(response, js['message'])

    def parse_info(self, response):
        (result, js) = self._validate_response(response)
        if result:
            if 1 == js['jsonStatus']:
                j = Job()
                j['Published'] = response.meta['published']
                j['CityId'] = response.meta['region']['id']
                j['CityName'] = response.meta['region']['name']
                for (key, value) in js['result'].iteritems():
                    if key in ['Title', 'Description']:
                        j[key] = FmtSQLCharater(value)
                    else:
                        if key not in ['AllApplies']:
                            j[key] = value
                yield j
            else:
                self.did_failed_request(response, js['message'])

    def did_success_request(self, response):
        self.log(u'%s结束,总[%d]页' % (response.meta['name'], response.meta['page']))

    def did_failed_request(self, response, message):
        self.log(u'%s失败,原因:%s,uri=%s' % (response.meta['name'], message, response.url), level=log.ERROR)


    def _validate_response(self, response):
        data = response.body
        if data == '' or data == '[]':
            self.did_failed_request(response, '请求结果为空')
            return (False, None)
        try:
            js = json.loads(data)
            return (True, js)
        except:
            self.did_failed_request(response, '非法的json数据格式')
            return (False, None)
