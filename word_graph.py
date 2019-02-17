import json
from builtins import enumerate

import networkx as nx
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import time

cache = {}


def stem_word_list(text, english_stopwords, stemmer):
    # Get its token, remove punctuation marks
    tokens = set(nltk.RegexpTokenizer(r'[a-zA-Z]{2,}').tokenize(text.lower()))

    return set(stemmer.stem(word) for word in tokens if word not in english_stopwords)


def stem_articles(articles):
    # Get the English stop words
    english_stopwords = stopwords.words('english')

    # Create a new Porter stemmer
    stemmer = nltk.stem.porter.PorterStemmer()

    stemmed_articles = {}

    for researcher in articles.keys():
        stemmed_articles[researcher] = []
        for article in articles[researcher]:
            stemmed_articles[researcher].append(stem_word_list(article, english_stopwords, stemmer))

    return stemmed_articles


def generate_word_graph(articles):
    all_articles = []

    # Get the English stop words
    english_stopwords = stopwords.words('english')

    # Create a new Porter stemmer
    stemmer = nltk.stem.porter.PorterStemmer()

    for article_list in list(articles.values()):
        all_articles += article_list
        # articles.append(str.join(" ", article_list))

    random_articles = json.load(open('data/random_articles.json', 'rb'))
    for article in random_articles:
        all_articles.append(stem_word_list(article, english_stopwords, stemmer))

    # articles = []
    # for i in range(20):
    #     articles.append("computer computer humor technology intelligence")
    #
    # for i in range(5):
    #     articles.append("banana orange orange banana banana apple apples")
    #
    # articles.append("computer banana")

    G = nx.Graph()
    # for article in articles:
    for i, article in enumerate(all_articles):
        if i % (int(len(all_articles) / 10)) == 0:
            print(str(i) + '/' + str(len(all_articles)))
        words = article

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

    for i, edge in enumerate(G.edges):
        G[edge[0]][edge[1]]['weight'] /= max(G.node[edge[0]]['weight'], G.node[edge[1]]['weight'])

    print('graph generated')

    return G


def get_word_similarity(G, word1, word2):
    if not G.has_node(word1) or not G.has_node(word2):
        return 0

    if word1 == word2:
        return 1

    if G.has_edge(word1, word2):
        return G[word1][word2]['weight']

    if word1 in cache and word2 in cache[word1]:
        return cache[word1][word2]

    if word2 in cache and word1 in cache[word2]:
        return cache[word2][word1]

    try:
        shortest_path = nx.shortest_path(G, word1, word2)
    except:
        return 0

    product = 1
    for i in range(len(shortest_path) - 1):
        product *= G[shortest_path[i]][shortest_path[i + 1]]['weight']

    if word1 not in cache:
        cache[word1] = {}

    cache[word1][word2] = product
    return product


def get_article_similarity(G, article1, article2):
    weight_sum = 0

    if len(article2) > len(article1):
        temp = article1
        article1 = article2
        article2 = temp

    for word1 in article1:
        max_score = 0
        for word2 in article2:
            current_similarity = get_word_similarity(G, word1, word2)

            if max_score < current_similarity:
                max_score = current_similarity

            if max_score == 1:
                break

        weight_sum += max_score

    return weight_sum / len(article1)


original_articles = json.load(open('data/researchers_articles.json', encoding='utf-8'))
articles = stem_articles(original_articles)
# G = nx.read_gml('data/word_graph.json')
# print('done reading the graph')
G = generate_word_graph(articles)
# nx.write_gml(G, 'data/word_graph.json')
# print('done writing the graph')
start = time.time()

