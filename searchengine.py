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

    def search(self, word):
        urls = {url for url, freq in self.indexer.index.get(word, [])}
        # print(self.indexer.index)
        return sorted(urls)
    
if __name__ == "__main__":
    engine = SearchEngine('https://vm009.rz.uos.de/crawl/page1.html', 300)
    engine.build_index()
    search_word = 'glitches'
    result = engine.search(search_word)
    print(f'URLs containing the word {search_word}: {result}')