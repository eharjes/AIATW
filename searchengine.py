from crawler import Crawler
import os
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, AndGroup

class SearchEngine:
    def __init__(self, start_url, max_pages, index_dir='indexdir'):
        self.crawler = Crawler(start_url, max_pages)
        self.index_dir = index_dir
        # Define the schema for indexing
        self.schema = Schema(
            url=ID(stored=True, unique=True),
            content=TEXT(stored=True)
        )
        # Create or open the index directory
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
            self.ix = create_in(self.index_dir, self.schema)
        else:
            self.ix = open_dir(self.index_dir)

    def build_index(self):
        """
        Builds an index for web pages by crawling and then indexing their content
        initializes an index writer, starts or continues web crawling, retrieves web page content, and adds the content to the index

        :param: none specified, the intern parameters will be used
        :return:initializes an index writer, starts or continues web crawling, retrieves web page content, and adds the content to the index
        """
        if not self.is_index_built():
            writer = self.ix.writer()
            self.crawler.crawl()
            for url in self.crawler.visited:
                content = self.crawler.get_content(url)
                if content is not None:
                    writer.add_document(url=url, content=content)
            writer.commit()
    
    def is_index_built(self):
        """
        Checks if the index directory exists and if there are documents in it

        :param: none specified, the intern parameters will be used
        :return:
        """
        if exists_in(self.index_dir):
            ix = open_dir(self.index_dir)
            with ix.searcher() as searcher:
                return searcher.doc_count() > 0
        return False
    
    def search(self, words):
        """
        Search for pages that contain all the search words.

        :param words: A list of words to search for.
        :return: A list of URLs containing all the search words.
        """
        # Open the existing index directory
        ix = open_dir(self.index_dir)

        # Use Whoosh's searcher
        with ix.searcher() as searcher:
            # print(list(searcher.lexicon("content")))

            # Using the AndGroup to require all words in the query
            parser = QueryParser("content", ix.schema, group=AndGroup)
            # Create a query string that includes all words
            query_str = ' AND '.join(words)
            # Parse the query string
            query = parser.parse(query_str)
            # Perform the search
            results = searcher.search(query)
            # Collect the URLs from the results
            urls = [result['url'] for result in results]

        return urls

if __name__ == "__main__":
    engine = SearchEngine('https://vm009.rz.uos.de/crawl/index.html', 4000)
    engine.build_index()  # Make sure this is commented out if the index is already built and you're just searching
    search_words = ['platypus', 'mammal']
    result = engine.search(search_words)
    print(f'URLs containing all the words {search_words}: {result}')