# -*- coding:utf-8 -*-

import pyDes


class DesHelper(object):
    """des加密工具类
    """
    def __init__(self, key):
        self._des = pyDes.des(key, pyDes.CBC, key, pad=None, padmode=pyDes.PAD_PKCS5)

    def encrypt(self, plain):
        return self._des.encrypt(plain).hex()

    def decrypt(self, cipher):
        return self._des.decrypt(bytes.fromhex(cipher))

