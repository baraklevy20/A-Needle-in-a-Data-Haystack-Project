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
    temp_articles = list(json.load(open('data/researchers_articles.json', encoding='utf-8')).values())
    articles = []
    for article_list in temp_articles:
        articles += article_list
    articles += json.load(open('data/random_articles.json', 'rb'))['articles']

    # articles[0] = "barak barak barak tomer mazor tomer banana"
    # articles[1] = "apple pens mazor"

    G = nx.Graph()
    # for article in articles[0:2]:
    for i, article in enumerate(articles):
        if i % (int(len(articles) / 10)) == 0:
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

        # for w1 in words:
        #     for w2 in words:
        #         if w1 != w2:
        #             if not G.has_edge(w1, w2):
        #                 G.add_edge(w1, w2, weight=0.5)
        #             else:
        #                 G[w1][w2]['weight'] += 0.5

    # count = 0
    for edge in G.edges:
        G[edge[0]][edge[1]]['weight'] /= G.node[edge[0]]['weight'] * G.node[edge[1]]['weight']
    #         G[edge[0]][edge[1]]['weight'] /= (1 + np.log(max(G.node[edge[0]]['weight'], G.node[edge[1]]['weight'])))

    print('graph generated')
    #
    #     if G[edge[0]][edge[1]]['weight'] > 0.1 and G[edge[0]][edge[1]]['weight'] < 1:
    #         count += 1
    # print (f"{count}/{len(G.edges)}")
    # G[edge[0]][edge[1]]['weight'] /= G.node[edge[0]]['weight'] * G.node[edge[1]]['weight']

    # if G[edge[0]][edge[1]]['weight'] > 1:
    #     print('hi2')

    # G.add_node('avi')
    # G.add_edge('avi', 'mazor', weight=1)
    # G.add_edge('avi', 'pen', weight=3)
    # for edge in G.edges:
    #     G[edge[0]][edge[1]]['weight'] = 1 / G[edge[0]][edge[1]]['weight']

    return G


def get_word_similarity(G, word1, word2):
    if not G.has_node(word1) or not G.has_node(word2):
        return 0

    if word1 == word2:
        return 1 / G.node[word1]['weight']

    try:
        shortest_path = nx.shortest_path(G, word1, word2)
    except:
        return 0

    sum = 0

    for i in range(len(shortest_path) - 1):
        sum += G[shortest_path[i]][shortest_path[i + 1]]['weight']
    # todo having the same article will always return 1/total_appearances.
    # to normalize it we might need to multiple by the total frequency of all of the words in the article to get this value to 1
    # otherwise articles with more frequent words will have higher weight
    # if sum / (len(shortest_path) - 1) > 1:
    #     print('hi')
    return sum / (len(shortest_path) - 1)


def get_article_similarity(G, article1, article2):
    weight_sum = 0

    articles1_words = stem_word_list(article1)
    articles2_words = stem_word_list(article2)

    if len(articles2_words) > len(articles1_words):
        temp = articles1_words
        articles1_words = articles2_words
        articles2_words = temp

    for word1 in articles1_words:
        max_score = 0
        for word2 in articles2_words:
            current_similarity = get_word_similarity(G, word1, word2)

            if max_score < current_similarity:
                max_score = current_similarity

        weight_sum += max_score

    return weight_sum / len(articles1_words)


def sum_frequency(G, article1_words, article2_words):
    sum = 0

    for word1 in article1_words:
        sum += 1 / G.node[word1]['weight']

    for word2 in article2_words:
        sum += 1 / G.node[word2]['weight']

    return sum


