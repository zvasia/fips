import asyncio
import random
import aiohttp
import logging
from datetime import datetime, timedelta
from proxybroker import Broker
from proxybroker.resolver import Resolver
from proxybroker.utils import log
from .settings import PROXY_LIMIT


MIN_PROXY_RATING = -3


# its here to fix ProxyBroker bug
class ResolverCustom(Resolver):
    _temp_host = []

    def _pop_random_ip_host(self):

        host = random.choice(self._temp_host)
        self._temp_host.remove(host)
        return host

    async def get_real_ext_ip(self):
        self._temp_host = self._ip_hosts.copy()
        while self._temp_host:
            try:
                timeout = aiohttp.ClientTimeout(total=self._timeout)
                async with aiohttp.ClientSession(
                        timeout=timeout, loop=self._loop,
                        connector=aiohttp.TCPConnector(verify_ssl=False)
                ) as session, session.get(self._pop_random_ip_host()) as resp:
                    ip = await resp.text()
            except asyncio.TimeoutError:
                pass
            else:
                ip = ip.strip()
                if self.host_is_ip(ip):
                    log.debug('Real external IP: %s', ip)
                    break
        else:
            raise RuntimeError('Could not get the external IP')
        return ip


class ProxyStorage(object):
    def __init__(self):
        try:
            open('proxy_ban_list.txt', 'r')
        except IOError:
            open('proxy_ban_list.txt', 'w')
        address_list = []
        self.proxies = []
        self.find_proxies(address_list)
        self.get_proxy_objects(address_list)

    def get_proxy_objects(self, list):
        for proxy in list:
            self.proxies.append(ProxyState(proxy))

    def get_random_proxy(self, list):
        # ban all proxy with lower then min rating
        for p in list:
            if p.rating < MIN_PROXY_RATING:
                self.ban_proxy(p.address)
                list.remove(p)
        ready_to_use = []

        # filter by cooldown and availability
        for p in list:
            if p.ready_to_use(5) and p.available:
                ready_to_use.append(p)
        if len(ready_to_use) < 1:
            return None
        x = random.choice(ready_to_use)

        # set availability and cooldown to fix proxy to request
        x.time_of_last_use = datetime.now()
        x.available = False
        return x

    def ban_proxy(self, proxy):
        logging.info('Ban to ' + str(proxy))
        filename = 'proxy_ban_list.txt'
        with open(filename, 'a') as f:
            f.write(proxy)

    def in_ban_list(self, address):
        file = open("proxy_ban_list.txt", "r")
        ban_list = file.readlines()
        if address in ban_list:
            logging.info('Proxy already in ban-list: ' + str(address))
            return True
        else:
            return False

    async def format_proxy(self, proxies, list):
        """Save proxies."""
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            proto = 'https' if 'HTTPS' in proxy.types else 'http'
            row = '%s://%s:%d\n' % (proto, proxy.host, proxy.port)
            self.add_proxy(row, list)

    def add_proxy(self, address, list):
        if self.in_ban_list(address) is False:
            if address not in self.proxies:
                list.append(address)
                logging.info('Add proxy: ' + address)

    def find_proxies(self, list):
        proxies = asyncio.Queue()
        broker = Broker(proxies)
        broker._resolver = ResolverCustom()
        types = ['HTTP', 'HTTPS']
        tasks = asyncio.gather(broker.find(types=types, limit=PROXY_LIMIT),
                               self.format_proxy(proxies, list))
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait_for(tasks, 60))
        except asyncio.TimeoutError:
            print("RETRYING PROXIES ...")


    def get_proxy(self):
        random_proxy = self.get_random_proxy(self.proxies)
        while random_proxy is None:
            address_list = []
            self.find_proxies(address_list)
            self.get_proxy_objects(address_list)
            random_proxy = self.get_random_proxy(self.proxies)
        print('Quantity of alive proxies in list: ' + str(len(self.proxies)))
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
        if current_delta > timedelta(seconds=cooldown_in_seconds):
            return True
        else:
            return False

    def get_proxy_state(self):
        print('\nAvailable: ' + str(self.available))
        print('Rating: ' + str(self.rating))
        print('Time of use: ' + str(self.time_of_last_use))
        print('Adress: ' + str(self.address))


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
