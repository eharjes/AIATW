from crawler import Crawler
from indexer import Indexer

class SearchEngine:
    def __init__(self, start_url, max_pages):
        self.crawler = Crawler(start_url, max_pages)
        self.indexer = Indexer()

    def build_index(self):
        self.crawler.crawl()
        for url in self.crawler.visited:
            content = self.crawler.get_content(url)
            if content is not None:
                self.indexer.add_to_index(url, content)

    def search(self, words):
        if not isinstance(words, list) or not words:
            raise ValueError("Words must be a non-empty list")
        
        # Retrieve the set of URLs for the first word in the list
        urls = set(url for url, freq in self.indexer.index.get(words[0], []))
        
        # Intersect with the sets of URLs of the other words
        for word in words[1:]:
            urls &= set(url for url, freq in self.indexer.index.get(word, []))
        
        return sorted(urls)
    
if __name__ == "__main__":
    engine = SearchEngine('https://vm009.rz.uos.de/crawl/page1.html', 4000)
    engine.build_index()
    search_words = ['with', 'a']
    result = engine.search(search_words)
    print(f'URLs containing all the words {search_words}: {result}')