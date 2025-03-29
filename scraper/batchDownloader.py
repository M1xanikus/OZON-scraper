import os
from scraper.pageDownloader import PageDownloader
from htmlParser.htmlProductParser import HTMLProductParser
from JSONConverter.jsonProductConverter import JSONProductConverter  # Предположим, что у вас есть класс JSONConverter

class BatchDownloader:
    def __init__(self, links_file: str, download_path: str, used_links_file: str = "used_links.txt"):
        """
        Инициализация BatchDownloader.

        :param links_file: Путь к файлу с ссылками на товары.
        :param download_path: Папка для сохранения HTML-файлов.
        :param used_links_file: Файл для хранения использованных ссылок.
        """
        self.links_file = links_file
        self.download_path = download_path
        self.used_links_file = used_links_file

    def _load_used_links(self) -> set:
        """
        Загружает использованные ссылки из файла.

        :return: Множество использованных ссылок.
        """
        if not os.path.exists(self.used_links_file):
            return set()

        with open(self.used_links_file, "r", encoding="utf-8") as file:
            return set(file.read().splitlines())

    def _save_used_link(self, url: str):
        """
        Сохраняет использованную ссылку в файл.

        :param url: Ссылка для сохранения.
        """
        with open(self.used_links_file, "a", encoding="utf-8") as file:
            file.write(url + "\n")

    def parse_product_page(self, file_name: str) -> dict:
        """
        Парсит HTML-файл и возвращает данные о товаре в виде словаря.

        :param file_name: Имя HTML-файла.
        :return: Словарь с данными о товаре.
        """
        file_path = os.path.join(self.download_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            html = file.read()
            if html:
                parser = HTMLProductParser(html, file_name.rstrip('.html'))
                return parser.get_product_data()  # Возвращаем словарь
        return {}

    def download_all(self):
        """
        Скачивает все страницы товаров из файла с ссылками.
        """
        # Чтение всех ссылок из файла
        with open(self.links_file, "r", encoding="utf-8") as file:
            links = file.read().splitlines()

        total_links = len(links)
        if total_links == 0:
            print("Файл с ссылками пуст.")
            return

        print(f"Найдено {total_links} ссылок для скачивания.")

        # Загрузка использованных ссылок
        used_links = self._load_used_links()

        # Скачивание каждой страницы
        for index, url in enumerate(links, start=1):
            try:
                # Пропускаем ссылку, если она уже использовалась
                if url in used_links:
                    print(f"Ссылка уже использовалась: {url}")
                    continue

                print(f"Скачивание [{index}/{total_links}] {url}")
                with PageDownloader(url, self.download_path) as downloader:
                    file_path = downloader.save_html_to_file()

                    # Извлекаем имя файла из пути
                    file_name = os.path.basename(file_path)

                    # Парсинг HTML-файла
                    product_data = self.parse_product_page(file_name)
                    if product_data:
                        print("Данные о товаре:", product_data)

                      # Преобразование в JSON и сохранение
                        json_converter = JSONProductConverter(product_data)
                        json_converter.to_json_file()

                        # Удаление HTML-файла
                        os.remove(file_path)
                        print(f"HTML-файл удален: {file_path}")

                        # Сохранение использованной ссылки
                        self._save_used_link(url)
                        used_links.add(url)

                # Вычисление и вывод прогресса
                progress = (index / total_links) * 100
                print(f"Прогресс: {progress:.2f}% завершено\n")

            except Exception as e:
                print(f"Ошибка при скачивании {url}: {e}")

        print("Скачивание завершено.")