# -*- coding:utf-8 -*-

import shelve


class LocalDb(object):
    """本地数据库类
    """
    def __init__(self, db_path):
        self._db_path = db_path

    def write_dict(self, dic):
        with shelve.open(self._db_path) as db:
            for k, v in dic.items():
                if k is None or v is None:
                    continue
                db[k] = v

    def put(self, k, v):
        with shelve.open(self._db_path) as db:
            db[k] = v

    def get(self, k):
        with shelve.open(self._db_path) as db:
            return db.get(k)

    def keys(self):
        with shelve.open(self._db_path) as db:
            # db.keys()的返回值不能直接返回, 因为返回的是一个生成器, 获取key的值要求db一直出于开启状态
            # 返回后db会关闭, 因此通过yield返回数据，保存db开启的状态
            for key in db.keys():
                yield key

