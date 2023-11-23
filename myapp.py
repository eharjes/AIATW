from flask import Flask, request, render_template
from Levenshtein import distance
from english_dictionary.scripts.read_pickle import get_dict
import enchant
from searchengine import SearchEngine  # Assuming your search engine code is in search_engine.py

app = Flask(__name__)
search_engine = SearchEngine('https://vm009.rz.uos.de/crawl/index.html', 4000)
search_engine.build_index()

history = []
english_dict = enchant.Dict("en_US")

def get_recommendation(query):
    """Returns closest (Levenshtein distance) word to the given word

    query (string)          = word to get recommendation for

    Returns:

    recommendations (list)    = joined string of recommended words (can match the given word(s))
    """
    # initialize recommendation as empty list with length of words in the query
    queries = query.split()
    recommendations = []
    # initialize best distance as very high so the first word checked always becomes the first recommendation
    for word in queries:
        if english_dict.check(word):
            recommendations.append(word)
        else:
            recommendations.append(english_dict.suggest(word))
    return " ".join(recommendations)

@app.route('/')
def home():

    return render_template('home_page_template2.html', history = reversed(history))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query not in history:
        history.append(query)
    if len(history) > 10:
        history.pop(0)
    recommendation = get_recommendation(query)
    if query:
        urls = search_engine.search(query.split())
        return render_template('search_results_template.html', urls = urls, query = query, recommendation = recommendation)
    else:
        return '<p>Please enter a search term.</p>', 400


