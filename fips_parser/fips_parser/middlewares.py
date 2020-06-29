# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import sys
from datetime import datetime, timedelta

from scrapy import signals
import random
# useful for handling different item types with a single interface
from .find_proxies import main as get_new_proxy
from .settings import PROXIES_LIST, RETRY_HTTP_CODES


class TestDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self, auth_encoding, proxy_list, wrong_response):
        self.auth_encoding = auth_encoding
        self.proxies = get_proxy_objects(proxy_list)
        self.wrong_response = wrong_response

    @classmethod
    def from_crawler(cls, crawler):
        wrong_response = crawler.settings.get('WRONG_RESPONSE')
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING')
        proxy_list = get_new_proxy_list()
        s = cls(auth_encoding=auth_encoding, proxy_list=proxy_list, wrong_response=wrong_response)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # filter proxy list
        valid_proxies = []
        for x in self.proxies:
            if x.timedelta(timedelta(seconds=15)) and x.rating > -3:
                valid_proxies.append(x)
        if len(valid_proxies) < 1:
            print("No active proxies")
            self.proxies = get_new_proxy_list()
            random_proxy = get_random_proxy(self.proxies)
        else:
            random_proxy = get_random_proxy(valid_proxies)
        random_proxy.set_last_use(datetime.now())
        print('Это запрос и random proxy: ' + str(random_proxy.address))
        # send request
        request.meta['proxy'] = random_proxy.address

    def process_response(self, request, response, spider):
        proxy = request.meta['proxy']
        for x in self.proxies:
            if x.address == proxy:
                proxy = x
        print(response.status)
        if response.status == 200:
            # сравниваем с ошибочным ответом
            if request.meta.get('wrong_response') == self.wrong_response:
                # сильно понижаем рейт
                proxy.set_rating(proxy.rating - 2)
        # TODO else if запрос отвалился по таймауту - понижаем рейтинг
        elif response.status in RETRY_HTTP_CODES:
            proxy.set_rating(proxy.rating - 1)
            request.meta['proxy'] = get_random_proxy(self.proxies)
        # Called with the response returned from the downloader.
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


def get_proxy_objects(proxies):
    proxy_list = []
    for proxy in proxies:
        proxy_list.append(ProxyState(proxy))
    return proxy_list


def get_random_proxy(list):
    x = random.choice(list)
    return x


def get_new_proxy_list():
    get_new_proxy()
    proxy_path = PROXIES_LIST
    with open(proxy_path, 'r', encoding='utf8') as f:
        proxy_list = [line.strip() for line in f if line.strip()]
    return proxy_list


class ProxyState(object):
    def __init__(self, address_from_list):
        self.address = address_from_list
        self.rating = 0
        self.response_time = 0
        self.time_of_last_use = datetime.now()
        self.request_counter = 0

    def set_rating(self, new_rating):
        self.rating = new_rating

    def set_response_time(self, response_time):
        self.response_time = response_time

    def set_last_use(self, time):
        self.time_of_last_use = time

    def increase_request_counter(self):
        self.request_counter += 1

    def timedelta(self, delta):
        current_delta = datetime.now() - self.time_of_last_use
        if current_delta < delta:
            return True
        else:
            return False




# 2) Вместо однократного сбора списка прокси нужен постоянно действующий механизм ранжирования. Получаем список
# прокси, ставим каждому нулевой рейтинг. Затем при каждом запросе страницы:
#     1. Берём текущий список прокси
#     2. Отбрасываем те, которые использовали менее 15 секунд назад (чтобы слишком часто не использовать
#     один и тот же адрес)
#     3. Отбрасываем те, у которых слишком маленький рейтинг (например < -3)
#     4. Из оставшихся выбираем случайный, делаем запрос. Если ответ не пришёл - снижаем рейтинг, если
#     пришёл не тот, что ожидаем - снижаем ещё сильнее.  А если всё нормально - увеличиваем.
#     5. Если в списке остаётся совсем мало проксей с положительным рейтингом - запрашиваем список бесплатных
#     прокси ещё раз.