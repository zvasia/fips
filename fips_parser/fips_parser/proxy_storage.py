import asyncio
import random
from datetime import datetime, timedelta
from proxybroker import Broker
from .settings import PROXY_LIMIT


class ProxyStorage(object):
    def __init__(self):
        try:
            open('proxy_ban_list.txt', 'r')
        except IOError:
            open('proxy_ban_list.txt', 'w')
        self.proxies = self.get_new_proxies()

    def get_proxy_objects(self, list):
        # TODO итератор
        proxy_list = []
        for proxy in list:
            proxy_list.append(ProxyState(proxy))
        return proxy_list

    def get_random_proxy(self, list):
        # TODO использовать итераторы
        for p in list:
            if p.rating < -3:
                self.ban_proxy(p.address)
                list.remove(p)
        ready_to_use = []
        for p in list:
            if p.ready_to_use(5) and p.available:
                ready_to_use.append(p)
        if len(ready_to_use) < 1:
            print('не осталось подходящих адресов')
            return None
        x = random.choice(ready_to_use)
        x.time_of_last_use = datetime.now()
        x.available = False
        return x

    def add_proxy(self, address, list):
        if self.in_ban_list(address) is False:
            if address not in list:
                list.append(address)
                print('add_proxy ' + address)
        else:
            print(address + ' in ban list')

    def ban_proxy(self, proxy):
        print('баним ' + proxy)
        filename = 'proxy_ban_list.txt'
        with open(filename, 'a') as f:
            f.write(proxy)

    def in_ban_list(self, address):
        file = open("proxy_ban_list.txt", "r")
        ban_list = file.readlines()
        if address in ban_list:
            return True
        else:
            return False

    async def save_proxy(self, proxies, list):
        """Save proxies."""
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            proto = 'https' if 'HTTPS' in proxy.types else 'http'
            row = '%s://%s:%d\n' % (proto, proxy.host, proxy.port)
            self.add_proxy(row, list)

    def find_proxies(self, list):
        proxies = asyncio.Queue()
        broker = Broker(proxies)
        types = ['HTTP', 'HTTPS']
        tasks = asyncio.gather(broker.find(types=types, limit=PROXY_LIMIT),
                               self.save_proxy(proxies, list))
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait_for(tasks, 60))
        except asyncio.TimeoutError:
            print("RETRYING PROXIES ...")
        return list

    def get_new_proxies(self):
        proxy_list = []
        self.find_proxies(proxy_list)
        return self.get_proxy_objects(proxy_list)

    def get_proxy(self):
        random_proxy = self.get_random_proxy(self.proxies)
        while random_proxy is None:
            self.get_new_proxies()
            random_proxy = self.get_random_proxy(self.proxies)
        print('АКТУАЛЬНЫЕ АДРЕСА')
        print(len(self.proxies))
        # for i in self.proxies:
        #     i.get_proxy_state()
        print('ОТДАЕМ ПРОКСИ')
        return random_proxy


class ProxyState(object):
    def __init__(self, address_from_list):
        self.available = True
        self.address = address_from_list
        self.rating = 0
        self.response_time = 0
        self.time_of_last_use = datetime.now()

    def ready_to_use(self, cooldown_in_seconds):
        current_delta = datetime.now() - self.time_of_last_use
        if current_delta < timedelta(seconds=cooldown_in_seconds):
            return True
        else:
            return False

    def get_proxy_state(self):
        print('\n' + str(self.available))
        print(self.rating)
        print(self.time_of_last_use)
        print(self.address)


# def main():
#     storage = ProxyStorage()
#     p = storage.get_proxy()
#     print('p1')
#     print(p.rating)
#     print(p.time_of_last_use)
#     print(p.address)
#     p.rating = -4
#     print(p.rating)
#     p2 = storage.get_proxy()
#     print('p2')
#     print(p2.rating)
#     print(p2.time_of_last_use)
#     print(p2.address)
#     p2.rating = -5
#     p3 = storage.get_proxy()
#     print('p3')
#     print(p3.rating)
#     print(p3.time_of_last_use)
#     print(p3.address)
#
#
# if __name__ == '__main__':
#     main()
