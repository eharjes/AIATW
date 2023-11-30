from searchengine import SearchEngine  # Assuming your search engine code is in search_engine.py
import whoosh

if __name__=='__main__':
    search_engine = SearchEngine('https://en.wikipedia.org/wiki/Home_page', 100, create_index=True)
    search_engine.build_index()
    search_history = []