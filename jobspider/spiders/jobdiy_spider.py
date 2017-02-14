# -*- encoding=utf-8 -*-


import json
from scrapy import Request, log
from jobspider.spiders.base_spider import BaseSpider
from jobspider.jobdiy_items import Job, Company
from jobspider.utils.tools import FmtSQLCharater


class JobdiySpider(BaseSpider):

	name = 'freetime.jobdiy'

	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36'
	}

	list_url = 'http://app.jobdiy.cn/app/v2_0/Activity/list/?page_size=10&pn=<?page?>&city=<?city?>'

	info_url = 'http://app.jobdiy.cn/app/v2_0/Activity/applyActivityDetail/?activity_id=<?aid?>'

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
			yield Request(url=self.list_url.replace('<?page?>', '1').replace('<?city?>', city),
			              callback=self.parse_list, headers=self.headers, dont_filter=True,
			              meta={'page': 1, 'city': city})

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
		if 1 == js['status']:
			for item in js['activityPage']['list']:
				yield Request(url=self.info_url.replace('<?aid?>', str(item['activity_id'])),
				              callback=self.parse_info, headers=self.headers, dont_filter=True,
				              meta={'aid': item['activity_id']})
			#下一页
			city = response.meta['city']
			if len(js['activityPage']['list']) == 10:
				page = response.meta['page'] + 1
				log.msg(u'采集[%s]第[%d]页' % (city, page))
				yield Request(url=self.list_url.replace('<?page?>', str(page)).replace('<?city?>', city),
				              callback=self.parse_list, headers=self.headers, dont_filter=True,
				              meta={'page': page, 'city': city})
			else:
				log.msg('采集[%s]终止' % city)
		else:
			log.msg(js['msg'])

	def parse_info(self, response):
		data = response.body
		if data == '' or data == '[]':
			log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
			return
		try:
			js = json.loads(data)
		except:
			log.msg(u'兼职职位[%d]请求结果解析异常,非json数据.url=%s' % (response.meta['aid'], response.url), level = log.INFO)
			return
		if 1 == js['status']:
			j = Job()
			for (key, value) in js['activityDetail'].iteritems():
				if key not in ['salary', 'avatar', 'banner_kw']:
					if value is None:
						if key == 'group_id':
							j[key] = -1
						elif key == 'post_time':
							j[key] = ''
					else:
						if key == 'require_info':
							j[key] = FmtSQLCharater(value)
						else:
							j[key] = value
			yield j
			#
			cid = js['activityDetail']['company_im_id']
			yield Request(url=self.cmp_url.replace('<?cid?>', str(cid)),
			              callback=self.parse_cmp, headers=self.headers, dont_filter=True, meta={'cid': cid})
		else:
			log.msg(js['msg'])

	def parse_cmp(self, response):
		data = response.body
		if data == '' or data == '[]':
			log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
			return
		try:
			js = json.loads(data)
		except:
			log.msg(u'兼职公司[%d]请求结果解析异常,非json数据.url=%s' % (response.meta['cid'], response.url), level = log.INFO)
			return
		if 1 == js['status']:
			c = Company()
			for (key, value) in js['companyInfo'].iteritems():
				if key not in ['avatar']:
					if value is None:
						if key == 'hire_type':
							c[key] = ''
						elif key == 'introduction':
							c[key] = ''
					else:
						c[key] = value
			yield c
		else:
			log.msg(js['msg'])
