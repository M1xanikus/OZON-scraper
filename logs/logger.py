import os
import time
class Logger:
    def __init__(self, log_file: str = "log.txt"):
        """
        Инициализация класса Logger.

        :param log_file: Имя файла для записи логов.
        """
        # Создаем папку logs, если она не существует
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)

        # Указываем полный путь к файлу логов
        self.log_file = os.path.join(self.logs_dir, log_file)

    def log(self, message: str):
        """
        Запись сообщения в лог-файл.

        :param message: Сообщение для записи.
        """
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
