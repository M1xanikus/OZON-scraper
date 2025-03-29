from htmlParser.htmlProductParser import HTMLProductParser
from scraper.batchDownloader import BatchDownloader
from scraper.pageDownloader import PageDownloader

if __name__ == "__main__":


    LINKS_FILE = "product_links.txt"
    # Папка для сохранения HTML-файлов
    DOWNLOAD_PATH = "htmldata"

    # Создание и запуск BatchDownloader
    batch_downloader = BatchDownloader(LINKS_FILE, DOWNLOAD_PATH)
    batch_downloader.download_all()

