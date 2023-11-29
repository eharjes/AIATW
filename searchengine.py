from crawler import Crawler
import os
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, AndGroup
from bs4 import BeautifulSoup
import re
import numpy as np
import requests



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
                content = self.clean_text(content)
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

            # Using the AndGroup to require all words in the query
            parser = QueryParser("content", ix.schema, group=AndGroup)
            # Create a query string that includes all words
            query_str = ' AND '.join(words)
            # Parse the query string
            query = parser.parse(query_str)

            # Perform the search
            results = searcher.search(query,limit=100)

            processed_results = self.process_search_results(results)
            # Collect the URLs from the results
            urls = [result['url'] for result in results]
            word_occurrences = [0] * len(urls)
            context = [0] * len(urls)
            empty = ['', ' ']

            # Iterate through the results and count word occurrences
            for indx, result in enumerate(results):
                # content = result['content'].lower().split()  # Convert content to lowercase and split into words
                soup = BeautifulSoup(result['content'], 'html.parser')
                text_content = soup.get_text(separator=' ', strip=True).lower()
                content = re.split(r'\W+', text_content)
                
                for spot, word in enumerate(content):
                    if word in words:
                        word_occurrences[indx] += 1
                        context[indx] = content[spot-4: spot+5]
                        context[indx] = " ".join(context[indx])

            # Convert the dictionary to a list of tuples and sort by count in descending order
            urls_context = zip(urls, context)
            sorted_occur_urls = [0] * len(word_occurrences)

            for i, (context_word, url) in enumerate(urls_context):
                # check if word occured at all
                if word_occurrences[i] > 0:
                    sorted_occur_urls[i] = [word_occurrences[i], url, context_word]
            sorted_occur_urls = [elem for elem in sorted_occur_urls if elem != 0]
            sorted_occur_urls = sorted(sorted_occur_urls, reverse = True)
            # sorted_urls = [x[1] for x in sorted_occur_urls]
            # sorted_occurrences = [x[0] for x in sorted_occur_urls]

        return sorted_occur_urls
    
    def clean_text(self, html_content: str) -> str:
        """
        Clean the HTML content and extract human-readable text.

        :param html_content: The HTML content to be cleaned.
        :return: Cleaned, human-readable text.
        """
        # Parse HTML content
        # only execute if there is any content at all
        if html_content is not None:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()

            # Get text and replace HTML entities
            html_content = soup.get_text()

            # Replace multiple spaces with a single space and strip leading/trailing whitespace
            html_content = re.sub(r'\s+', ' ', html_content).strip()

        return html_content



    def process_search_results(self, results):
        processed_results = [dict(hit) for hit in results]
        # if self.__stored_content:
        highlights = [hit.highlights("content") for hit in results]
        highlights = [BeautifulSoup(highlight, "html.parser").get_text() for highlight in highlights]
        for i, highlight in enumerate(highlights):
            processed_results[i]["highlight"] = highlight
        return tuple(processed_results)