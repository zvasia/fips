# Scrapy settings for fips_parser project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'fips_parser'

SPIDER_MODULES = ['fips_parser.spiders']
NEWSPIDER_MODULE = 'fips_parser.spiders'
PROXIES_LIST = 'proxies.txt'
PROXY_LIMIT = 2
WRONG_RESPONSE = 'sadflkjsdf'
RETRY_HTTP_CODES = [500, 501, 502, 503, 504, 522, 524, 400, 403, 404, 408, 429]
RETRY_TIMES = 2


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'fips_parser (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'fips_parser.middlewares.FipsParserSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'fips_parser.middlewares.TestDownloaderMiddleware': 543,
#    'fips_parser.middlewares.FipsParserDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'fips_parser.pipelines.FipsParserPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DOCNUM_LIST_FILENAME = "numbers.txt"

SQLALCHEMY_DB = "mysql://fips-number:FipPSV&ys4#@poiskznakov.cg3pufp1yols.eu-west-1.rds.amazonaws.com:3306/ru?charset=utf8mb4"

# There fields will be updated if present on mark page.
FIELDS_TO_UPDATE = [
    "country", "application_number", "valid_until",
    "application_date", "registration_date",
    "owner", "owner_address", "status", "status_date",
    "colors", "publishing_date", "icgs"]

try:
    from fips_by_number.local_settings import *
except ImportError:
    pass