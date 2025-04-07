import json
import re
import os
import shutil
from pathlib import Path
from lxml import html


class HTMLConfigUpdater:
    def __init__(self, downloaded_html: str, template_html_file: str, config_file: str = None):
        """
        :param downloaded_html: HTML-код, скачанный с сайта
        :param template_html_file: Путь к файлу с шаблонным HTML (и папка назначения)
        :param config_file: Путь к файлу конфигурации
        """
        self.downloaded_html = downloaded_html
        self.template_html_file = template_html_file
        
        # If config_file is not provided, use the default path in the same directory as this script
        if config_file is None:
            config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.config_file = config_file
        
        self.config_html_file = "config_html_file.html"  # Имя конечного файла

        # Загружаем шаблонный HTML
        with open(template_html_file, "r", encoding="utf-8") as f:
            self.template_html = f.read()

        # Загружаем конфиг
        with open(self.config_file, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def extract_xpath_to_class(self, html_content):
        """
        Извлекает соответствие {XPath: [список классов]} из HTML-кода
        """
        tree = html.fromstring(html_content)
        mapping = {}

        for element in tree.xpath('//*[@class]'):  # Ищем все элементы с атрибутом class
            xpath = tree.getroottree().getpath(element)  # Исправленный метод получения XPath
            classes = element.get('class').split()  # Разбиваем строку классов на список
            mapping[xpath] = classes

        return mapping

    def find_class_changes(self):
        """
        Находит изменения классов в новой версии страницы
        :return: словарь {XPath: (старые классы, новые классы)}
        """
        old_tree = self.extract_xpath_to_class(self.template_html)
        new_tree = self.extract_xpath_to_class(self.downloaded_html)

        changed_classes = {}

        for xpath, old_classes in old_tree.items():
            new_classes = new_tree.get(xpath, None)

            # Если класс изменился, сохраняем
            if new_classes is not None and old_classes != new_classes:
                changed_classes[xpath] = (old_classes, new_classes)

        return changed_classes

    def update_config(self):
        """
        Обновляет конфигурационный JSON, заменяя изменённые классы.
        Если изменения найдены, перемещает новый HTML файл в папку назначения и переименовывает.
        """
        changes = self.find_class_changes()
        updated = False  # Флаг, чтобы понять, были ли обновления

        def update_class(obj):
            """ Рекурсивно ищет class и обновляет его """
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "class" and isinstance(value, str):
                        for xpath, (old_classes, new_classes) in changes.items():
                            old_class_str = " ".join(old_classes)
                            if value == old_class_str:  # Если нашли совпадение
                                obj[key] = " ".join(new_classes)
                                print(f"Обновлено: {value} → {obj[key]}")
                                nonlocal updated
                                updated = True
                    else:
                        update_class(value)

        # Обходим JSON и обновляем классы
        update_class(self.config)

        if updated:
            # Записываем обновленный конфиг
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"Конфиг {self.config_file} успешно обновлён!")

            # Перемещаем и переименовываем HTML файл
            self._move_and_rename_html_file()

            return True
        else:
            print("Изменений не найдено.")
            return False

    def _move_and_rename_html_file(self):
        """
        Перемещает новый HTML файл из htmldata/ в папку проекта/htmldata/html_config/
        и переименовывает его в config_html_file.html, заменяя существующий
        """
        # Определяем пути
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        # Get the downloaded file name from the HTML content
        downloaded_file = "krossovki-lexsan-1585614406.html"  # This should match the file name from PageDownloader
        source_file = Path(os.path.join(project_root, "htmldata", downloaded_file))
        dest_folder = Path(os.path.join(project_root, "htmldata", "html_config"))
        dest_file = dest_folder / "config_html_file.html"

        # Проверяем существование исходного файла
        if not source_file.exists():
            raise FileNotFoundError(f"Исходный файл не найден: {source_file}")

        # Создаем папку назначения если не существует
        dest_folder.mkdir(parents=True, exist_ok=True)

        # Удаляем старый файл в папке html_config если существует
        old_files = list(dest_folder.glob("*.html"))
        for old_file in old_files:
            try:
                os.remove(old_file)
                print(f"Удален старый HTML файл: {old_file}")
            except OSError as e:
                print(f"Ошибка при удалении файла {old_file}: {e}")

        # Копируем и переименовываем файл
        try:
            shutil.copy2(source_file, dest_file)
            print(f"Файл успешно скопирован и переименован: {source_file} → {dest_file}")

            # Обновляем ссылки в классе
            self.template_html_file = str(dest_file)
            with open(self.template_html_file, "r", encoding="utf-8") as f:
                self.template_html = f.read()

            # Удаляем исходный файл после успешного копирования
            os.remove(source_file)
            print(f"Исходный файл {source_file} удален")

        except Exception as e:
            print(f"Ошибка при копировании файла: {e}")
            raise