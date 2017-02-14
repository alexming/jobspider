# -*- coding: utf-8 -*-


from base64 import b64encode, b64decode
from Crypto.Cipher import DES


PADDING = '\0'
#mode = DES/CBC/PKCS5Padding
pad_it = lambda s: s + (8 - len(s) % 8) * PADDING

class GanJiDES(object):

    #加密秘钥
    _key = b64decode(u'aS5IM3ZCLHo=')
    #加密向量
    _iv  = b'\x12\x34\x56\x78\x90\xAB\xCD\xEF'

    def encrypt(self, data):
        generator = DES.new(self._key, DES.MODE_CBC, self._iv)
        crypt = generator.encrypt(pad_it(data))
        return b64encode(crypt)

    def decrypt(self, data):
        generator = DES.new(self._key, DES.MODE_CBC, self._iv)
        recovery = generator.decrypt(b64decode(data))
        return recovery.rstrip('\0\3\4\5\6\b')
