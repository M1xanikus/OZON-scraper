import json
import re
from lxml import html

class HTMLConfigUpdater:
    def __init__(self, downloaded_html: str, template_html_file: str, config_file: str = "config.json"):
        """
        :param downloaded_html: HTML-код, скачанный с сайта
        :param template_html_file: Путь к файлу с шаблонным HTML
        :param config_file: Путь к файлу конфигурации
        """
        self.downloaded_html = downloaded_html
        self.template_html_file = template_html_file
        self.config_file = config_file

        # Загружаем шаблонный HTML
        with open(template_html_file, "r", encoding="utf-8") as f:
            self.template_html = f.read()

        # Загружаем конфиг
        with open(config_file, "r", encoding="utf-8") as f:
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
        Обновляет конфигурационный JSON, заменяя изменённые классы
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
        else:
            print("Изменений не найдено.")

