from crawler import Crawler
import os
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, AndGroup
from bs4 import BeautifulSoup
import re
import requests
from bs4.element import Comment


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
        words = [word.lower() for word in words]

        # Use Whoosh's searcher
        with ix.searcher() as searcher:


            # Using the AndGroup to require all words in the query
            parser = QueryParser("content", ix.schema, group=AndGroup)
            # Create a query string that includes all words
            query_str = ' AND '.join(words)

            # Parse the query string
            query = parser.parse(query_str)

            # Perform the search
            results = searcher.search(query)
            processed_results = self.process_search_results(results)

            # Collect the URLs from the results
            urls = [result['url'] for result in processed_results]

            word_occurrences = [0] * len(urls)
            context = [0] * len(urls)
            empty = ['', ' ']

            # Iterate through the results and count word occurrences
            for indx, (result, url) in enumerate(zip(processed_results, urls)):
                # content = result['content'].lower().split()  # Convert content to lowercase and split into words
                # content = re.split('(\W+?)', result['content'].lower())
                # content = [el for el in content if el not in empty]

                split_soup, split_soup_lower = get_beautiful_text(url, )

                for spot, word_lower in enumerate(split_soup_lower):
                    if word_lower in words:
                        word_occurrences[indx] += 1
                        context[indx] = split_soup[spot-4: spot+5]
                        context[indx] = " ".join(context[indx])


            # Convert the dictionary to a list of tuples and sort by count in descending order
            context_urls = zip(context, urls)
            word_con_urls_tit = self.get_merged_list(context_urls, word_occurrences)

        return word_con_urls_tit



    def process_search_results(self, results):
        processed_results = [dict(hit) for hit in results]
        # if self.__stored_content:
        highlights = [hit.highlights("content") for hit in results]
        highlights = [BeautifulSoup(highlight, "html.parser").get_text() for highlight in highlights]
        for i, highlight in enumerate(highlights):
            processed_results[i]["highlight"] = highlight
        return tuple(processed_results)


    def get_merged_list(self, context_urls, word_occurrences):
        word_con_urls_tit = [0] * len(word_occurrences)

        for i, (context_word, url) in enumerate(context_urls):
            soup = BeautifulSoup(requests.get(url).content, 'html.parser')
            title = soup.title.string

            if word_occurrences[i] > 0:
                word_con_urls_tit[i] = [word_occurrences[i], context_word, url, title]

        word_con_urls_tit = [i for i in word_con_urls_tit if i != 0]
        word_con_urls_tit = sorted(word_con_urls_tit, reverse=True)

        return word_con_urls_tit


def tag_visible(element):
    if element.parent.name in ['meta']:
        # ['style', 'script', 'head', 'meta', 'title', '[document]']
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_beautiful_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    texts = soup.findAll(text=True)

    visible_texts_soup = u" ".join(t.strip() for t in filter(tag_visible, texts))

    split_soup = visible_texts_soup.split()
    split_soup_lower = [word.lower() for word in split_soup]

    return split_soup, split_soup_lower