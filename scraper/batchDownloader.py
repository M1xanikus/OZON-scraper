import os
import json
from typing import Dict, List, Any, Optional
from scraper.pageDownloader import PageDownloader
from htmlParser.htmlProductParser import HTMLProductParser
from JSONConverter.jsonProductConverter import JSONProductConverter  # Предположим, что у вас есть класс JSONConverter

class BatchDownloader:
    def __init__(self, links_file: str, download_path: str, used_links_file: str = "used_links.txt"):
        """
        Инициализация BatchDownloader.

        Args:
            links_file: Путь к файлу с ссылками на товары.
            download_path: Папка для сохранения HTML-файлов.
            used_links_file: Файл для хранения использованных ссылок.
        """
        self.links_file = links_file
        self.download_path = download_path
        self.used_links_file = used_links_file
        
        # Создаем директорию для JSON, если она не существует
        self.json_dir = os.path.join(os.path.dirname(download_path), "json_data")
        os.makedirs(self.json_dir, exist_ok=True)

    def _load_used_links(self) -> set:
        """
        Загружает использованные ссылки из файла.

        Returns:
            Множество использованных ссылок.
        """
        if not os.path.exists(self.used_links_file):
            return set()

        with open(self.used_links_file, "r", encoding="utf-8") as file:
            return set(file.read().splitlines())

    def _save_used_link(self, url: str):
        """
        Сохраняет использованную ссылку в файл.

        Args:
            url: Ссылка для сохранения.
        """
        with open(self.used_links_file, "a", encoding="utf-8") as file:
            file.write(url + "\n")

    def parse_product_page(self, file_name: str) -> dict:
        """
        Парсит HTML-файл и возвращает данные о товаре в виде словаря.

        Args:
            file_name: Имя HTML-файла.
            
        Returns:
            Словарь с данными о товаре.
        """
        file_path = os.path.join(self.download_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            html = file.read()
            if html:
                parser = HTMLProductParser(html, file_name.rstrip('.html'))
                return parser.get_product_data()
        return {}

    def save_to_json(self, product_data: Dict[str, Any], product_id: str):
        """
        Сохраняет данные о товаре в JSON-файл.

        Args:
            product_data: Данные о товаре.
            product_id: Идентификатор товара.
        """
        json_file = os.path.join(self.json_dir, f"{product_id}.json")
        with open(json_file, 'w', encoding='utf-8') as file:
            json.dump(product_data, file, ensure_ascii=False, indent=4)

    def download_all(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Скачивает все страницы товаров из файла с ссылками.

        Args:
            limit: Максимальное количество товаров для скачивания.
                  Если None, скачиваются все товары.

        Returns:
            Словарь с результатами скачивания.
        """
        # Чтение всех ссылок из файла
        with open(self.links_file, "r", encoding="utf-8") as file:
            links = file.read().splitlines()

        total_links = len(links)
        if total_links == 0:
            print("Файл с ссылками пуст.")
            return {
                "success": False,
                "message": "Файл с ссылками пуст.",
                "downloaded": 0,
                "total": 0
            }

        # Ограничиваем количество ссылок, если указан лимит
        if limit is not None and limit < total_links:
            links = links[:limit]
            total_links = limit

        print(f"Найдено {total_links} ссылок для скачивания.")

        # Загрузка использованных ссылок
        used_links = self._load_used_links()
        
        # Статистика
        downloaded = 0
        skipped = 0
        errors = 0
        results = []

        # Скачивание каждой страницы
        for index, url in enumerate(links, start=1):
            try:
                # Пропускаем ссылку, если она уже использовалась
                if url in used_links:
                    print(f"Ссылка уже использовалась: {url}")
                    skipped += 1
                    continue

                print(f"Скачивание [{index}/{total_links}] {url}")
                with PageDownloader(url, self.download_path) as downloader:
                    file_path = downloader.save_html_to_file()

                    if not file_path:
                        print(f"Не удалось скачать страницу: {url}")
                        errors += 1
                        continue

                    # Извлекаем имя файла из пути
                    file_name = os.path.basename(file_path)
                    product_id = file_name.rstrip('.html')

                    # Парсинг HTML-файла
                    product_data = self.parse_product_page(file_name)
                    if product_data:
                        # Сохраняем данные в JSON
                        self.save_to_json(product_data, product_id)
                        
                        # Удаление HTML-файла
                        os.remove(file_path)
                        print(f"HTML-файл удален: {file_path}")

                        # Сохранение использованной ссылки
                        self._save_used_link(url)
                        used_links.add(url)
                        
                        downloaded += 1
                        results.append({
                            "url": url,
                            "product_id": product_id,
                            "success": True
                        })
                    else:
                        print(f"Не удалось извлечь данные о товаре: {url}")
                        errors += 1
                        results.append({
                            "url": url,
                            "success": False,
                            "error": "Не удалось извлечь данные о товаре"
                        })

                # Вычисление и вывод прогресса
                progress = (index / total_links) * 100
                print(f"Прогресс: {progress:.2f}% завершено\n")

            except Exception as e:
                print(f"Ошибка при скачивании {url}: {e}")
                errors += 1
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e)
                })

        print("Скачивание завершено.")
        
        return {
            "success": True,
            "message": f"Скачивание завершено. Скачано: {downloaded}, Пропущено: {skipped}, Ошибок: {errors}",
            "downloaded": downloaded,
            "skipped": skipped,
            "errors": errors,
            "total": total_links,
            "results": results
        }