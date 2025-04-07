import os
import sys
from typing import List, Dict, Any, Optional

# Добавляем корневую директорию проекта в путь Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from scraper.categoryPageDownloader import CategoryPageDownloader
from scraper.pageDownloader import PageDownloader
from scraper.batchDownloader import BatchDownloader
from htmlParser.htmlMainPageParser import HTMLMainPageLinksParser
from htmlParser.configUpdater.htmlConfigUpdater import HTMLConfigUpdater
from htmlParser.htmlProductParser import HTMLProductParser

class OzonScraperFacade:
    """
    Фасад для удобного использования функциональности скрапера OZON.
    Предоставляет простой интерфейс для всех основных операций.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Инициализация фасада.
        
        Args:
            base_dir: Базовая директория для сохранения файлов. 
                     Если не указана, используется директория проекта.
        """
        self.base_dir = base_dir or project_root
        self.htmldata_dir = os.path.join(self.base_dir, "htmldata")
        self.categories_dir = os.path.join(self.htmldata_dir, "categories")
        self.config_dir = os.path.join(self.base_dir, "htmlParser", "configUpdater")
        self.json_dir = os.path.join(self.base_dir, "json_data")
        
        # Создаем необходимые директории
        os.makedirs(self.htmldata_dir, exist_ok=True)
        os.makedirs(self.categories_dir, exist_ok=True)
        os.makedirs(os.path.join(self.htmldata_dir, "html_config"), exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
    
    def download_product_page(self, product_url: str) -> Dict[str, Any]:
        """
        Загружает страницу продукта и возвращает информацию о загрузке.
        
        Args:
            product_url: URL продукта на OZON.
            
        Returns:
            Словарь с информацией о загрузке.
        """
        try:
            with PageDownloader(product_url, self.htmldata_dir) as downloader:
                file_path = downloader.save_html_to_file()
                
                if not file_path:
                    return {
                        "success": False,
                        "message": "Не удалось загрузить страницу продукта",
                        "file_path": None
                    }
                
                # Читаем HTML
                with open(file_path, 'r', encoding='utf-8') as file:
                    html = file.read()
                
                # Извлекаем имя файла
                file_name = os.path.basename(file_path)
                
                return {
                    "success": True,
                    "message": "Страница продукта успешно загружена",
                    "file_path": file_path,
                    "html": html,
                    "file_name": file_name
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при загрузке страницы продукта: {str(e)}",
                "file_path": None
            }
    
    def parse_product_data(self, html: str, file_name: str) -> Dict[str, Any]:
        """
        Парсит данные продукта из HTML.
        
        Args:
            html: HTML-код страницы продукта.
            file_name: Имя файла (без расширения).
            
        Returns:
            Словарь с данными продукта.
        """
        try:
            parser = HTMLProductParser(html, file_name.rstrip('.html'))
            product_data = parser.get_product_data()
            
            return {
                "success": True,
                "message": "Данные продукта успешно извлечены",
                "product_data": product_data
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при извлечении данных продукта: {str(e)}",
                "product_data": None
            }
    
    def update_config(self, html: str) -> Dict[str, Any]:
        """
        Обновляет конфигурацию на основе HTML.
        
        Args:
            html: HTML-код страницы продукта.
            
        Returns:
            Словарь с информацией об обновлении конфигурации.
        """
        try:
            # Путь к файлу шаблона HTML
            template_html_file = os.path.join(self.htmldata_dir, "html_config", "config_html_file.html")
            
            # Путь к файлу конфигурации
            config_file = os.path.join(self.config_dir, "config.json")
            
            # Создаем экземпляр класса HTMLConfigUpdater
            updater = HTMLConfigUpdater(html, template_html_file, config_file)
            
            # Анализируем и обновляем конфигурацию
            result = updater.update_config()
            
            return {
                "success": True,
                "message": "Конфигурация успешно обновлена",
                "config_updated": result
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при обновлении конфигурации: {str(e)}",
                "config_updated": False
            }
    
    def download_category_page(self, category_name: str) -> Dict[str, Any]:
        """
        Загружает страницу категории и возвращает информацию о загрузке.
        
        Args:
            category_name: Название категории для поиска на OZON.
            
        Returns:
            Словарь с информацией о загрузке.
        """
        try:
            with CategoryPageDownloader(category_name, self.categories_dir) as downloader:
                file_path = downloader.save_html_to_file()
                
                if not file_path:
                    return {
                        "success": False,
                        "message": "Не удалось загрузить страницу категории",
                        "file_path": None
                    }
                
                # Читаем HTML
                with open(file_path, 'r', encoding='utf-8') as file:
                    html = file.read()
                
                return {
                    "success": True,
                    "message": "Страница категории успешно загружена",
                    "file_path": file_path,
                    "html": html
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при загрузке страницы категории: {str(e)}",
                "file_path": None
            }
    
    def extract_product_links(self, html: str, links_file: str = "product_links.txt") -> Dict[str, Any]:
        """
        Извлекает ссылки на продукты из HTML.
        
        Args:
            html: HTML-код страницы.
            links_file: Имя файла для сохранения ссылок.
            
        Returns:
            Словарь с информацией об извлечении ссылок.
        """
        try:
            # Парсим HTML для извлечения ссылок на продукты
            parser = HTMLMainPageLinksParser(html)
            product_links = parser.get_product_links()
            
            # Сохраняем ссылки в файл
            full_links_file = os.path.join(self.base_dir, links_file)
            parser.save_links_to_txt(product_links, full_links_file)
            
            return {
                "success": True,
                "message": f"Успешно извлечено {len(product_links)} ссылок на продукты",
                "links_count": len(product_links),
                "links_file": full_links_file,
                "links": product_links
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при извлечении ссылок на продукты: {str(e)}",
                "links_count": 0,
                "links_file": None,
                "links": []
            }
    
    def process_category(self, category_name: str, links_file: str = "product_links.txt") -> Dict[str, Any]:
        """
        Обрабатывает категорию: загружает страницу и извлекает ссылки на продукты.
        
        Args:
            category_name: Название категории для поиска на OZON.
            links_file: Имя файла для сохранения ссылок.
            
        Returns:
            Словарь с информацией об обработке категории.
        """
        # Загружаем страницу категории
        download_result = self.download_category_page(category_name)
        
        if not download_result["success"]:
            return {
                "success": False,
                "message": f"Не удалось обработать категорию '{category_name}': {download_result['message']}",
                "category_name": category_name,
                "links_count": 0
            }
        
        # Извлекаем ссылки на продукты
        links_result = self.extract_product_links(download_result["html"], links_file)
        
        return {
            "success": links_result["success"],
            "message": links_result["message"],
            "category_name": category_name,
            "links_count": links_result["links_count"],
            "links_file": links_result["links_file"]
        }
    
    def process_product(self, product_url: str) -> Dict[str, Any]:
        """
        Обрабатывает продукт: загружает страницу, извлекает данные и обновляет конфигурацию.
        
        Args:
            product_url: URL продукта на OZON.
            
        Returns:
            Словарь с информацией об обработке продукта.
        """
        # Загружаем страницу продукта
        download_result = self.download_product_page(product_url)
        
        if not download_result["success"]:
            return {
                "success": False,
                "message": f"Не удалось обработать продукт: {download_result['message']}",
                "product_url": product_url
            }
        
        # Извлекаем данные продукта
        parse_result = self.parse_product_data(download_result["html"], download_result["file_name"])
        
        # Обновляем конфигурацию
        config_result = self.update_config(download_result["html"])
        
        return {
            "success": parse_result["success"] and config_result["success"],
            "message": f"Продукт обработан. Парсинг: {parse_result['message']}, Конфигурация: {config_result['message']}",
            "product_url": product_url,
            "product_data": parse_result.get("product_data"),
            "config_updated": config_result.get("config_updated", False)
        }
    
    def batch_download_products(self, links_file: str = "product_links.txt", limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Пакетно скачивает товары из файла с ссылками и сохраняет их в JSON.
        
        Args:
            links_file: Путь к файлу с ссылками на товары.
            limit: Максимальное количество товаров для скачивания.
                  Если None, скачиваются все товары.
            
        Returns:
            Словарь с результатами скачивания.
        """
        try:
            # Полный путь к файлу с ссылками
            full_links_file = os.path.join(self.base_dir, links_file)
            
            # Проверяем существование файла
            if not os.path.exists(full_links_file):
                return {
                    "success": False,
                    "message": f"Файл с ссылками не найден: {full_links_file}",
                    "downloaded": 0,
                    "total": 0
                }
            
            # Создаем экземпляр BatchDownloader
            batch_downloader = BatchDownloader(full_links_file, self.htmldata_dir)
            
            # Запускаем пакетное скачивание
            result = batch_downloader.download_all(limit)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при пакетном скачивании товаров: {str(e)}",
                "downloaded": 0,
                "total": 0
            } 