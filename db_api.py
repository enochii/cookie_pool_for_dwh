from redis.connection import BlockingConnectionPool
from redis import Redis

from config import *
import random


class CookiesPool(object):
    def __init__(self, name, host, port, db=2):
        """
        init
        :param name: hash name
        :param host: host
        :param port: port
        :param password: password
        :return:
        """
        self.name = name
        self.conn = Redis(connection_pool=BlockingConnectionPool(host=host, port=port, db=db))
        # 当加入一定量的新cookie后删除老化的cookie
        self.put_cnt = 0
        self.get_cnt = 0
        self.cache = None

    def get(self, session_id):
        data = self.conn.hget(name=self.name, key=session_id)
        return self.__str_to_dict(data) if data is not None else None

    @staticmethod
    def __str_to_dict(cookie_dump: str):
        infos = cookie_dump.split(' ')
        cookies = {}
        for i in range(len(infos) // 2):
            cookies[infos[i * 2]] = infos[i * 2 + 1]
        return cookies

    @staticmethod
    def __dict2str(cookies:dict):
        dump = ''
        for key, val in cookies.items():
            dump += key
            dump += ' '
            dump += val
            dump += ' '

        return dump

    def put(self, session_id, cookies):
        self.put_cnt = self.put_cnt+1
        if self.put_cnt >= 10 :
            self.put_cnt = 0
            # TODO : delete some cookie

        return self.conn.hset(self.name, session_id, self.__dict2str(cookies))

    def delete(self, session_id):
        self.conn.hdel(self.name, session_id)

    def get_all(self):
        if self.cache is None:
            raw_items = self.conn.hgetall(self.name)
            self.cache = []
            # print(raw_items)
            for val in raw_items.values():
                self.cache.append(val.decode('utf8'))
        return self.cache

    def get_random_cookie(self):
        self.get_cnt = self.get_cnt + 1
        # 获取多次后，重新从数据库获取数据，更新缓存
        if self.cache is None or self.get_cnt >= 6:
            self.get_cnt = 0
            self.get_all()

        if len(self.cache) == 0:
            return None

        raw_cookie = random.choice(self.cache)
        return self.__str_to_dict(str(raw_cookie))


cookies_pool = CookiesPool(name='session', host=COOKIE_HOST, port=COOKIE_PORT, db=2)