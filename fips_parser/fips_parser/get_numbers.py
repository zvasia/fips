import argparse
import sys
import lxml.html
import xml.etree.ElementTree as ET
import requests

SEARCH_URL = 'https://www1.fips.ru/publication-web/publications/' \
             'UsrTM?pageNumber={page_number}&inputSelectOIS=TM,CKTM,AOG,ERAOG,TMIR&tab=' \
             'UsrTM&searchSortSelect=dtPublish&searchSortDirection=true'
DATE_SEARCH = '&extendedFilter=true&_extendedFilter=on&registration_S={date_from}&registration_Po={date_to}'


# - get docnums from site with date params
def get_numbers_from_site(date_from, date_to):
    print(SEARCH_URL.format(page_number=1) + DATE_SEARCH.format(date_from=date_from, date_to=date_to))
    r = requests.get((SEARCH_URL.format(page_number=1) + DATE_SEARCH.format(date_from=date_from, date_to=date_to)),
                     'lxml', verify=False)
    html = lxml.html.fromstring(r.text)
    total_pages = html.xpath("//div[@class='modern-page-navigation']/a[7]/text()")[0].split(' ')
    total_pages = total_pages[16].split('\\')
    total_pages = int(total_pages[0])
    docnums = html.xpath("//td[@class='nowrap']/a/text()")
    print(docnums)
    print(total_pages)
    if total_pages > 1:
        for page in range(5):
            print(page)
            # page = 2
            r = requests.get((SEARCH_URL.format(page_number=page) + DATE_SEARCH.format(date_from=date_from, date_to=date_to)),
                             'lxml', verify=False)
            html = lxml.html.fromstring(r.text)
            docnums = html.xpath("//td[@class='nowrap']/a/text()")
            print(str(page) + ' done')

    print(len(docnums))
    for num in docnums:
        num = num.strip()
        num = num.split(' ')
        num = num.pop()
        print(num)

# - получение номеров из нашей базы - чтобы все наши знаки имели актуальную инфу
def get_number_from_db():
    pass


# - запуск поиска на сайте, потом сравнивание ответа с базой (аналогично Ромарину) - чтобы быстро
# добавить в базу те знаки, которых у нас нет
def add_diff_data():
    pass


def main(urllib2=None):
    # arguments_parser = argparse.ArgumentParser()
    # arguments_parser.add_argument('-df', default='*')  # date_from
    # arguments_parser.add_argument('-dt', default='*')  # date_to
    # arguments_parser.add_argument('-p', default='1')
    # namespace = arguments_parser.parse_args(sys.argv[1:])
    # date_from = namespace.df
    # date_to = namespace.dt
    # start_page = int(namespace.p)

    get_numbers_from_site('15.05.2011', '15.08.2011')


if __name__ == "__main__":
    main()

