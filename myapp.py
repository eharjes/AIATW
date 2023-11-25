from flask import Flask, request, render_template
from searchengine import SearchEngine  # Assuming your search engine code is in search_engine.py
import whoosh

# initialize all variables
app = Flask(__name__)
search_engine = SearchEngine('https://vm009.rz.uos.de/crawl/index.html', 4000)
search_engine.build_index()
search_history = []

@app.route('/')
def home():
    return render_template('home_page_template2.html', history = reversed(search_history))

@app.route('/search')
def search():
    # receive query
    query = request.args.get('q', '')
    if query:
        # find urls in our index
        sorted_urls_occurrences, other_results, context = search_engine.search(query.split())
        # initialize recommendation as empty string that only fills if correct_query() returns something different than the query
        recommendation = ""
        # expand search_history without duplicates
        if query not in search_history:
            search_history.append(query)
        # keep search_history to at most 10 entries
        if len(search_history) > 10:
            search_history.pop(0)
        # use the previously created index for our recommendations (only used in html when the query does not return any urls)
        ix = search_engine.ix
        qp = whoosh.qparser.QueryParser("content", ix.schema)
        q = qp.parse(query)
        with ix.searcher() as searcher:
            corrected = searcher.correct_query(q, query)
            # if our query is different from the with our index corrected one we get recommendations
            if corrected.query != q:
                recommendation = corrected.string
        return render_template('search_results_template.html', urls_occurrences=sorted_urls_occurrences, query=query, recommendation = recommendation, other_results = other_results, context=context)
    else:
        return '<p>Please enter a search term.</p>', 400


