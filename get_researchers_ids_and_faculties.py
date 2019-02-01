import json
import re

import requests
import scrapy
from scrapy import cmdline, Request, signals

BASE_URL = 'http://www.yissum.co.il/find-experts?page='
END_URL = '&k=&rk=&tag='
SEPERATOR = 'class="item-no-body">'
PROF = "Prof. "
DR = "Dr. "


# The class is responsible of finding the faculty of each researcher and the ID of each researcher on SemanticScholar
class YissumSpider(scrapy.Spider):
    # Set the name of the spider
    name = "yissum"

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,  # Use 1 thread to avoid spamming a website
        'DOWNLOAD_DELAY': 1,  # The delay between each page request
        'CLOSESPIDER_PAGECOUNT': 46,  # The total number of pages to visit
    }

    # The current page we're crawling
    currentPage = 0

    # This will store all of the projects the spider found
    names = []
    faculties = []

    # The start URL the spider will use
    start_urls = [
        BASE_URL + str(currentPage) + END_URL
    ]

    get_id_by_author_request_data = json.load(open('requests/get_id_by_author_data.json', encoding='utf-8'))
    get_id_by_author_request_headers = json.load(open('requests/get_id_by_author_headers.json', encoding='utf-8'))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Initiate the crawler to use a custom spider closed signal
        spider = super(YissumSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        # Find the id of each researcher by searching 'SemanticScholar'
        names_to_ids = {}
        for author_name in self.names:
            self.get_id_by_author_request_data['queryString'] = '"' + author_name + '"'
            names_to_ids[author_name] = list(map(lambda author: int(author['id']), requests.post(
                'https://www.semanticscholar.org/api/1/search',
                json=self.get_id_by_author_request_data,
                headers=self.get_id_by_author_request_headers
            ).json()['matchedAuthors']))

        # Save the id's
        result_file = open('data/researchers_ids.json', 'w', encoding='utf-8')
        result_file.write(json.dumps(
            names_to_ids,
            indent=4,  # Indent the json with 4 spaces
            ensure_ascii=False)
        )
        result_file.close()

        # Save the faculties
        result_file = open('data/researchers_faculties.json', 'w', encoding='utf-8')
        names_to_faculties = {}

        for i in range(len(self.allNames)):
            print(self.allNames[i])
            names_to_faculties[self.allNames[i]] = self.faculties[i]

        result_file.write(json.dumps(
            names_to_faculties,
            indent=4,  # Indent the json with 4 spaces
            ensure_ascii=False)
        )
        result_file.close()

    # The spider gets here once it crawled a new page
    def parse(self, response):
        # Read the projects of the entire page and convert it to JSON
        # MAIN_PAGE_PROJECTS_PATH = '//div[contains(@class,"js-react-proj-card")]/@data-project'

        names = response.xpath('//div[contains(@class,"expert-name")]').extract()
        for line in names:
            # print(line)
            if PROF in line:
                start,cur_name = line.split(PROF)
                cur_name, start = cur_name.split("</a>")
            elif DR in line:
                start, cur_name = line.split(DR)
                cur_name, start = cur_name.split("</a>")
            else:
                start, cur_name = line.split(SEPERATOR)
                cur_name, start = cur_name.split("</a>")
            self.allNames.append(cur_name)
            # print(cur_name)

        faculties = (response.xpath('//div[contains(@class,"expert-text")]')).extract()
        for faculty in faculties:
            m = re.search(".*<a href.*>(.*)</a>.*", faculty)

            if m and "FACULTY / SCHOOL" in faculty:
                print(faculty)
                self.faculties.append(m.group(1))

        # Move on to the next page
        self.currentPage += 1
        yield Request(url=BASE_URL + str(self.currentPage) + END_URL, callback=self.parse)


cmdline.execute(["scrapy", "runspider", "get_researchers_ids_and_faculties.py"])
