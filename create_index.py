from searchengine import SearchEngine
import whoosh

# builds the index of size {max_pages} in domain {domain}
domain      = 'https://en.wikipedia.org/wiki/Home_page'
max_pages   = 100

if __name__=='__main__':
    search_engine = SearchEngine(domain, max_pages, create_index=True)
    search_engine.build_index()
    search_history = []