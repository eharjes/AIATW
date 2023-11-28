import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Crawler:
    """
    A Crawler class to visit and extract links from a given start URL up to a specified number of pages.
    """

    def __init__(self, start_url: str, max_pages: int):
        """
        Initializes the Crawler with a starting URL and a maximum number of pages to visit.

        :param start_url: The URL where the crawler will begin.
        :param max_pages: The maximum number of pages to visit.
        """
        self.start_url = start_url
        self.visited = set()
        self.max_pages = max_pages
        self.session = requests.Session()  # Session object for reusing the same TCP connection
        self.base_domain = urlparse(self.start_url).netloc

    def crawl(self):
        """Performs the crawling operation, visiting pages and collecting links."""
        stack = [self.start_url]
        while stack and len(self.visited) < self.max_pages:
            url = stack.pop()
            if url not in self.visited:
                self.visited.add(url)
                if not(self.get_content(url) == None):
                    content, _ = self.get_content(url)
                # if content is not None:
                    links = self.get_links(content, url)
                    stack.extend(links)

    def get_content(self, url: str) -> str:
        """
        Fetches the content from the specified URL.

        :param url: The URL to fetch the content from.
        :return: The content of the URL as text, or None if the request fails.
        """
        try:
            response = self.session.get(url, timeout=5)
            if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find the <title> tag
                title_tag = soup.find('title')
                #print(title_tag)
                #print(response.text)
                return response.text, title_tag
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        print("it is none?!")
        return None

    def get_links(self, content: str, base_url: str) -> list:
        """
        Extracts all the links from the content of the given base URL.

        :param content: The HTML content to extract links from.
        :param base_url: The base URL to resolve relative links.
        :return: A list of absolute URLs found within the content.
        """
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            url = urljoin(base_url, href)
            if self.is_same_server(url):
                links.append(url)
        return links

    def is_same_server(self, url: str) -> bool:
        """
        Checks if the domain of the given URL matches the base domain.

        :param url: The URL to check.
        :return: True if the URL's domain matches the base domain; False otherwise.
        """
        return urlparse(url).netloc == self.base_domain
