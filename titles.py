import random
import time
import requests

class titles():

    def __init__(self):
        self.session = requests.Session()

    def title_getter(self, ids):
        headers = {
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Accept-Language' : 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'Connection' : 'keep-alive',
            'Host' : 'api.semanticscholar.org',
            'Upgrade-Insecure-Requests' : '1',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        article_dict = {}
        for id in ids:
            article_dict[id] = []
            # Make sure that we will not block
            timeDelay = random.randrange(0, 1)
            time.sleep(timeDelay)
            web_api = f'https://api.semanticscholar.org/v1/author/{id}'
            response = self.session.get(url=web_api, verify=True, headers=headers)
            id_json = response.json()
            for article in id_json['papers']:
                article_dict[id].append(article['title'])
        return article_dict


a = titles()
b = a.title_getter(['1805894', '50491885'])
print(b['1805894'])
print(b['50491885'])
