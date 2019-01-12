import scrapy
from scrapy import cmdline, Request
import time
import json
import urllib.request

BASE_URL = 'http://www.yissum.co.il/find-experts?page='
END_URL = '&k=&rk=&tag='
SEPERATOR = 'class="item-no-body">'
PROF = "Prof."
DR = "Dr."


class YissumSpider(scrapy.Spider):
    # Set the name of the spider
    name = "yissum"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # The delay between each page request
        'CONCURRENT_REQUESTS': 1,  # Use 1 thread to avoid spamming a website
        'CLOSESPIDER_PAGECOUNT': 46,  # The total number of pages to visit
        'ITEM_PIPELINES': { # This tells the spider to have a custom pipeline
            '__main__.YissumSpider': 100,
        }
    }

    # The current page we're crawling
    currentPage = 0

    # This will store all of the projects the spider found
    pages = []
    allNames = []

    # The start URL the spider will use
    start_urls = [
        BASE_URL + str(currentPage) + END_URL
    ]

    # When we found an item, we simply add it to the projects list
    def process_item(self, item, spider):
        self.pages.append(item)
        return item

    # When the spider finished, we'll save the projects
    # def close_spider(self, spider):
    #     # Add an ID for each project
    #     for idx, project in enumerate(self.pages):
    #         project['id'] = idx + 1
    #
    #     # Save the JSON
    #     # open('kickstarter_bigdata.json', 'w').write(json.dumps(
    #     #     {
    #     #         'records': {
    #     #             'record': self.projects
    #     #         }
    #     #     },
    #     #     indent=4))  # Indent the json with 4 spaces

    # The spider gets here once it crawled a new page
    def parse(self, response):
        print('in parse')
        # Read the projects of the entire page and convert it to JSON
        # MAIN_PAGE_PROJECTS_PATH = '//div[contains(@class,"js-react-proj-card")]/@data-project'

        projects = response.xpath('//div[contains(@class,"expert-name")]').extract()
        for line in projects:
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
            print(cur_name)

        # Move on to the next page
        self.currentPage += 1
        yield Request(url=BASE_URL + str(self.currentPage) + END_URL, callback=self.parse)

cmdline.execute(["scrapy", "runspider", "project.py"])


