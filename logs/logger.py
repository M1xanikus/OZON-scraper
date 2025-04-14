import os
import time
import sys
import traceback

class Logger:
    def __init__(self, log_file: str = "log.txt"):
        """
        Инициализация класса Logger.

        :param log_file: Имя файла для записи логов.
        """
        try:
            # Создаем папку logs, если она не существует
            self.logs_dir = "logs"
            os.makedirs(self.logs_dir, exist_ok=True)

            # Указываем полный путь к файлу логов
            self.log_file = os.path.join(self.logs_dir, log_file)
            
            # Проверяем, что файл существует и доступен для записи
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Логгер инициализирован\n")
                
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Логгер инициализирован, файл: {self.log_file}")
        except Exception as e:
            print(f"Ошибка при инициализации логгера: {str(e)}")
            # Используем стандартный вывод в случае ошибки
            self.log_file = None

    def log(self, message: str, level: str = "INFO"):
        """
        Запись сообщения в лог-файл.

        :param message: Сообщение для записи.
        :param level: Уровень логирования (INFO, WARNING, ERROR, DEBUG).
        """
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # Вывод в консоль
        print(log_entry)
        
        # Запись в файл
        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"{log_entry}\n")
            except Exception as e:
                print(f"Ошибка при записи в лог-файл: {str(e)}")
                
    def error(self, message: str, exception: Exception = None):
        """
        Запись сообщения об ошибке в лог-файл.

        :param message: Сообщение об ошибке.
        :param exception: Объект исключения (опционально).
        """
        self.log(message, "ERROR")
        if exception:
            self.log(f"Тип исключения: {type(exception).__name__}", "ERROR")
            self.log(f"Текст исключения: {str(exception)}", "ERROR")
            self.log(f"Стек вызовов: {traceback.format_exc()}", "ERROR")
            
    def warning(self, message: str):
        """
        Запись предупреждения в лог-файл.

        :param message: Сообщение-предупреждение.
        """
        self.log(message, "WARNING")
        
    def debug(self, message: str):
        """
        Запись отладочного сообщения в лог-файл.

        :param message: Отладочное сообщение.
        """
        self.log(message, "DEBUG")
