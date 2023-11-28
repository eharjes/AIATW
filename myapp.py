from flask import Flask, request, render_template
from searchengine import SearchEngine  # Assuming your search engine code is in searchengine.py
import whoosh

# initialize all variables
app = Flask(__name__)
search_engine = SearchEngine('https://vm009.rz.uos.de/crawl/index.html', 10) # use https://vm009.rz.uos.de/crawl/index.html or https://en.wikipedia.org/wiki/Home_page
search_engine.build_index()
search_history = []

@app.route('/')
def home():
    """
    Home page route that renders the main search page with search history.
    
    :return: Rendered template of the home page.
    """
    return render_template('home_page_template2.html', history = reversed(search_history))

@app.route('/search')
def search():
    """
    Search route that processes the search query and renders the search results.
    
    :return: Rendered template of the search results page or an error message for an empty query.
    """
    # receive query
    query = request.args.get('q', '')
    # find urls in our index
    urls = search_engine.search(query.split())
    # initialize recommendation as empty string that only fills if correct_query() returns something different than the query
    recommendation = ""
    # expand search_history without duplicates
    if query not in search_history and query != "":
        search_history.append(query)
    # keep search_history to at most 10 entries
    if len(search_history) > 10:
        search_history.pop(0)
    # use the previously created index for our recommendations (only used in html when the query does not return any urls)
    qp = whoosh.qparser.QueryParser("content", search_engine.ix.schema)
    q = qp.parse(query)
    with search_engine.ix.searcher() as searcher:
        corrected = searcher.correct_query(q, query)
        # if our query is different from the with our index corrected one we get recommendations
        if corrected.query != q:
            recommendation = corrected.string
    return render_template('search_results_template.html',urls = urls, length = len(urls), query = query, recommendation = recommendation)