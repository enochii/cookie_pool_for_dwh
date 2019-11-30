import time
from os import path
import threading

from url_manager import URL_manager
from cookie_caching import Crawler


def store_pages(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)


PAGES_PREFIX = path.join(path.abspath(path.join('..', '..')),'data','pages')


def crawl_one_page(crawler : Crawler):
    product_id = URL_manager.pop()
    if product_id is None:
        print('Empty DB')
        # 当数据库为空时返回
        return False

    url = 'https://www.amazon.com/dp/' + product_id
    print(url)
    try:
        text = crawler.try_request(url=url)
        if text is None:
            print('fail ', product_id)
            URL_manager.fail(product_id)
        else:
            print('success ', product_id)
            URL_manager.succ(product_id)
            # with open(path.join(PAGES_PREFIX, product_id + '.html'), 'w', encoding='utf-8') as f:
            #     f.write(text)
            filename = path.join(PAGES_PREFIX, product_id + '.html')
            store_pages(filename, text)
    except Exception as e:
        print('fail')
        if product_id is not None:
            URL_manager.fail(product_id)

    return True


class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.crawler = Crawler()

    def run(self):
        # TODO: Config
        # 要一直跑改为`while True:`
        for i in range(5):
            if crawl_one_page(self.crawler) is False:
                return


if __name__ == '__main__':
    # print('Hello')
    # print(PAGES_PREFIX)
    threads = []

    time_start = time.time()
    # TODO: Config
    # 线程数为5
    THREAD_NUM = 16
    for i in range(THREAD_NUM):
        threads.append(MyThread())
        threads[i].start()

    for i in range(THREAD_NUM):
        threads[i].join()

    time_end = time.time()
    print('Total time ', (time_end - time_start) /60, ' minutes')