# G = nx.read_gml('data/word_graph.json')
# print('done reading the graph')
G = generate_word_graph()
nx.write_gml(G, 'data/word_graph.json')
print('done writing the graph')
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
# researcher1 = 'Shahal Abbo'
researcher1 = 'Dafna Shahaf'
# researcher1 = 'Amir Shmueli'
# researchers2 = ['Eyal Fridman', 'Smadar Harpaz Saad', 'Raphael Goren']
# researchers2 = ['Sha''Eyal Fridman', 'Smadar Harpaz Saad', 'Raphael Goren', 'Matan Gavish', 'Gil Segev']
# researchers2 = ['Matan Gavish', 'Gil Segev', 'Sara Cohen']
# researchers2 = ['Shahal Abbo',
#                 'Avigdor Cahaner', 'Arie Altman',
#                 'Saul Burdman', 'Shay Covo',
#                 'Avner Adin', 'Yona Chen',
#                 'Omri Abend', 'Dafna Shahaf', 'Matan Gavish']

cs_researchers = ['Dafna Shahaf', 'Omri Abend', 'Dorit Aharonov', 'Yair Bartal', 'Tsevi Beatus', 'Michael Ben-Or', 'Amit Daniely',
                  'Guy Kindler', 'Yuval Kochman', 'Orna Kupferman', 'Katrina Ligett', 'Scott Kirkpatrick']
agri_researchers = ['Zach Adam', 'Arie Altman', 'Avigdor Cahaner', 'Idan Efroni', 'Rivka Elbaum', 'Yonatan Elkind', 'Eyal Fridman',
                    'Eliezer Goldschmidt', 'Raphael Goren', 'Tamar Friedlander', 'Smadar Harpaz Saad', 'Shimon Lavee']
cs_avg = []
agri_avg = []

for researcher2 in cs_researchers:
    max_score = 0
    best_article1, best_article2 = '', ''
    score = 0
    print(researcher2)
    for article1 in researchers_articles[researcher1]:
        for article2 in researchers_articles[researcher2]:
            score += get_article_similarity(G, article1, article2)

            if max_score < score:
                max_score = score
                best_article1 = article1
                best_article2 = article2
    # cs_avg.append(score / len(researchers_articles[researcher1]) / len(researchers_articles[researcher2]))
    cs_avg.append(max_score)
    # print(f'Best score of {researcher1} and {researcher2} is {100 * score / len(researchers_articles[researcher1]) / len(researchers_articles[researcher2])}')
    # print(f'Best score of {researcher1} and {researcher2} is {max_score}:\t\t{best_article1}\t\t{best_article2}')

for researcher2 in agri_researchers:
    max_score = 0
    best_article1, best_article2 = '', ''
    score = 0
    print(researcher2)
    for article1 in researchers_articles[researcher1]:
        for article2 in researchers_articles[researcher2]:
            score += get_article_similarity(G, article1, article2)

            if max_score < score:
                max_score = score
                best_article1 = article1
                best_article2 = article2

    # agri_avg.append(score / len(researchers_articles[researcher1]) / len(researchers_articles[researcher2]))
    agri_avg.append(max_score)
#
plt.figure()
plt.plot(cs_avg, 'bo')
plt.plot(agri_avg, 'ro')
plt.show()

# print(get_article_similarity(G, 'tomer tomer', 'barak mazor'))
# print(get_article_similarity(G, 'high soil acidity, very low of nutrient availability  especially NPK', 'fruit trees agricultural'))
# print(get_article_similarity(G, 'In the engineering curriculum, remote labs', 'agricultural fruit'))
# print(get_article_similarity(G, 'In the engineering curriculum, remote labs', 'high soil acidity, very low of nutrient availability  especially NPK'))
# print(get_article_similarity(G, 'physical characteristicsare among propertiesaffecting the susceptibility to erosion', 'high soil acidity, very low of nutrient availability  especially NPK'))
# print(get_article_similarity(G, 'This paper focuses on a new way for students to deepen their knowledge in image processing', 'high soil acidity, very low of nutrient availability  especially NPK'))
# print(get_article_similarity(G, 'This paper focuses on a new way for students to deepen their knowledge in image processing', 'In the engineering curriculum, remote labs'))


# matches = []
# for researcher in researchers_in_other_faculties:
#     score = 0
#     for article1 in dafna_articles:
#         for article2 in researcher_articles:
#             score = max(get_article_similarity(G, article1, article2), score)
#     matches.append(score)
#
# # take researchers with best 3 scores
