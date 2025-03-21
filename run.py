import os

from scraper.pageScraper import PageScraper
from htmlParser.htmlProductParser import HTMLProductParser

if __name__ == "__main__":
    '''URL = "https://ozon.by/product/krossovki-lexsan-1585614406/?abt_att=1&at=XQtkZZ6GBFE1vAP4uLNx2rYTV3ppyWf56XqyrhBEwmOz&from_sku=1585614406&oos_search=false&origin_referer=ozon.by&tab=reviews"
    scraper = PageScraper(URL)
    html = scraper.get_page_html()
'''
    file_name = "washing_machine.html"
    subdirectory = "htmldata"
    file_path = os.path.join(os.getcwd(), subdirectory, file_name)
    with open(file_path,'r',encoding='utf-8') as file:
        html = file.read()
    if html:
        parser = HTMLProductParser(html)
        print(parser.get_product_data())
        print(parser.get_reviews())
    else:
        print("Не удалось получить HTML страницы.")
