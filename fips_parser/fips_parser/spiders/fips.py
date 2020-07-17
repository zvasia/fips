import scrapy
from venv import logger
from ..settings import DOCNUMS_TO_UPDATE


class DocsSpider(scrapy.Spider):
    name = "docs_from_fips"
    wrong_response = "Слишком быстрый просмотр документов."

    url_fmt = {
        'TM': 'https://www1.fips.ru/fips_servl/fips_servlet?DB=RUTM&DocNumber={docnum}&TypeFile=html',
        'GP': 'https://www1.fips.ru/fips_servl/fips_servlet?DB=RUGP&DocNumber={docnum}&TypeFile=html',
        'WK': 'https://www1.fips.ru/fips_servl/fips_servlet?DB=WKTM&DocNumber={docnum}&TypeFile=html',
    }

    fields = {
        "priority": '//p[@class="bib2"]/b/text()',
        "country": 'table/tr/td[contains(text(), "(190)")]/following-sibling::td[1]/div/text()',
        "status_str": 'table/tr[@class="Status"]/td/text()',
        "image_url": 'p/a/img/@src',
        "application_number": 'table/tr/td/p[contains(text(), "(210)")]/b/a/text()',
        "valid_until": 'table/tr/td/p[contains(text(), "(181)")]/b/text()',
        "application_date": 'table/tr/td/p[contains(text(), "(220)")]/b/text()',
        "registration_date": 'table/tr/td/p[contains(text(), "(151)")]/b/text()',
        "publishing_date": 'table/tr/td/p[contains(text(), "(450)")]/b/a/text()',
        "pdf_url": 'table/tr/td/p[contains(text(), "(450)")]/b/a/@href',
        "colors": 'p[contains(text(), "(591)")][1]/b/text()',
        "owner": 'p[contains(text(), "(732)")][1]/b/text()',
        "owner_address": 'p[contains(text(), "(750)")][1]/b/text()',
        "icgs": 'p[contains(text(), "(511)")]/b/text()',
    }

    def __init__(self, filename=None, target='TM', *args, **kwargs):
        super(DocsSpider, self).__init__(*args, **kwargs)
        self.filename = filename
        self.target_type = target

        # final stat
        self.requests_total = 0
        self.requests_success = 0
        self.requests_invalid_data = 0
        self.requests_invalid_docnums = []

        if self.target_type not in self.url_fmt:
            raise Exception('Invalid target type: %s' % (self.target_type, ))

    def get_numbers(self):
        filename = DOCNUMS_TO_UPDATE
        with open(filename) as fd:
            for line in fd.readlines():
                for num in line.split(','):
                    self.requests_total += 1
                    yield num.strip()

    def check_proxy_response(self, response):
        if self.wrong_response in response.body.decode('cp1251'):
            logger.info('Verification failed with response: ' + response.body.decode('cp1251'))
            return False
        return True

    def start_requests(self):
        for docnum in self.get_numbers():
            yield scrapy.Request(url=self.url_fmt[self.target_type].format(docnum=docnum),
                                 meta={
                                     'docnum': docnum, 'type': self.target_type,
                                     'check_callback': self.check_proxy_response, 'proxy_object': ''
                                 },
                                 callback=self.parse, dont_filter=True)

    def parse(self, response):
        main_block = response.xpath('//div[contains(@id, "mainDoc")]')
        item = {"number": response.request.meta['docnum'], "type": response.request.meta['type']}

        for field, xpath_expr in self.fields.items():
            values = main_block.xpath(xpath_expr).extract()
            if values:
                if len(values) > 1:
                    item[field] = [val.strip() for val in values]
                else:
                    item[field] = values[0].strip()

        if len(item) > 2:
            self.requests_success += 1
            yield item
        else:
            # retry
            self.requests_invalid_data += 1
            self.requests_invalid_docnums.append(response.request.meta['docnum'])
        #     """
        #     yield scrapy.Request(response.url, callback=self.parse, dont_filter=True,
        #                          meta={
        #                             'docnum': response.request.meta['docnum'],
        #                             'type': response.request.meta['type']
        #                          })
        #     """

