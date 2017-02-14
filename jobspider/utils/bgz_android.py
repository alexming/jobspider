# -*- coding: utf-8 -*-


import random
#from tools import md5
import hashlib


def md5(sourcestr):
    return hashlib.md5(sourcestr).hexdigest()


class BGZAndroidID(object):

    _CHARACTORS_16 = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    _CHARACTORS_32 = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

    @staticmethod
    def _random16():
        #从源列表随机获取12个32进制字符
        return random.choice(BGZAndroidID._CHARACTORS_16)

    @staticmethod
    def _random32():
        #从源列表随机获取12个32进制字符列表
        list32 = random.sample(BGZAndroidID._CHARACTORS_32, 12)
        #转换为字符串
        return ''.join(list32)

    @staticmethod
    def instrumentId():
        str16 = BGZAndroidID._random16()
        str32 = BGZAndroidID._random32()
        #
        s1 = str16 + str32
        s2 = md5(s1 + '*')
        s2 = s2.lower()
        s3 = s2[-6 + len(s2): ]
        s0 = 'x' + s3 + s1
        return s0

if __name__ == '__main__':
    print BGZAndroidID.instrumentId()
