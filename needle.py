import scrapy
from scrapy import cmdline, Request, signals
import time
import json
import urllib.request

BASE_URL = 'https://www.kickstarter.com/discover/categories/technology?page='

# todo clean the code, remove kickstarter references

class KickstarterSpider(scrapy.Spider):
    # Set the name of the spider
    name = "kickstarter"

    request_format = open('request_format.json', encoding='utf-8').read()
    topics = ['Agriculture', 'Auxiliary sciences of history', 'Bibliography. Library science. Information resources',
              'Education', 'Fine Arts', 'General Works', 'Geography. Anthropology. Recreation',
              'History (General) and history of Europe', 'History America', 'Language and Literature', 'Law',
              'Medicine', 'Military Science', 'Music and books on Music', 'Naval Science',
              'Philosophy. Psychology. Religion', 'Political science', 'Science', 'Social Sciences', 'Technology']

    # topics = ['Bibliography. Library science. Information resources']

    # This will store all of the projects the spider found
    articles = []

    # todo use api and not endpoint directly
    # The start URL the spider will use
    start_urls = list(map(lambda topic, topics=topics, request_format=request_format:
                          'https://doaj.org/query/article/_search?ref=please-stop-using-this-endpoint-directly-use-the-api&source=' + request_format.replace(
                              '%s', topic), topics))

    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # The delay between each page request
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(KickstarterSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        # Save the JSON
        open('articles.json', 'w', encoding='utf-8').write(json.dumps(
            {
                'articles': self.articles
            },
            indent=4, ensure_ascii=False))  # Indent the json with 4 spaces

    # The spider gets here once it crawled a new page
    def parse(self, response):
        self.articles.extend(list(map(lambda hit: hit['_source']['bibjson']['abstract'],
                                      filter(lambda hit: hit['_source']['index']['language'] == ['English'] and 'abstract' in hit['_source']['bibjson'] and hit['_source']['bibjson']['abstract'] != '-',
                                             json.loads(response.text)['hits']['hits']))))


cmdline.execute(["scrapy", "runspider", "needle.py"])
