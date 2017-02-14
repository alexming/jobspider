# -*- encoding=utf-8 -*-


import json
from scrapy import Request, log
from jobspider.spiders.base_spider import BaseSpider
from jobspider.jzdd_items import Job


class JzddSpider(BaseSpider):

	name = 'freetime.jzdd'
	download_delay = 2
	randomize_download_delay = True
    
	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36'
	}

	list_url = 'http://api.jzdd.net/index.php/api/index?sign=a73ed0352cddc82711c54320172d0f5a&act=job&fun=getnewjob&uid=0&pindex=<?page?>&psize=20&address=<?address?>'

	info_url = 'http://api.jzdd.net/index.php/api/index?sign=a73ed0352cddc82711c54320172d0f5a&act=job&fun=getjob&id=<?id?>&uid=0'

	all_city = [
		u'北京', u'天津', u'石家庄', u'唐山', u'秦皇岛', u'邯郸', u'保定', u'太原', u'晋中', u'呼和浩特', u'包头', u'沈阳', u'大连', u'鞍山', u'长春',
        u'吉林', u'哈尔滨', u'上海', u'南京', u'无锡', u'常州', u'苏州', u'扬州', u'杭州', u'宁波', u'温州', u'合肥', u'芜湖', u'蚌埠', u'淮南', u'安庆',
        u'福州', u'厦门', u'南昌', u'九江', u'赣州', u'吉安', u'济南', u'青岛', u'烟台', u'泰安', u'日照', u'郑州', u'洛阳', u'平顶山', u'安阳', u'武汉',
        u'宜昌', u'荆州', u'恩施', u'长沙', u'湘潭', u'广州', u'深圳', u'珠海', u'南宁', u'桂林', u'海口', u'三亚', u'重庆', u'合川', u'永川', u'成都',
        u'攀枝花', u'德阳', u'广汉', u'绵阳', u'遂宁', u'南充', u'贵阳', u'六盘水', u'遵义', u'昆明', u'拉萨', u'西安', u'宝鸡', u'咸阳', u'银川', u'香港'
	]

	def start_requests(self):
		for address in self.all_city:
			yield Request(url=self.list_url.replace('<?page?>', '1').replace('<?address?>', address),
			              callback=self.parse_list, headers=self.headers, dont_filter=True,
			              meta={'page': 1, 'address': address})

	def parse_list(self, response):
		data = response.body
		if data == '' or data == '[]':
			log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
			return
		try:
			#data = data[6:]
			#je = json.JSONEncoder().encode(data)
			js = json.loads(data)
		except Exception, e:
			log.msg(u'兼职职位列表请求结果解析异常,非json数据.cause by %s.url=%s' % (e, response.url), level = log.INFO)
			return
		if 1 == js['code']:
			for item in js['data']:
				yield Request(url=self.info_url.replace('<?id?>', item['jid']), callback=self.parse_info, headers=self.headers, dont_filter=True, meta={'jid': item['jid']})
			#下一页
			address = response.meta['address']
			if len(js['data']) == 20:
				page = response.meta['page'] + 1
				log.msg(u'采集[%s]第[%d]页' % (address, page))
				yield Request(url=self.list_url.replace('<?page?>', str(page)).replace('<?address?>', address),
				              callback=self.parse_list, headers=self.headers, dont_filter=True,
				              meta={'page': page, 'address': address})
			else:
				log.msg('采集[%s]终止' % address)
		else:
			log.msg(js['message'])

	def parse_info(self, response):
		data = response.body
		if data == '' or data == '[]':
			log.msg(format= '%(request)s post fail.response is [].', level = log.ERROR, request = response.url)
			return
		try:
			#data = data[6:]
			js = json.loads(data)
		except:
			log.msg(u'兼职职位[%s]请求结果解析异常,非json数据.url=%s' % (response.meta['jid'], response.url), level = log.INFO)
			return
		if 1 == js['code']:
			j = Job()
			for (key, value) in js['data'][0].iteritems():
				j[key] = value
			yield j
		else:
			log.msg(js['message'])
