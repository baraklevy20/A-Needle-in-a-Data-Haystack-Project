import json

import scrapy
from scrapy import cmdline, signals


# The class is responsible of finding random articles on multiple topics
class RandomArticlesSpider(scrapy.Spider):
    # Set the name of the spider
    name = "random_articles_crawler"

    request_format = open('requests/get_random_articles_data.json', encoding='utf-8').read()
    topics = ['Agriculture', 'Auxiliary sciences of history', 'Bibliography. Library science. Information resources',
              'Education', 'Fine Arts', 'General Works', 'Geography. Anthropology. Recreation',
              'History (General) and history of Europe', 'History America', 'Language and Literature', 'Law',
              'Medicine', 'Military Science', 'Music and books on Music', 'Naval Science',
              'Philosophy. Psychology. Religion', 'Political science', 'Science', 'Social Sciences', 'Technology']

    # This will store all of the projects the spider found
    articles = []

    # The start URL the spider will use
    base_url = 'https://doaj.org/query/article/_search'
    ref = 'please-stop-using-this-endpoint-directly-use-the-api'  # The direct API offers search by multiple fields

    start_urls = list(map(lambda topic, topics=topics, base_url=base_url, ref=ref, request_format=request_format:
                          f'{base_url}?ref={ref}&source=' + request_format.replace('%s', topic), topics))

    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # The delay between each page request
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Initiate the crawler to use a custom spider closed signal
        spider = super(RandomArticlesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    # The function will get called once the spider is done crawling
    def spider_closed(self, spider):
        # Save the articles as a JSON file
        open('data/random_articles.json', 'w', encoding='utf-8').write(json.dumps(
            self.articles,
            indent=4,  # Indent the json with 4 spaces
            ensure_ascii=False)  # Make sure we save every character
        )

    # The spider gets here once it crawled a new page
    def parse(self, response):
        self.articles.extend(
            list(
                # Get the abstract of the articles
                map(lambda hit: hit['_source']['bibjson']['abstract'],
                    # Get articles in English only with an abstract
                    filter(
                        lambda hit: hit['_source']['index']['language'] == ['English']
                                    and 'abstract' in hit['_source']['bibjson'] and
                                    hit['_source']['bibjson']['abstract'] != '-',
                        json.loads(response.text)['hits']['hits'])
                    )
            )
        )


cmdline.execute(["scrapy", "runspider", "get_random_articles.py"])
