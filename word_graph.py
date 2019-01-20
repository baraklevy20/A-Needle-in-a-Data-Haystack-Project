import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage
import networkx as nx
import nltk
from nltk.corpus import stopwords
from collections import Counter


def stem_word_list(text):
    # Get its token, remove punctuation marks
    tokens = nltk.RegexpTokenizer(r'[a-zA-Z]{2,}').tokenize(text.lower())

    # Get the English stop words
    english_stopwords = stopwords.words('english')

    # todo maybe
    useless_words = ['use', 'paper', 'also', 'two']

    # Create a new Porter stemmer
    stemmer = nltk.stem.porter.PorterStemmer()

    return [stemmer.stem(word) for word in tokens if word not in english_stopwords]

def generate_word_graph():
    articles = json.load(open('data/random_articles.json', 'rb'))['articles']

    # articles[0] = "barak tomer mazor tomer banana"
    # articles[1] = "apple pens mazor"

    G = nx.Graph()
    for i, article in enumerate(articles):
        print(str(i) + '/' + str(len(articles)))
        words = stem_word_list(article)
        # tokens_count = Counter(words)
        # print(tokens_count.most_common(20))

        # todo take only most frequent
        for word in words:
            if not G.has_node(word):
                G.add_node(word, weight=1)
            else:
                G.node[word]['weight'] += 1

        for w1 in words:
            for w2 in words:
                if w1 != w2:
                    if not G.has_edge(w1, w2):
                        G.add_edge(w1, w2, weight=0.5)
                    else:
                        G[w1][w2]['weight'] += 0.5

    for edge in G.edges:
        G[edge[0]][edge[1]]['weight'] /= max(G.node[edge[0]]['weight'], G.node[edge[1]]['weight'])


    # G.add_node('avi')
    # G.add_edge('avi', 'mazor', weight=1)
    # G.add_edge('avi', 'pen', weight=3)
    # for edge in G.edges:
    #     G[edge[0]][edge[1]]['weight'] = 1 / G[edge[0]][edge[1]]['weight']

    return G


def get_word_similarity(G, word1, word2):
    if not G.has_node(word1) or not G.has_node(word2):
        return 0

    shortest_path = nx.shortest_path(G, word1, word2)
    sum = 0

    for i in range(len(shortest_path) - 1):
        sum += G[shortest_path[i]][shortest_path[i + 1]]['weight']

    return sum / (len(shortest_path) - 1)


def get_article_similarity(G, article1, article2):
    weight_sum = 0

    articles1_words = stem_word_list(article1)
    articles2_words = stem_word_list(article2)

    not_found_words = 0

    for word1 in articles1_words:
        for word2 in articles2_words:
            if word1 == word2:
                weight_sum += 1
            else:
                current_similarity = get_word_similarity(G, word1, word2)
                if current_similarity != 0:
                    weight_sum += current_similarity
                else:
                    not_found_words += 1

    if not_found_words == len(articles1_words) * len(articles2_words):
        # print('no words')
        return 0
    return weight_sum / (len(articles1_words) * len(articles2_words) - not_found_words)  # todo why not this
    # return weight_sum / len(set(articles1_words) | set(articles2_words))


G = generate_word_graph()
# edge_labels = dict([((u,v,),d['weight'])
#                  for u,v,d in G.edges(data=True)])
# pos=nx.spring_layout(G)
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
# nx.draw(G, pos, with_labels=True)
# plt.show()


researchers_articles = json.load(open('data/researchers_articles.json', encoding='utf-8'))

# Should be very high (same person)
# print(get_article_similarity(G, researchers_articles['Shahal Abbo'][0], researchers_articles['Shahal Abbo'][1]))
# print(get_article_similarity(G, researchers_articles['Shahal Abbo'][1], researchers_articles['Shahal Abbo'][5]))
# print(get_article_similarity(G, researchers_articles['Shahal Abbo'][6], researchers_articles['Shahal Abbo'][18]))
#
# # Should be high (same domain)
# print()
# print(get_article_similarity(G, researchers_articles['Shahal Abbo'][2], researchers_articles['Hagai Abeliovich'][0]))
# print(get_article_similarity(G, researchers_articles['Shahal Abbo'][4], researchers_articles['Hagai Abeliovich'][4]))
# print(get_article_similarity(G, researchers_articles['Shahal Abbo'][7], researchers_articles['Hagai Abeliovich'][7]))
#
# # Should be low (different domain, agriculture and NLP)
# print()
# print(get_article_similarity(G, researchers_articles['Shahal Abbo'][0], researchers_articles['Omri Abend'][1]))
# print(get_article_similarity(G, researchers_articles['Shahal Abbo'][2], researchers_articles['Omri Abend'][7]))
# print(get_article_similarity(G, researchers_articles['Shahal Abbo'][4], researchers_articles['Omri Abend'][1]))

# Find best match of researcher 1 with any of researchers 2
# Shahal Abbo = Same person
# Avigdor Cahaner, Arie Altman = Same department (PLANT SCIENCES AND GENETICS)
# Saul Burdman, Shay Covo = Different department, same faculty (PLANT PATHOLOGY AND MICROBIOLOGY)
# Avner Adin, Yona Chen - Different department, same faculty (SOIL AND WATER SCIENCES)
# Omri Abend, Dafna Shahaf, Sara Cohen - Different faculty
researcher1 = 'Shahal Abbo'
researchers2 = ['Shahal Abbo',
                'Avigdor Cahaner', 'Arie Altman',
                'Saul Burdman', 'Shay Covo',
                'Avner Adin', 'Yona Chen',
                'Omri Abend', 'Dafna Shahaf', 'Sara Cohen']

for researcher2 in researchers2:
    max_score = 0
    for article1 in researchers_articles[researcher1]:
        for article2 in researchers_articles[researcher2]:
            score = get_article_similarity(G, article1, article2)

            if max_score < score:
                max_score = score
    print(f'Best score of {researcher1} and {researcher2} is {max_score}')

# print(get_article_similarity(G, 'tomer tomer', 'barak mazor'))
# print(get_article_similarity(G, 'high soil acidity, very low of nutrient availability  especially NPK', 'fruit trees agricultural'))
# print(get_article_similarity(G, 'In the engineering curriculum, remote labs', 'agricultural fruit'))
# print(get_article_similarity(G, 'In the engineering curriculum, remote labs', 'high soil acidity, very low of nutrient availability  especially NPK'))
# print(get_article_similarity(G, 'physical characteristicsare among propertiesaffecting the susceptibility to erosion', 'high soil acidity, very low of nutrient availability  especially NPK'))
# print(get_article_similarity(G, 'This paper focuses on a new way for students to deepen their knowledge in image processing', 'high soil acidity, very low of nutrient availability  especially NPK'))
# print(get_article_similarity(G, 'This paper focuses on a new way for students to deepen their knowledge in image processing', 'In the engineering curriculum, remote labs'))
