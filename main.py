import json
from builtins import enumerate
import networkx as nx
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

cache = {}


# The function stems an article
def stem_article(text, english_stopwords, stemmer):
    # Get its token, remove punctuation marks
    tokens = set(nltk.RegexpTokenizer(r'[a-zA-Z]{2,}').tokenize(text.lower()))

    return set(stemmer.stem(word) for word in tokens if word not in english_stopwords)


# The function stems all the researchers articles
def stem_articles(articles):
    # Get the English stop words
    english_stopwords = stopwords.words('english')

    # Create a new Porter stemmer
    stemmer = nltk.stem.porter.PorterStemmer()

    stemmed_articles = {}

    # Stem each article of each researcher
    for researcher in articles.keys():
        stemmed_articles[researcher] = []
        for article in articles[researcher]:
            stemmed_articles[researcher].append(stem_article(article, english_stopwords, stemmer))

    return stemmed_articles


# The function generates the word graph, described in step 2
def generate_word_graph(articles):
    all_articles = []

    # Get the English stop words
    english_stopwords = stopwords.words('english')

    # Create a new Porter stemmer
    stemmer = nltk.stem.porter.PorterStemmer()

    for article_list in list(articles.values()):
        all_articles += article_list

    # Stem the random articles as well
    random_articles = json.load(open('data/random_articles.json', 'rb'))
    for article in random_articles:
        all_articles.append(stem_article(article, english_stopwords, stemmer))

    # Go through each article
    G = nx.Graph()
    for article in all_articles:
        # Create a node for each word that appears in the article
        for word in article:
            if not G.has_node(word):
                G.add_node(word, weight=1)
            else:
                G.node[word]['weight'] += 1

        # Create an edge between each pair of words that appear in the same article
        # The initial weight is 0.5. This makes sure we only count a pair once and not twice
        for w1 in article:
            for w2 in article:
                if w1 != w2:
                    if not G.has_edge(w1, w2):
                        G.add_edge(w1, w2, weight=0.5)
                    else:
                        G[w1][w2]['weight'] += 0.5

    # Normalize the graph
    for i, edge in enumerate(G.edges):
        G[edge[0]][edge[1]]['weight'] /= max(G.node[edge[0]]['weight'], G.node[edge[1]]['weight'])

    return G


# The function returns the similarity between two words (step 3)
def get_word_similarity(word1, word2):
    # There's nothing to do if the words do not appear in the words graph.
    # This should not happen as the graph is quite rich in words
    if not G.has_node(word1) or not G.has_node(word2):
        return 0

    # If the two words are the same word, simply return 1
    if word1 == word2:
        return 1

    # If there's a direct edge between the words, return its weight
    if G.has_edge(word1, word2):
        return G[word1][word2]['weight']

    # If the two words were already calculated and are in the cache, return their score
    if word1 in cache and word2 in cache[word1]:
        return cache[word1][word2]

    if word2 in cache and word1 in cache[word2]:
        return cache[word2][word1]

    # Otherwise, get the shortest path
    try:
        shortest_path = nx.shortest_path(G, word1, word2)
    except:
        return 0

    # Multiply the weight along the path
    product = 1
    for i in range(len(shortest_path) - 1):
        product *= G[shortest_path[i]][shortest_path[i + 1]]['weight']

    # Add the score to the cache
    if word1 not in cache:
        cache[word1] = {}

    cache[word1][word2] = product

    # Return the end result
    return product


# The function returns the similarity between two articles (step 4)
def get_article_similarity(article1, article2):
    weight_sum = 0

    # When the first article is longer, the results are better. So we switch the two if necessary
    if len(article2) > len(article1):
        temp = article1
        article1 = article2
        article2 = temp

    # Go through each word in the first article
    for word1 in article1:

        # Find the best matched word in the other article
        max_score = 0
        for word2 in article2:
            current_similarity = get_word_similarity(word1, word2)

            if max_score < current_similarity:
                max_score = current_similarity

            # If we already found the best one (same word), no need to continue checking
            if max_score == 1:
                break

        # Add it to the total weight
        weight_sum += max_score

    # Normalize the results
    return weight_sum / len(article1)


# The function returns the similarity between two researchers (step 5)
def get_researchers_similarity(researcher1, researcher2):
    best_match = None

    # Go through each the first researcher's articles and calculate
    # its similarity with the articles of the second researcher
    for j, article1 in enumerate(articles[researcher1]):
        score = 0
        for article2 in articles[researcher2]:
            score += get_article_similarity(article1, article2)

        score /= len(articles[researcher2])
        if best_match is None or score > best_match[0]:
            best_match = (score, researcher2, article1, "", j)

    if best_match:
        return best_match


