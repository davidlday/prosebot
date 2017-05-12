# -*- coding: utf-8 -*-

# Scrapy settings for prosebot project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'prosebot'

SPIDER_MODULES = ['prosebot.spiders']
NEWSPIDER_MODULE = 'prosebot.spiders'
LOG_LEVEL = 'WARN'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'prosebot (+https://www.prosegrinder.com)'

# Randomize Download Delay
RANDOMIZE_DOWNLOAD_DELAY = True

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
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
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'prosebot.middlewares.ProsebotSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'prosebot.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'prosebot.pipelines.BookwormRestApiPipeline':   100,
#    'prosebot.pipelines.ProsebotPipeline': 300,
    'scrapysolr.SolrPipeline':                      500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPCACHE_POLICY ='scrapy.extensions.httpcache.RFC2616Policy'

# BookwormRestApiPipeline Configuration
BOOKWORM_REST_URI = 'http://localhost:8080/analysis' # Dropwizard Rest Service

# ScrapySolr Configuration
SOLR_URL = 'http://localhost:8983/solr/shortstories'
SOLR_MAPPING = {
    'id':   'url',

    'url':            'url',
    'magazine':	      'magazine',
    'pub_date':	      'pub_date',
    'title':          'title',
    'author':         'author',
    'genre':          'genre',
    'original_tags':	'original_tags',
    'text':           'text',

    'avg_syllables_per_word':	'avg_syllables_per_word',
    'avg_words_per_sentence': 'avg_words_per_sentence',
    'complex_word_count':	'complex_word_count',
    'dialogue_syllable_count':	'dialogue_syllable_count',
    'dialogue_syllable_percentage':	'dialogue_syllable_percentage',
    'dialogue_unique_word_count':	'dialogue_unique_word_count',
    'dialogue_word_count':	'dialogue_word_count',
    'dialogue_word_percentage':	'dialogue_word_percentage',
    'long_word_count': 'long_word_count',
    'narrative_syllable_count':	'narrative_syllable_count',
    'narrative_unique_word_count': 'narrative_unique_word_count',
    'narrative_word_count':	'narrative_word_count',
    'paragraph_count': 'paragraph_count',
    'pov':	'pov',
    'sentence_count': 'sentence_count',
    'syllable_count':	'syllable_count',
    'unique_word_count':	'unique_word_count',
    'unique_words':	'unique_words',
    'word_count': 'word_count',

    'automated_readability_index':	'automated_readability_index',
    'coleman_liau_index':	'coleman_liau_index',
    'flesch_kincaid_grade_level':	'flesch_kincaid_grade_level',
    'flesch_reading_ease':	'flesch_reading_ease',
    'gunning_fog_index':	'gunning_fog_index',
    'lix':	'lix',
    'rix':	'rix',
    'smog_index':	'smog_index',
}
