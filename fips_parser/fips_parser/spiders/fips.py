import scrapy


class FipsSpider(scrapy.Spider):
    name = "fips"

    wrong_response = "Слишком быстрый просмотр документов."

    def check_proxy_response(self, response, request):
        p = request.meta['proxy_object']
        if self.wrong_response in response.body.decode('cp1251'):
            print(response.body.decode('cp1251') + '\n\n' + 'ПРОВЕРКА НЕ ПРОЙДЕНА' + '\n\n')
            return False
        p.rating = p.rating + 1
        return True

    def start_requests(self):
        urls = []
        for num in range(190000, 190020):
            urls.append('https://www1.fips.ru/fips_servl/fips_servlet?DB=RUTM&DocNumber={}&TypeFile=html'.format(num))

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"check_callback": self.check_proxy_response,
                                                                     "proxy_object": ''},
                                 dont_filter=True)

    def parse(self, response):
        ip = str(response.css("p.bib>b>a::text").extract())
        with open('ips.txt', 'a') as file:
            file.write(ip + "\n")
        print(ip)
