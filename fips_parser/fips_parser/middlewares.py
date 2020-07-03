# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from datetime import datetime, timedelta
from venv import logger

from scrapy import signals
from twisted.internet.error import TCPTimedOutError

from .settings import RETRY_HTTP_CODES
from .proxy_storage import ProxyStorage


class TestDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self, auth_encoding, check_callback):
        self.auth_encoding = auth_encoding
        self.proxy_storage = ProxyStorage()

    @classmethod
    def from_crawler(cls, crawler):
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING')
        s = cls(auth_encoding=auth_encoding, check_callback='')
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        proxy_object = self.proxy_storage.get_proxy()
        request.meta['proxy_object'] = proxy_object
        request.meta['proxy'] = proxy_object.address
        print("\nЗАПРОС")
        proxy_object.get_proxy_state()
        return None

    def process_response(self, request, response, spider):
        print('ОТВЕТ')
        check_response = request.meta['check_callback']
        if check_response(response, request) is True:
            p = request.meta['proxy_object']
            p.available = True
            return response
        else:
            # return request.copy()
            self.retry(request, -2, spider)

        # Called with the response returned from the downloader.
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest

    def process_exception(self, request, exception, spider):
        return self.retry(request, -1, spider)
        # if isinstance(exception, TimeoutError) or isinstance(exception, TCPTimedOutError):
        #     return self.retry(request, -1, spider)
        # else:
        #     print('ЭТО ИСКЛЮЧЕНИЕ МЫ НЕ ВОЗВРАЩАЕМ')

        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def retry(self, request, reason, spider):
        print('ПОВТОР ЗАПРОСА')
        p = request.meta['proxy_object']
        p.available = True
        p.rating = p.rating + reason
        print("МЕНЯЕМ РЕЙТИНГ НА " + str(p.rating))
        p.get_proxy_state()
        retryreq = request.copy()
        print('ПОЛУЧАЕМ НОВЫЙ ПРОКСИ')
        proxy_object = self.proxy_storage.get_proxy()
        retryreq.meta['proxy_object'] = proxy_object
        retryreq.meta['proxy'] = proxy_object.address
        print(proxy_object.get_proxy_state())
        print('ОТПРАВЛЯЕМ ПОВТОРНЫЙ ЗАПРОС')
        return retryreq
