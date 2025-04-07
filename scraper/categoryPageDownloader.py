import time
import random
import os
import sys
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from logs.logger import Logger

class CategoryPageDownloader:
    def __init__(self, category_name: str, download_path: str, log_file: str = "category_log.txt"):
        """
        Инициализация класса CategoryPageDownloader.

        :param category_name: Название категории для поиска на OZON.
        :param download_path: Путь для сохранения HTML файлов.
        :param log_file: Имя файла для логирования.
        """
        self.download_path = download_path
        self.category_name = category_name
        self.logger = Logger(log_file)
        self.driver = None
        self.base_url = "https://ozon.by"

    def __enter__(self):
        """
        Контекстный менеджер для автоматического запуска драйвера.
        """
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Контекстный менеджер для автоматического закрытия драйвера.
        """
        self.close_driver()

    def setup_driver(self):
        """
        Настройка undetected_chromedriver для обхода блокировок.
        """
        options = uc.ChromeOptions()

        # Случайный User-Agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")

        # Запуск браузера в фоновом режиме (headless)
        options.headless = False  # Браузер не будет открываться визуально

        # Инициализация undetected_chromedriver
        self.driver = uc.Chrome(options=options)
        self.driver.maximize_window()  # Максимизируем окно для лучшей видимости

    def _smooth_scroll(self):
        self.logger.log("Начало прокрутки страницы категории")
        """Плавная прокрутка с общей продолжительностью ~n секунд"""

        start_time = time.time()
        max_duration = 30  # Увеличенное время для категорий, так как они обычно длиннее
        current_position = 0
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")

        # Начальная задержка перед прокруткой
        time.sleep(random.uniform(4, 6))

        while time.time() - start_time < max_duration:
            # Рассчитываем оставшееся время
            remaining = max_duration - (time.time() - start_time)
            if remaining <= 0:
                break

            # Прокрутка с переменным шагом
            scroll_step = random.randint(650, 950)
            current_position += scroll_step

            # Плавный скролл с анимацией
            self.driver.execute_script(f"""
                window.scrollTo({{
                    top: {current_position},
                    behavior: 'smooth'
                }});
            """)

            # Динамическое обновление высоты
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height > scroll_height:
                scroll_height = new_height

            # Адаптивные паузы с учетом оставшегося времени
            base_pause = remaining / 5  # Динамически уменьшаем паузы
            pause = random.uniform(
                max(0.3, base_pause - 0.2),
                min(2.5, base_pause + 0.5)
            )
            time.sleep(pause)

            # Случайные микродействия (10% вероятность)
            if random.random() < 0.1:
                self.driver.execute_script("window.scrollBy(0, {})".format(
                    random.randint(-50, 50)
                ))
                time.sleep(random.uniform(0.2, 0.5))

        # Финишная прокрутка до конца и возврат
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(random.uniform(1, 1.5))
        self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'})")
        time.sleep(random.uniform(1, 2))
        self.logger.log("Окончание прокрутки страницы категории")

    def emulate_human_behavior(self):
        """Эмуляция поведения человека на странице категории"""
        # Увеличиваем базовую задержку
        time.sleep(random.uniform(2, 6))

        # Основная прокрутка (~30 сек)
        self._smooth_scroll()

        # Дополнительные действия после прокрутки
        actions = ActionChains(self.driver)
        actions.move_to_element(
            self.driver.find_element(By.TAG_NAME, 'body')
        ).pause(1).perform()

        # Финальная пауза перед сохранением
        time.sleep(random.uniform(2, 3))

    def search_category(self):
        """
        Открывает сайт OZON, вводит название категории в поиск и нажимает Enter.
        """
        try:
            self.logger.log(f"Открытие сайта OZON: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Ждем загрузки страницы
            time.sleep(random.uniform(3, 5))
            
            # Находим поле поиска
            self.logger.log(f"Поиск поля ввода для категории: {self.category_name}")
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            
            # Эмулируем человеческое поведение при вводе
            for char in self.category_name:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Пауза перед нажатием Enter
            time.sleep(random.uniform(0.5, 1.0))
            
            # Нажимаем Enter для поиска
            search_box.send_keys(Keys.RETURN)
            self.logger.log(f"Выполнен поиск категории: {self.category_name}")
            
            # Ждем загрузки результатов поиска
            time.sleep(random.uniform(3, 5))
            
            # Проверяем, что мы на странице с результатами
            current_url = self.driver.current_url
            self.logger.log(f"Текущий URL после поиска: {current_url}")
            
            # Проверяем, что мы на странице с результатами (либо search, либо category в URL)
            if "search" in current_url or "category" in current_url:
                self.logger.log(f"Успешно перешли на страницу результатов поиска: {current_url}")
                return True
            else:
                self.logger.log(f"Не удалось перейти на страницу результатов поиска. Текущий URL: {current_url}")
                return False
                
        except TimeoutException:
            self.logger.log("Таймаут при ожидании элемента поиска")
            return False
        except NoSuchElementException as e:
            self.logger.log(f"Элемент поиска не найден: {str(e)}")
            return False
        except Exception as e:
            self.logger.log(f"Ошибка при поиске категории: {str(e)}")
            return False

    def save_html_to_file(self):
        if not self.driver:
            raise RuntimeError("Драйвер не инициализирован")

        try:
            # Сначала выполняем поиск категории
            if not self.search_category():
                self.logger.log("Не удалось выполнить поиск категории")
                return None
                
            self.logger.log(f"Начало загрузки страницы категории: {self.category_name}")
            start_time = time.time()  # Засекаем время начала загрузки

            # Эмуляция поведения
            self.emulate_human_behavior()

            # Сохранение
            # Очищаем название категории от недопустимых символов для имени файла
            safe_category_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in self.category_name)
            os.makedirs(self.download_path, exist_ok=True)
            file_path = os.path.join(self.download_path, f"{safe_category_name}.html")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            end_time = time.time()  # Засекаем время окончания загрузки

            download_time = end_time - start_time
            self.logger.log(f"Время загрузки страницы категории: {download_time:.2f} секунд")
            self.logger.log(f"Страница категории успешно сохранена в {file_path}")
            return file_path

        except Exception as e:
            self.logger.log(f"Критическая ошибка при загрузке категории: {str(e)}")
            return None

    def close_driver(self):
        """
        Закрытие драйвера.
        """
        if self.driver:
            self.logger.log("Закрытие драйвера")
            self.driver.quit() 