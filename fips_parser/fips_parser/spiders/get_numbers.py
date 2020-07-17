import lxml.html
import requests
import scrapy
from ..settings import SEARCH_URL, DATE_SEARCH, DATE_FROM, DATE_TO, DOCNUMS_FROM_SITE


class FipsSearchSpider(scrapy.Spider):
    name = "nums_from_fips"

    # check response and increase proxy rating
    def check_proxy_response(self, response):
        if response.status == 200:
            return True
        return False

    def start_requests(self):

        # get count of pages
        r = requests.get((SEARCH_URL.format(page_number=1) +
                          DATE_SEARCH.format(date_from=DATE_FROM, date_to=DATE_TO)),
                         'lxml', verify=False)
        html = lxml.html.fromstring(r.text)
        total_pages = html.xpath("//div[@class='modern-page-navigation']/a[7]/text()")[0].split(' ')
        total_pages = total_pages[16].split('\\')
        total_pages = int(total_pages[0])

        # generate urls and requests
        for page in range(1, total_pages + 1):
            url = SEARCH_URL.format(page_number=page) \
                  + DATE_SEARCH.format(date_from=DATE_FROM, date_to=DATE_TO)
            yield scrapy.Request(url=url, callback=self.parse, meta={"check_callback": self.check_proxy_response,
                                                                     "proxy_object": ''}, dont_filter=True)

    def parse(self, response):
        docnums = response.xpath("//td[@class='nowrap']/a/text()").extract()
        for num in docnums:
            num = num.strip()
            num = num.split(' ')
            num = num.pop()
            print(num)

            try:
                with open('nums.txt', 'a') as f:
                    f.write(num + '\n')
            except IOError:
                open(DOCNUMS_FROM_SITE, 'w')
                with open('nums.txt', 'a') as f:
                    f.write(num + '\n')
