import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, start_url, max_pages):
        self.start_url = start_url
        self.visited = set()
        self.max_pages = max_pages
        self.session = requests.Session()  # Session object for the reuse of the same TCP connection
        self.base_domain = urlparse(self.start_url).netloc

    def crawl(self):
        stack = [self.start_url]
        while stack and len(self.visited) < self.max_pages:
            url = stack.pop()
            if url not in self.visited:
                self.visited.add(url)
                content = self.get_content(url)
                if content is not None:
                    links = self.get_links(content, url)
                    stack.extend(links)

    def get_content(self, url):
        try:
            response = self.session.get(url, timeout=5)
            # Check the response header for 'text/html' content type
            if (response.status_code != 404 and 'Content-Type' in response.headers and
                    'text/html' in response.headers['Content-Type']):
                return response.text
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        return None

    def get_links(self, content, base_url):
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            url = urljoin(base_url, href)
            if self.is_same_server(url):
                links.append(url)
        return links

    def is_same_server(self, url):
        """
        Check whether domain of given URL matches the base domain

        :param: new URL to check
        :return: Whether URL's match (boolean)
        """
        return urlparse(url).netloc == self.base_domain