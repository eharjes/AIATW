from flask import Flask, request, render_template
from searchengine import SearchEngine  # Assuming your search engine code is in search_engine.py

app = Flask(__name__)
search_engine = SearchEngine('https://vm009.rz.uos.de/crawl/index.html', 4000)
search_engine.build_index()

history = []
length = 0
@app.route('/')
def home():

    return render_template('home_page_template2.html', history = history, length = length)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query not in history:
        history.append(query)
    if len(history) > 10:
        history.pop(0)
    length = len(history)
    if query:
        urls = search_engine.search(query.split())
        return render_template('search_results_template.html', urls=urls, query=query)
    else:
        return '<p>Please enter a search term.</p>', 400


