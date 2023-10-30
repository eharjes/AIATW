import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url
        self.visited = set()

    def crawl(self):
        stack = [self.start_url]
        while stack:
            url = stack.pop()
            if url not in self.visited:
                # print(f"Processing: {url}")  
                self.visited.add(url)
                content = self.get_content(url)
                if content is not None:
                    links = self.get_links(content, url)
                    stack.extend(links)

    def get_content(self, url):
        try:
            response = requests.get(url, timeout=0.05)
            if response.status_code != 404 and 'text/html' in response.headers['Content-Type']:
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
            links.append(url)
        return links