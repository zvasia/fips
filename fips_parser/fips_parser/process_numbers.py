import argparse
import os
import sys
from fips_parser.fips_parser.settings import SQLALCHEMY_DB, DOCNUMS_FROM_SITE, DOCNUMS_FROM_DB, DOCNUMS_TO_UPDATE,\
    DATE_FROM, DATE_TO
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from fips_parser.fips_parser.model import Base, Certificate

SEARCH_URL = 'https://www1.fips.ru/publication-web/publications/' \
             'UsrTM?pageNumber={page_number}&inputSelectOIS=TM,CKTM,AOG,ERAOG,TMIR&tab=' \
             'UsrTM&searchSortSelect=dtPublish&searchSortDirection=true'
DATE_SEARCH = '&extendedFilter=true&_extendedFilter=on&registration_S={date_from}&registration_Po={date_to}'


# - get docnums from database
def get_numbers_from_db():
    date_from = datetime.strptime(DATE_FROM, '%d.%m.%Y')
    date_to = datetime.strptime(DATE_TO, '%d.%m.%Y')
    engine = db.create_engine(SQLALCHEMY_DB, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    docnums = session.query(Certificate).filter(Certificate.type == "TM",
                                                Certificate.registration_date >= str(datetime.date(date_from)),
                                                Certificate.registration_date <= str(datetime.date(date_to)))
    db_nums = [
        x.full_num for x in docnums
    ]
    for num in db_nums:
        with open(DOCNUMS_FROM_DB, 'a') as f:
            f.write(num + "\n")


# - get docnums from site, database and take difference
def get_diff_nums():
    file_site = open(DOCNUMS_FROM_SITE, "r")
    site_data = set([x[:-1] for x in file_site])
    file_site.close()
    file_db = open(DOCNUMS_FROM_DB, "r")
    db_data = set([x[:-1] for x in file_db])
    file_db.close()
    diff = site_data.difference(db_data)
    for num in diff:
        with open(DOCNUMS_TO_UPDATE, 'a') as f:
            f.write(num + "\n")


def main():
    arguments_parser = argparse.ArgumentParser()
    arguments_parser.add_argument('-diff')
    arguments_parser.add_argument('-nums_from_db')
    namespace = arguments_parser.parse_args(sys.argv[1:])
    if namespace.diff:
        get_diff_nums()
    elif namespace.nums_from_db:
        get_numbers_from_db()


if __name__ == '__main__':
    main()

