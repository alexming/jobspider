#-*- encoding=utf-8 -*-
#!/usr/bin/env python


import sys
sys.path.append('../..')
import urlparse
import random
from jobspider.utils.tools import md5


#百姓网http请求头BAIP-HASH字段加密算法
class BaixHeader(object):

    API_SECRET = 'c6dd9d408c0bcbeda381d42955e08a3f'
    _CHARACTORS_16 = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']

    #默认token为空,只针对http-get请求,postParam为空
    def apiDynamicHash(self, url, token = '', postParam = ''):
        #获取android的16位32进制udid
        udid = self._apiDynamicUDID()
        #解析url请求,去除protocol与host
        urlTuple = urlparse.urlparse(url)
        htmlQuery = urlTuple.path + '?' + urlTuple.query
        #原始串拼接
        originalString = udid + token + htmlQuery + postParam + BaixHeader.API_SECRET + udid
        encryptionString = md5(originalString)
        #
        return {'BAPI-NONCE': udid, 'UDID': udid, 'BAPI-HASH': encryptionString}

    def _apiDynamicUDID(self):
        #从源列表随机获取16个16进制字符列表
        list16 = random.sample(BaixHeader._CHARACTORS_16, 16)
        #转换为字符串
        return ''.join(list16)


if __name__ == '__main__':
    bx = BaixHeader()
    print bx.apiDynamicHash('http://www.baixing.com/api/mobile/gongzuo/ad?apiFormatter=AdList&suggestOn=1&area=m250&from=0&size=30')
    #print bx.apiDynamicHash('http://www.baixing.com/api/mobile/gongren/ad?apiFormatter=AdList&suggestOn=1&area=m250&from=0&size=30')
