import requests
from bs4 import BeautifulSoup

r = requests.get('https://www.uos.de')
# print(r)
print(r.status_code)
print(r.headers)
# print(r.content)
soup = BeautifulSoup(r.content, 'html.parser')
print(soup.title.text)
print(soup.text)
for l in soup.find_all("a"):
    print(l['href'])
    print(l.text)