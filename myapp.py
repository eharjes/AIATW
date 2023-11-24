from flask import Flask, request, render_template
from searchengine import SearchEngine  # Assuming your search engine code is in search_engine.py

app = Flask(__name__)
search_engine = SearchEngine('https://vm009.rz.uos.de/crawl/index.html', 4000)
search_engine.build_index()

search_history = []

@app.route('/')
def home():
    return render_template('home_page_template2.html', history = reversed(search_history))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query not in search_history:
        search_history.append(query)
    if len(search_history) > 10:
        search_history.pop(0)
    recommendation = "hier könnte ihre recommendation stehen"
    if query:
        sorted_urls_occurrences = search_engine.search(query.split())
        return render_template('search_results_template.html', urls_occurrences=sorted_urls_occurrences, query=query, recommendation = recommendation)
    else:
        return '<p>Please enter a search term.</p>', 400


