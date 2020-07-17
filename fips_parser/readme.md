


# 1 Search nums on fips site
To start scrapying docnums by date start in shell: 
    cd fips_parser/fips_parser
    scrapy crawl nums_from_fips

Options:
    DOCNUMS_FROM_SITE - output file;
    DATE_FROM - start date;
    DATE_TO - finish date;

# 2 Search nums in DB
To get docnums from DB start 'process_numbers.py' with '-nums_from_db' param

Options:
    DOCNUMS_FROM_DB - output file;
    DATE_FROM - start date;
    DATE_TO - finish date;

# 3 Get difference
To get difference between numbers from DB and site start 'process_numbers.py' with '-diff' param
Options:
    DOCNUMS_FROM_SITE - file with nums from fips
    DOCNUMS_FROM_DB - file with nums from DB
    DOCNUMS_TO_UPDATE - output file

# 4 Create/update TMs
To start scrapying docnums by date start in shell: 
    cd fips_parser/fips_parser
    scrapy crawl docs_from_fips
Options:
    DOCNUMS_TO_UPDATE - input file