# The function prints the best K matched researchers to a given researcher (step 6)
# When K=-1, it prints all the researchers
# The function prints the M best matched articles of the best matched researchers
def print_best_k_researchers(researcher, K, M, is_same_faculty):
    researcher_faculty = faculties[researcher]
    researchers_in_desired_faculties = []

    # Could've been done with a XOR but it may not have been understandable
    def correct_faculty(faculty, desired_faculty):
        return is_same_faculty and faculty == desired_faculty or not is_same_faculty and faculty != desired_faculty

    # Go through each researcher. If they're in the correct faculties, we add them to the list of desired faculties
    for researcher2 in faculties:
        if correct_faculty(faculties[researcher2], researcher_faculty)\
                and len(articles[researcher2]) != 0\
                and researcher2 != researcher:
            researchers_in_desired_faculties.append(researcher2)

    # Find the score of each researcher in the desired faculties with the given researcher
    matches = []

    for researcher2 in researchers_in_desired_faculties:
        similarity = get_researchers_similarity(researcher, researcher2)
        if similarity:
            matches.append(similarity)

    # Sort the results by the score
    matches.sort(key=lambda x: x[0], reverse=True)

    # Print the top K results
    if K == -1:
        K = len(matches)

    for i in range(K):
        researcher2 = matches[i][1]
        researcher_matches = []

        for j, article in enumerate(articles[researcher2]):
            for k, dafna_article in enumerate(articles[researcher]):
                researcher_matches.append((original_articles[researcher][k], original_articles[researcher2][j],
                                           get_article_similarity(dafna_article, article)))
            researcher_matches.sort(key=lambda x: x[2], reverse=True)

        print(researcher2)
        for j in range(min(M, len(articles[researcher2]))):
            print(researcher_matches[j][1] + "\t\t" + researcher_matches[j][0])

        print()
        print()


def show_correlation_graph(researcher):
    cs_researchers = ['Omri Abend', 'Dorit Aharonov', 'Yair Bartal',
                      'Tsevi Beatus', 'Michael Ben-Or', 'Amit Daniely',
                      'Guy Kindler', 'Yuval Kochman', 'Orna Kupferman',
                      'Katrina Ligett', 'Scott Kirkpatrick', 'Matan Gavish']

    agri_researchers = ['Zach Adam', 'Arie Altman', 'Avigdor Cahaner',
                        'Idan Efroni', 'Rivka Elbaum', 'Yonatan Elkind',
                        'Eyal Fridman', 'Eliezer Goldschmidt', 'Raphael Goren',
                        'Tamar Friedlander', 'Smadar Harpaz Saad', 'Shimon Lavee']
    cs_avg = []
    agri_avg = []

    # Go through each researcher in the CS department and find
    # the score of its best matching article with the given researcher
    for researcher2 in cs_researchers:
        max_score = 0
        for article1 in articles[researcher]:
            for article2 in articles[researcher2]:
                score = get_article_similarity(article1, article2)

                if max_score < score:
                    max_score = score
        cs_avg.append(max_score)

    # Go through each researcher in the agriculture department and find
    # the score of its best matching article with the given researcher
    for researcher2 in agri_researchers:
        max_score = 0
        for article1 in articles[researcher]:
            for article2 in articles[researcher2]:
                score = get_article_similarity(article1, article2)

                if max_score < score:
                    max_score = score

        agri_avg.append(max_score)

    plt.figure()
    plt.plot(cs_avg, 'bo')
    plt.plot(agri_avg, 'ro')
    plt.show()


if __name__ == '__main__':
    faculties = json.load(open('data/researchers_faculties.json', encoding='utf-8'))
    original_articles = json.load(open('data/researchers_articles.json', encoding='utf-8'))
    articles = stem_articles(original_articles)
    G = generate_word_graph(articles)

    # Experiment 1
    print_best_k_researchers("Shmuel Peleg", 3, 3, True)

    # Experiments 2-4
    show_correlation_graph('Shahal Abbo')
    show_correlation_graph('Dafna Shahaf')
    show_correlation_graph('Amir Shmueli')

    # Experiment 5
    print_best_k_researchers("Dafna Shahaf", 3, 3, False)

    # Experiment 6
    print_best_k_researchers("Shmuel Peleg", -1, 1, True)
    print_best_k_researchers("Ari Rappoport", -1, 1, True)
    print_best_k_researchers("Gur Mosheiov", -1, 1, True)
