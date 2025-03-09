import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import atexit


class PageScraper:
    def __init__(self, url: str, chrome_version: int = 134):
        self.url = url
        self.chrome_version = chrome_version
        self.driver = None
        atexit.register(self.close_driver)  # Гарантируем закрытие драйвера при завершении программы

    def _init_driver(self):
        """Создает и настраивает Selenium-драйвер"""
        options = Options()
        options.add_argument("--headless=new")  # Без GUI
        options.add_argument("--disable-blink-features=AutomationControlled")  # Отключаем детектирование Selenium
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")

        try:
            self.driver = uc.Chrome(options=options, version_main=self.chrome_version)
            return True
        except Exception as e:
            print(f"[ERROR] Ошибка при запуске драйвера: {e}")
            return False

    def get_page_html(self):
        """
        Открывает страницу и получает её HTML-код.
        :return: HTML-код страницы или None при ошибке
        """
        if self.driver is None:
            if not self._init_driver():
                return None  # Не удалось запустить драйвер

        try:
            print(f"[INFO] Открываем страницу: {self.url}")
            self.driver.get(self.url)
            time.sleep(random.uniform(5, 10))  # Имитация поведения пользователя
            html = self.driver.page_source
            print("[SUCCESS] Данные получены!")
            return html

        except Exception as e:
            print(f"[ERROR] Ошибка при получении данных: {e}")
            return None

        finally:
            self.close_driver()  # Закрываем драйвер после выполнения

    def close_driver(self):
        """Закрывает драйвер, если он активен"""
        if self.driver:
            try:
                if self.driver.service.process and self.driver.service.process.poll() is None:
                    print("[INFO] Закрываем драйвер...")
                    self.driver.quit()
            except Exception as e:
                print(f"[ERROR] Ошибка при закрытии драйвера: {e}")
            finally:
                self.driver = None
                atexit.unregister(self.close_driver)  # Убираем из atexit, если драйвер уже закрыт

