#-*- encoding=utf-8 -*-
#!/usr/bin/env python


import sys
sys.path.append('../..')
import uuid
from time import time
from jobspider.utils.tools import md5


#智联招聘http请求头e字段加密算法
class ZhaoPinHeader(object):

	API_SN = '4fc986cb1d754cd0a5bee817c48473b5'
	HOST = 'http://mi.zhaopin.com'

	def apiDynamicUrl(self, url):
		url = url.replace('<?uuid?>', str(uuid.uuid1())).replace('<?unixtime?>', str(int(time())))
		token = url.replace(ZhaoPinHeader.HOST, '').lower()
		token += ZhaoPinHeader.API_SN
		token = md5(token)
		return url + '&e=' + token


if __name__ == '__main__':
	zp = ZhaoPinHeader()
	linkUrl = 'http://mi.zhaopin.com/android/Position/Search?pageIndex=<?page?>&SF_2_100_4=<?city?>&pageSize=20&d=<?uuid?>&channel=zhilian&v=4.3&key=135486907212185&t=<?unixtime?>'
	linkUrl = linkUrl.replace('<?city?>', '765').replace('<?page?>', '1')
	print zp.apiDynamicUrl(linkUrl)
	linkUrl = 'http://mi.zhaopin.com/android/Position/Detail?channel=zhilian&d=<?uuid?>&key=135486907212185&number=<?number?>&v=4.3&t=<?unixtime?>'
	linkUrl = linkUrl.replace('<?number?>', 'CC535117221J90250181000')
	print zp.apiDynamicUrl(linkUrl)
