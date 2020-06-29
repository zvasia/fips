import scrapy


class FipsSpider(scrapy.Spider):
    name = "fips"

    def start_requests(self):
        urls = [
            'https://www.myip.com/',
        'http://www.facebook.com',
        'http://www.baidu.com',
        'http://www.yahoo.com',
        'http://www.amazon.com',
        'http://www.wikipedia.org',
        'http://www.qq.com',
        'http://www.google.co',
                 'http://www.twitter.com',
        'http://www.live.com',
        'http://www.taobao.com',
        'http://www.bing.com',
        'http://www.instagram.com',
        'http://www.weibo.com',
        'http://www.sina.com.cn',
        'http://www.linkedin.com',
        'http://www.yahoo.co.jp',
        'http://www.msn.com',
        'http://www.vk.com',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = 'ips.txt'
        ip = str(response.xpath("//span[@id = 'ip']/text()").extract()[0])
        with open('ips.txt', 'a') as file:
            file.write(ip + "\n")
        print("\n\n\n" + str(ip) + "\n\n\n")
        self.log('Saved file %s' % filename)
