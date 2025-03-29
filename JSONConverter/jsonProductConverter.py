import json
import os
from typing import Any, Dict, Optional
from logs.logger import Logger
class JSONProductConverter:
    def __init__(self, data: Dict[str, Any], log_file: str = "log.txt"):
        """
        Инициализация конвертера.

        :param data: Данные для преобразования в JSON (словарь).
        :param logger: Объект класса Logger для логирования.
        """
        self.data = data
        self.logger = Logger(log_file)

    def to_json_string(self, indent: Optional[int] = 4) -> str:
        """
        Преобразует данные в JSON-строку.

        :param indent: Отступ для форматирования JSON. Если None, JSON будет компактным.
        :return: JSON-строка.
        """
        self.logger.log("Преобразование данных в JSON-строку.")
        return json.dumps(self.data, indent=indent, ensure_ascii=False)

    def to_json_file(self, folder_path: str = "jsondata", indent: Optional[int] = 4):
        """
        Сохраняет данные в JSON-файл.

        :param folder_path: Папка для сохранения JSON-файлов.
        :param indent: Отступ для форматирования JSON. Если None, JSON будет компактным.
        """
        try:
            # Извлекаем product_name из данных
            product_name = self.data.get("URL товара", "").split("/")[-2]  # Берем часть URL
            if not product_name:
                error_msg = "Не удалось извлечь product_name из данных."
                self.logger.log(error_msg)
                raise ValueError(error_msg)

            # Создаем папку, если она не существует
            os.makedirs(folder_path, exist_ok=True)
            self.logger.log(f"Папка '{folder_path}' создана или уже существует.")

            # Формируем путь к файлу
            file_path = os.path.join(folder_path, f"{product_name}.json")
            self.logger.log(f"Формирование пути к файлу: {file_path}")

            # Записываем данные в файл
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=indent, ensure_ascii=False)

            self.logger.log(f"Файл успешно сохранен: {file_path}")

        except Exception as e:
            error_msg = f"Ошибка при сохранении JSON-файла: {e}"
            self.logger.log(error_msg)
            raise