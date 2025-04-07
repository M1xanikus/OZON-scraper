from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class HTMLMainPageLinksParser:
    def __init__(self, html_code: str, base_url: str = 'https://ozon.by'):
        self.html = html_code
        self.soup = BeautifulSoup(html_code, "html.parser")
        self.base_url = base_url

    def get_product_links(self) -> list[str]:
        product_links = set()
        for a_tag in self.soup.find_all('a', href=True):
            href = a_tag['href']
            if '/product/' in href:
                full_url = urljoin(self.base_url, href)
                parsed_url = urlparse(full_url)
                if 'ozon.by' in parsed_url.netloc:
                    product_links.add(full_url)
        return list(product_links)

    def save_links_to_txt(self, links: list[str], filename: str = 'product_links.txt') -> None:
        with open(filename, 'a', encoding='utf-8') as f:
            for link in links:
                f.write(f"{link}\n")