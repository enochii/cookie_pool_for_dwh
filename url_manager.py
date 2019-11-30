# 对所有需要爬取的电影的url进行管理
from redis import Redis, BlockingConnectionPool
from config import URL_HOST, URL_PORT


class URLManager(object):
    def __init__(self, host, port, db=0):
        """
        init
        :param host: host
        :param port: port
        :return:
        """
        self.origin_ids = 'movieID'
        self.fail_ids = 'failID'
        self.succ_ids = 'succID'
        self.extracted_ids = 'extractedID'

        self.conn = Redis(connection_pool=BlockingConnectionPool(host=host, port=port, db=db))
        self.data = self.conn.smembers(self.origin_ids)

    def pop(self) -> str:
        raw_id = self.data.pop()
        if raw_id is None:
            return None

        rid = raw_id.decode('utf-8')
        self.conn.srem(self.origin_ids, rid)

        return rid

    def fail(self, product_id : str):
        self.conn.sadd(self.fail_ids, product_id)

    def succ(self, product_id : str):
        self.conn.sadd(self.succ_ids, product_id)

    def extracted(self, product_id : str):
        self.conn.sadd(self.extracted_ids, product_id)


URL_manager = URLManager(URL_HOST, URL_PORT)