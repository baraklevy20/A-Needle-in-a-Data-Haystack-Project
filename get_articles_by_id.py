import time
import requests
import json


class titles():
    def __init__(self):
        self.session = requests.Session()

    def title_getter(self, researchers):
        article_dict = {}
        for i, name in enumerate(researchers):
            article_dict[name] = []

            # Make sure that we will not block
            time.sleep(1)

            for id in researchers[name]:
                articles = self.session.get(url=f'https://api.semanticscholar.org/v1/author/{id}').json()['papers']

                for article in articles:
                    article_dict[name].append(article['title'])
            print(str(i) + "/910")
        return article_dict


a = titles()
b = a.title_getter(json.load(open('data/authors_names_to_id.json')))
result_file = open('data/researchers_articles.json', 'w', encoding='utf-8')
result_file.write(json.dumps(
    b,
    indent=4,  # Indent the json with 4 spaces
    ensure_ascii=False)
)
result_file.close()
