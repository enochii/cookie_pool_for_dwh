import requests
import random
from bs4 import BeautifulSoup
import time
from db_api import cookies_pool


# 代理IP的逻辑
# 建议https://github.com/jhao104/proxy_pool 
def get_proxy():
    return None


# 在这里填写user agent的逻辑
# 建议使用fake_useragent
def get_header():
    return None


class Crawler(object):
    # 某个页面最大的尝试次数
    Max_URL_Retry = 10
    Max_Cookie_Fail = 15
    # 记录某个cookie失败次数，如果超过限制次数进行删除？
    Fail_Cnt = {}

    # 当某个cookie失败时在这
    # 里登记
    # 失败次数过多通知cookie池删除
    @staticmethod
    def inc_cookie_fail(session_id : str):
        if session_id in Crawler.Fail_Cnt:
            Crawler.Fail_Cnt[session_id] += 1
            if Crawler.Fail_Cnt[session_id] > Crawler.Max_Cookie_Fail:
                Crawler.Fail_Cnt.pop(session_id)
                print('Delete ', session_id)
                cookies_pool.delete(session_id)
        else:
            Crawler.Fail_Cnt[session_id] = 1

    @staticmethod
    def reset_cookie_succ(session_id : str):
        if session_id in Crawler.Fail_Cnt:
            Crawler.Fail_Cnt[session_id] = 0

    @staticmethod
    def cache_cookies(cookiedict):
        cookies_pool.get_all()
        cookies_pool.put(cookiedict['session-id'], cookiedict)

    @staticmethod
    def update_cookies(cookiedict:dict, old_cookies:dict):
        # session_id = old_cookies['session-id']
        print('New Cookie: ', cookiedict)
        # 更新cookie池缓存
        cookies_pool.get_all()
        if 'session-id' in cookiedict:
            # 更新session-id
            # session_id = cookiedict['session-id']
            print('delete')

            cookies_pool.delete(old_cookies['session-id'])
            assert cookies_pool.get(old_cookies['session-id']) is None

        for key, val in cookiedict.items():
            old_cookies[key] = val
        Crawler.cache_cookies(old_cookies)

    def try_request(self, url: str, generate_cookie=False):
        fail_cnt = 0
        while True:
            try:
                # 根据随机数判断是否需要获取新cookie
                choice = random.randint(1, 10)
                # print('Choice : ', choice)
                if  2<=choice <=5:
                    cookie = None
                    # print('No cookie')
                else:
                    cookie = cookies_pool.get_random_cookie()

                # cookie = cookies_pool.get_random_cookie()
                # print('cookie: ', cookie)

                r = requests.get(url, headers=get_header(), timeout=10,cookies=cookie, proxies=get_proxy())

                # print('?')
                r.raise_for_status()
                soup = BeautifulSoup(r.text)
                if soup.title.string == "Robot Check":
                    print("Robot")
                    continue

                cookiejar = r.cookies
                cookiedict = requests.utils.dict_from_cookiejar(cookiejar)

                if cookie is None:
                    self.cache_cookies(cookiedict)
                else :
                    Crawler.update_cookies(cookiedict, cookie)


                # print('success!')
                fail_cnt = 0
                if cookie is not None:
                    # 一个cookie请求成功时 重置它的可失败次数
                    Crawler.reset_cookie_succ(cookie['session-id'])

                if not generate_cookie:
                    return r.text

            except Exception as e:
                # print('fail', e.__class__)
                fail_cnt += 1
                if cookie is not None:
                    Crawler.inc_cookie_fail(cookie['session-id'])

                if fail_cnt == Crawler.Max_URL_Retry:
                    return None

                if e.__class__ is KeyError:
                    print('No RETURN Cookie!')
                    # print(r.text)
                    # raise e
                elif e.__class__ is TypeError or e.__class__ is AttributeError:
                    # print(e.__traceback__)
                    raise e
                time.sleep(2)


# if __name__ == '__main__':
#     urls = load_urls()
#     crawler = Crawler()
#     crawler.try_request(urls[0],generate_cookie=True)
