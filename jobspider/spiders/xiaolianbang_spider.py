# -*- encoding=utf-8 -*-


import json
from scrapy import FormRequest, log
from jobspider.spiders.base_spider import BaseSpider
from jobspider.xiaolianbang_items import Job
from jobspider.utils.tools import FmtSQLCharater


class XiaolianbangSpider(BaseSpider):

	download_delay = 2
	randomize_download_delay = True

	name = 'freetime.xiaolianbang'

	headers = {
		'Host': 'api.xiaolianbang.com',
		'Accept': 'application/json',
		'Accept-Encoding': 'gzip',
		'Cookie': '',
		'Cookie2': '$Version=1'
	}

	list_url = 'http://api.xiaolianbang.com/zjz/v1/list'
	list_arg = {'pageSize': '20', 'cityName': u'', 'pageNum': '0'}

	contact_url = 'http://api.xiaolianbang.com/user/v1/way'
	contact_arg = {'id': '', 'type': '1', 'token': 'LAjsVYa1AQAxMzgyMzYzNjU5NQAAAAAAAAAAAAAAAAAAAAAAAAAAAA=='}

	cmp_url = 'http://app.jobdiy.cn/app/v2_0/Huanxin/companyInfo/?id=<?cid?>'

	all_city = [
		u'北京',
		u'深圳',
		u'广州',
		u'上海',
		u'天津',
		u'长沙',
		u'济南',
		u'东莞',
		u'佛山',
		u'南昌',
		u'宜昌',
		u'郑州',
		u'合肥',
		u'沈阳',
		u'苏州',
		u'太原',
		u'武汉',
		u'南京',
		u'杭州',
		u'重庆',
		u'成都',
		u'西安'
	]

	def start_requests(self):
		for city in self.all_city:
			self.list_arg['cityName'] = city
			yield FormRequest(
				url=self.list_url,
			    formdata=self.list_arg,
			    callback=self.parse_list,
				errback=self.requestErrorBack,
				headers=self.headers, dont_filter=True,
			    meta={'page': 0, 'city': city})

	def parse_list(self, response):
		data = response.body
		if data == '' or data == '[]':
			log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
			return
		try:
			js = json.loads(data)
		except:
			log.msg(u'兼职职位列表请求结果解析异常,非json数据.url=%s' % response.url, level = log.INFO)
			return
		if 0 == js['error_code']:
			city = response.meta['city']
			log.msg(u'获取城市[%s]的职位列表' % city)
			if js['data'].has_key('list'):
				for item in js['data']['list']:
					self.contact_arg['id'] = item['id']
					item['city_name'] = city
					yield FormRequest(url=self.contact_url,
					              formdata=self.contact_arg,
					              callback=self.parse_info, headers=self.headers, dont_filter=True,
					              meta={'item': item})
				#下一页
				if len(js['data']['list']) == 20 and response.meta['page'] < 50:
					page = response.meta['page'] + 1
					log.msg(u'采集[%s]第[%d]页' % (city, page))
					self.list_arg['cityName'] = city
					self.list_arg['pageNum'] = str(page)
					yield FormRequest(url=self.list_url,
					              formdata=self.list_arg,
					              callback=self.parse_list, headers=self.headers, dont_filter=True,
					              meta={'page': page, 'city': city})
				else:
					log.msg('采集[%s]终止' % city)
			else:
				log.msg('采集[%s]终止' % city)
		else:
			log.msg(js['error_message'])

	def parse_info(self, response):
		data = response.body
		if data == '' or data == '[]':
			log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
			return
		try:
			js = json.loads(data)
		except:
			log.msg(u'兼职职位[%s]请求结果解析异常,非json数据.url=%s' % (response.meta['item']['id'], response.url), level = log.INFO)
			return
		if 0 == js['error_code']:
			j = Job()
			item = response.meta['item']
			for (key, value) in item.iteritems():
				if key not in ['zjz_type']:
					j[key] = value
				else:
					for (kk, kv) in value.iteritems():
						j['zjz_' + kk] = kv
			if js['data'].has_key('tel'):
				j['tel'] = js['data']['tel']['tell']
				j['contact'] = js['data']['tel']['contact']
			yield j
		else:
			log.msg(js['error_message'])