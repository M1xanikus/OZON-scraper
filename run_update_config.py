import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

from htmlParser.configUpdater.htmlConfigUpdater import HTMLConfigUpdater
from htmlParser.htmlProductParser import HTMLProductParser
from scraper.pageDownloader import PageDownloader

if __name__ == "__main__":
    URL = "https://ozon.by/product/krossovki-lexsan-1585614406/?abt_att=1&at=XQtkZZ6GBFE1vAP4uLNx2rYTV3ppyWf56XqyrhBEwmOz&from_sku=1585614406&oos_search=false&origin_referer=ozon.by&tab=reviews"
    with PageDownloader(URL, "htmldata") as downloader:
        file_path = downloader.save_html_to_file()
    with open(file_path, 'r', encoding='utf-8') as file:
        html = file.read()

    # Путь к файлу krossovki.html в папке htmldata/html_config
    template_html_file = os.path.join(project_root, "htmldata", "html_config", "config_html_file.html")

    # Путь к файлу конфигурации
    config_file = os.path.join(project_root, "htmlParser", "configUpdater", "config.json")
    
    # Создаём экземпляр класса HTMLConfigUpdater 
    updater = HTMLConfigUpdater(html, template_html_file, config_file)

    # Анализируем и обновляем конфигурацию
    updater.update_config()

    """ 
    file_name = os.path.basename(file_path)
    parser = HTMLProductParser(html, file_name.rstrip('.html'))
    print(parser.get_product_data())
    """ 