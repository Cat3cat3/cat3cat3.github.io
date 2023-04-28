import requests 
from bs4 import BeautifulSoup

url = "https://www.baidu.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

links = soup.find_all("a")
nodes = []
edges = []
for link in links: 
    url = link["href"]
    nodes.append({"label": url})
    edges.append({"source": nodes.index(nodes[-2]), "target": nodes.index(nodes[-1])})

# 导入nodes和edges到Gephi,进行可视化和分析