# researcher1 = 'Shahal Abbo'
# researcher1 = 'Dafna Shahaf'
# researcher1 = 'Amir Shmueli'
#
# cs_researchers = ['Omri Abend', 'Dorit Aharonov', 'Yair Bartal', 'Tsevi Beatus', 'Michael Ben-Or', 'Amit Daniely',
#                   'Guy Kindler', 'Yuval Kochman', 'Orna Kupferman', 'Katrina Ligett', 'Scott Kirkpatrick', 'Matan Gavish']
# agri_researchers = ['Zach Adam', 'Arie Altman', 'Avigdor Cahaner', 'Idan Efroni', 'Rivka Elbaum', 'Yonatan Elkind', 'Eyal Fridman',
#                     'Eliezer Goldschmidt', 'Raphael Goren', 'Tamar Friedlander', 'Smadar Harpaz Saad', 'Shimon Lavee']
# cs_avg = []
# agri_avg = []
#
# for researcher2 in cs_researchers:
#     max_score = 0
#     best_article1, best_article2 = '', ''
#     score = 0
#     print(researcher2)
#     for article1 in articles[researcher1]:
#         for article2 in articles[researcher2]:
#             score = get_article_similarity(G, article1, article2)
#
#             if max_score < score:
#                 max_score = score
#                 best_article1 = article1
#                 best_article2 = article2
#     # cs_avg.append(score / len(researchers_articles[researcher1]) / len(researchers_articles[researcher2]))
#     cs_avg.append(max_score)
#     # print(f'Best score of {researcher1} and {researcher2} is {100 * score / len(researchers_articles[researcher1]) / len(researchers_articles[researcher2])}')
#     # print(f'Best score of {researcher1} and {researcher2} is {max_score}:\t\t{best_article1}\t\t{best_article2}')
#
# for researcher2 in agri_researchers:
#     max_score = 0
#     best_article1, best_article2 = '', ''
#     score = 0
#     print(researcher2)
#     for article1 in articles[researcher1]:
#         for article2 in articles[researcher2]:
#             score = get_article_similarity(G, article1, article2)
#
#             if max_score < score:
#                 max_score = score
#                 best_article1 = article1
#                 best_article2 = article2
#
#     # agri_avg.append(score / len(researchers_articles[researcher1]) / len(researchers_articles[researcher2]))
#     agri_avg.append(max_score)
#
# # print(f"time:{time.time() - start} seconds")
# plt.figure()
# plt.plot(cs_avg, 'bo')
# plt.plot(agri_avg, 'ro')
# plt.show()


faculties = json.load(open('data/researchers_faculties.json', encoding='utf-8'))
dafna = "Dafna Shahaf"
researcher_faculty = faculties[dafna]
researchers_in_other_faculties = []

for researcher in faculties:
    if faculties[researcher] != researcher_faculty and len(articles[researcher]) != 0:
        researchers_in_other_faculties.append(researcher)

# researchers_in_other_faculties = ['Amalya Oliver', 'Tishby Orya', 'Shaul Oreg', 'Renana  Peres']
matches = []

for i, researcher in enumerate(researchers_in_other_faculties):
    print(f'{i}/{len(researchers_in_other_faculties)} - {researcher}')

    best_match = None
    total_score = 0
    for j, article1 in enumerate(articles[dafna]):
        score = 0
        for article2 in articles[researcher]:
            score += get_article_similarity(G, article1, article2)

        score /= len(articles[researcher])
        if best_match is None or score > best_match[0]:
            best_match = (score, researcher, article1, "", j)
    if best_match:
        matches.append(best_match)


# for i, researcher in enumerate(researchers_in_other_faculties):
#     print(f'{i}/{len(researchers_in_other_faculties)} - {researcher}')
#
#     best_match = None
#     total_score = 0
#     for article1 in articles[dafna]:
#         score = 0
#         for article2 in articles[researcher]:
#             score = max(get_article_similarity(G, article1, article2), score)
#         total_score += score
#
#     matches.append((total_score / len(articles[dafna]), researcher, "", "", i))



matches.sort(key=lambda x: x[0], reverse=True)

# for match in matches:
#     print(str(match) + " " + articles[dafna][match[4]])
# print(f"time:{time.time() - start} seconds")

for i in range(3):
    researcher = matches[i][1]
    researcher_matches = []

    print(researcher)
    for j, article in enumerate(articles[researcher]):
        for k, dafna_article in enumerate(articles[dafna]):
            researcher_matches.append((original_articles[dafna][k], original_articles[researcher][j], get_article_similarity(G, dafna_article, article)))
        # researcher_matches.append((original_articles[researcher][j], get_article_similarity(G, articles[dafna][matches[i][4]], article)))
    researcher_matches.sort(key=lambda x: x[2], reverse=True)

    print(researcher)
    for j in range(min(3, len(articles[researcher]))):
        print(researcher_matches[j][1] + "\t\t" + researcher_matches[j][0])

    print()
    print()
#
#
# # take researchers with best 3 scores
#
# print(len(G.nodes))
# print(len(G.edges))
# s = stem_articles(["banana banana computer orange", "computer banana"])
# print(get_article_similarity(G, s[0], s[1]))
