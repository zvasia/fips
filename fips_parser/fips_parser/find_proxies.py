import asyncio
from proxybroker import Broker
from .settings import PROXY_LIMIT


async def save(proxies, filename):
    """Save proxies to a file."""
    with open(filename, 'w') as f:
        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            proto = 'https' if 'HTTPS' in proxy.types else 'http'
            row = '%s://%s:%d\n' % (proto, proxy.host, proxy.port)
            f.write(row)
            print(row)


def main():
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    types = ['HTTP', 'HTTPS']
    tasks = asyncio.gather(broker.find(types=types, limit=PROXY_LIMIT),
                           save(proxies, filename='proxies.txt'))
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait_for(tasks, 60))
    except asyncio.TimeoutError:
        print("RETRYING PROXIES ...")


if __name__ == '__main__':
    main()


