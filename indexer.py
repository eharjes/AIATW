from bs4 import BeautifulSoup
import re


class Indexer:
    def __init__(self):
        self.index = {}

    def add_to_index(self, url, content):
        words = self.get_words(content)
        for word in words:
            # print(f"Adding: {word}")
            if word not in self.index:
                self.index[word] = [(url, 1)]
            else:
                for i, (existing_url, freq) in enumerate(self.index[word]):
                    if existing_url == url:
                        self.index[word][i] = (url, freq + 1)
                        break
                else:
                    self.index[word].append((url, 1))

    def get_words(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        words = text.split()
        words = [re.sub(r'[^a-zA-Z]', '', word) for word in words]
        words = [word for word in words if word]
        return words
