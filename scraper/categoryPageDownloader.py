import time
import os
import random
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent, FakeUserAgentError

import sys

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
        self.user_agent = self._get_user_agent()

    def _get_user_agent(self):
        """Генерирует случайный User-Agent."""
        try:
            # Use a specific version if needed, otherwise random might cause issues
            ua = UserAgent(browsers=['chrome'])
            return ua.random
        except FakeUserAgentError:
             self.logger.log("Failed to get random UserAgent, using default.")
             # Fallback user agent
             return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        except Exception as e:
            self.logger.log(f"Error getting UserAgent: {e}, using default.")
            # Fallback user agent
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    def _init_browserless(self):
        # This method is no longer used, but we keep it for reference or future changes
        # It might be useful if direct uc fails in some docker scenarios
        pass

    def _init_local_chrome(self):
        """Инициализация локального Chrome с undetected_chromedriver (теперь используется и в Docker)."""
        # import undetected_chromedriver as uc # Import moved to top

        options = uc.ChromeOptions()
        options.add_argument(f"user-agent={self.user_agent}")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # --- Опции для Docker ---
        # Всегда добавляем эти опции, т.к. код теперь один для local и docker
        options.add_argument('--no-sandbox')
        options.add_argument('--headless=new') # Новый рекомендуемый headless режим
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage') # Важно для Docker
        options.add_argument('--window-size=1920,1080') # Устанавливаем размер окна
        # ------------------------

        # Позволяем uc найти драйвер и браузер автоматически
        # CHROME_BIN и CHROMEDRIVER_PATH из env могут быть использованы uc, если он их найдет
        return uc.Chrome(
            options=options,
            driver_executable_path=os.getenv('CHROMEDRIVER_PATH'), # Можно оставить, uc попробует использовать
            browser_executable_path=os.getenv('CHROME_BIN')       # Можно оставить, uc попробует использовать
        )

    def setup_driver(self):
        """Настройка и инициализация WebDriver с повторными попытками (теперь всегда использует _init_local_chrome)."""
        for attempt in range(1, 4):
            try:
                # Всегда используем undetected_chromedriver
                self.logger.log(f"Attempt {attempt}/3: Initializing WebDriver using undetected_chromedriver...")
                self.driver = self._init_local_chrome()

                self.driver.set_page_load_timeout(60) # Увеличим таймаут загрузки страницы
                self.logger.log("WebDriver успешно инициализирован с undetected_chromedriver")
                return

            except WebDriverException as e:
                self.logger.log(f"Попытка {attempt}/3 не удалась: {str(e)}")
                if self.driver: # Попытка закрыть драйвер, если он частично создался
                    try:
                        self.driver.quit()
                    except: pass
                if attempt == 3:
                    self.logger.log("Не удалось инициализировать WebDriver после 3 попыток")
                    raise RuntimeError("Не удалось инициализировать WebDriver после 3 попыток")
                wait_time = 5 * attempt
                self.logger.log(f"Ожидание {wait_time} секунд перед следующей попыткой...")
                time.sleep(wait_time)  # Увеличиваем задержку с каждой попыткой
            except Exception as e: # Ловим другие возможные ошибки инициализации uc
                 self.logger.log(f"Попытка {attempt}/3 не удалась из-за общей ошибки: {str(e)}")
                 if self.driver:
                    try:
                        self.driver.quit()
                    except: pass
                 if attempt == 3:
                    self.logger.log("Не удалось инициализировать WebDriver после 3 попыток (общая ошибка)")
                    raise RuntimeError(f"Не удалось инициализировать WebDriver после 3 попыток: {e}")
                 wait_time = 5 * attempt
                 self.logger.log(f"Ожидание {wait_time} секунд перед следующей попыткой...")
                 time.sleep(wait_time)

    def close_driver(self):
        """Корректное закрытие WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.log("WebDriver успешно закрыт")
            except Exception as e:
                self.logger.log(f"Ошибка при закрытии WebDriver: {str(e)}")
            finally:
                self.driver = None

    def __enter__(self):
        """Контекстный менеджер для автоматического запуска драйвера."""
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер для автоматического закрытия драйвера."""
        self.close_driver()

    def _smooth_scroll(self):
        self.logger.log("Начало прокрутки страницы категории")
        """Плавная прокрутка с общей продолжительностью ~n секунд"""

        start_time = time.time()
        # Случайная продолжительность скролла
        max_duration = random.uniform(28, 35)
        self.logger.log(f"Smooth scroll duration set to {max_duration:.2f} seconds")
        current_position = 0
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        window_height = self.driver.execute_script("return window.innerHeight")

        # Начальная задержка перед прокруткой
        time.sleep(random.uniform(3, 5)) # Немного уменьшил верхнюю границу

        while time.time() - start_time < max_duration:
            # Рассчитываем оставшееся время
            remaining = max_duration - (time.time() - start_time)
            if remaining <= 0:
                break

            # Прокрутка с переменным шагом
            scroll_step = random.randint(max(200, int(window_height * 0.4)), min(950, int(window_height * 0.9)))
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
            base_pause = remaining / 5 # Динамически уменьшаем паузы
            pause = random.uniform(
                max(0.3, base_pause - 0.2),
                min(2.5, base_pause + 0.5)
            )
            time.sleep(pause)

            # Случайные микро-паузы (имитация запинок)
            if random.random() < 0.15: # 15% шанс
                extra_pause = random.uniform(0.1, 0.4)
                self.logger.log(f"Adding extra micro-pause: {extra_pause:.2f}s")
                time.sleep(extra_pause)

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

    def _perform_random_mouse_move(self):
        """Выполняет случайное движение мыши в пределах окна."""
        try:
            actions = ActionChains(self.driver)
            window_size = self.driver.get_window_size()
            width = window_size.get('width', 1920)
            height = window_size.get('height', 1080)
            # Ограничиваем координаты, чтобы не выходить за пределы (с небольшим отступом)
            random_x = random.randint(50, width - 50)
            random_y = random.randint(50, height - 50)
            self.logger.log(f"Performing random mouse move to ({random_x}, {random_y})")
            # Используем move_by_offset от текущего положения, чтобы имитировать непрямое движение
            # (Начальная точка (0,0) может быть не в углу, поэтому используем безопасный подход)
            # actions.move_by_offset(random_x, random_y).pause(random.uniform(0.3, 0.8)).perform()
            # Более надежный способ: двигаем к элементу body и потом смещаемся
            body = self.driver.find_element(By.TAG_NAME, 'body')
            actions.move_to_element(body).pause(0.1) # Переместились к body
            # Генерируем случайное смещение от левого верхнего угла body (приблизительно)
            actions.move_by_offset(random_x // 2, random_y // 2).pause(random.uniform(0.3, 0.8)).perform()
            # Сбрасываем цепочку действий
            # ActionChains(self.driver).reset_actions()
        except Exception as e:
            self.logger.log(f"Warning: Failed to perform random mouse move: {e}")

    def emulate_human_behavior(self):
        """Эмуляция поведения человека на странице категории"""
        self.logger.log("Starting human behavior emulation...")
        # Увеличиваем базовую задержку
        time.sleep(random.uniform(3, 7))

        # Случайные движения мыши ДО скроллинга
        for _ in range(random.randint(1, 3)): # 1-3 случайных движения
            self._perform_random_mouse_move()
            time.sleep(random.uniform(0.5, 1.5))

        # Основная прокрутка со случайной длительностью
        self._smooth_scroll()

        # Случайные движения мыши ПОСЛЕ скроллинга
        for _ in range(random.randint(0, 2)): # 0-2 случайных движения
             self._perform_random_mouse_move()
             time.sleep(random.uniform(0.4, 1.2))

        # Финальная пауза перед сохранением
        time.sleep(random.uniform(2.5, 4.5))
        self.logger.log("Finished human behavior emulation.")

    def search_category(self):
        """ (Упрощено)
        Открывает сайт OZON, вводит название категории в поиск и нажимает Enter.
        """
        try:
            self.logger.log(f"Opening OZON: {self.base_url}")
            self.driver.get(self.base_url)

            # Ждем загрузки (умеренная пауза)
            time.sleep(random.uniform(5, 8))

            # Попытка принять cookies (если баннер появится)
            try:
                self.logger.log("Attempting to accept cookies...")
                cookie_button_xpath = "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'принять') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'согласен') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]"
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, cookie_button_xpath))
                )
                cookie_button.click()
                self.logger.log("Cookies accepted or button clicked.")
                time.sleep(random.uniform(0.5, 1.5)) # Небольшая пауза после клика
            except TimeoutException:
                self.logger.log("Cookie consent banner not found or timed out.")
            except Exception as e:
                self.logger.log(f"Error interacting with cookie button: {e}")

            # Находим поле поиска
            self.logger.log(f"Searching for category input: {self.category_name}")
            # Используем более универсальный XPath для поля поиска
            search_input_xpath = "//input[@type='text' and (@placeholder='Искать на Ozon' or @name='text')]"
            search_box = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, search_input_xpath))
            )

            time.sleep(random.uniform(0.5, 1.5)) # Пауза перед вводом

            # Эмуляция ввода
            for char in self.category_name:
                search_box.send_keys(char)
                # Увеличен разброс пауз между символами
                time.sleep(random.uniform(0.08, 0.35))

            time.sleep(random.uniform(0.5, 1.0)) # Пауза перед Enter

            search_box.send_keys(Keys.RETURN)
            self.logger.log(f"Performed search for category: {self.category_name}")

            # Ждем загрузки результатов (возможно, нужно дождаться определенного элемента)
            time.sleep(random.uniform(4, 6)) # Пока оставляем простую задержку

            current_url = self.driver.current_url
            self.logger.log(f"Current URL after search: {current_url}")

            if "search" in current_url or "category" in current_url:
                self.logger.log(f"Successfully navigated to results page: {current_url}")
                return True
            else:
                self.logger.log(f"Failed to navigate to results page. Current URL: {current_url}")
                self._save_error_screenshot("navigation_failed_after_search") # Скриншот, если URL неверный
                return False

        except TimeoutException:
            self.logger.log("Timeout while waiting for search element")
            self._save_error_screenshot("timeout_search_element")
            return False
        except NoSuchElementException as e:
            self.logger.log(f"Search element not found: {str(e)}")
            self._save_error_screenshot("element_not_found")
            return False
        except Exception as e:
            # Ловим общую ошибку на этапе поиска, чтобы сделать скриншот
            self.logger.log(f"Error during category search: {str(e)}")
            self._save_error_screenshot("general_search_error")
            return False

    def _save_error_screenshot(self, error_type: str):
        """Сохраняет скриншот в папку data при ошибке."""
        try:
            # Используем относительный путь к data директории
            screenshot_folder = os.path.join("data", "screenshots")
            os.makedirs(screenshot_folder, exist_ok=True)
            # Очищаем имя категории для имени файла
            safe_category_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in self.category_name)
            timestamp = int(time.time())
            filename = f"error_{safe_category_name}_{error_type}_{timestamp}.png"
            filepath = os.path.join(screenshot_folder, filename)
            if self.driver:
                self.driver.save_screenshot(filepath)
                self.logger.log(f"Скриншот ошибки сохранен в: {filepath}")
            else:
                self.logger.log("Не удалось сохранить скриншот: драйвер не инициализирован.")
        except Exception as e:
            self.logger.log(f"Ошибка при сохранении скриншота: {str(e)}")

    def save_html_to_file(self):
        if not self.driver:
             self.logger.log("Драйвер не был инициализирован перед вызовом save_html_to_file")
             raise RuntimeError("Драйвер не инициализирован")

        try:
            # Сначала выполняем поиск категории
            if not self.search_category():
                self.logger.log("Не удалось выполнить поиск категории, HTML не будет сохранен.")
                return None

            self.logger.log(f"Начало загрузки страницы категории: {self.category_name}")
            start_time = time.time() # Засекаем время начала загрузки

            # Эмуляция поведения
            self.emulate_human_behavior()

            # Сохранение
            # Очищаем название категории от недопустимых символов для имени файла
            safe_category_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in self.category_name)
            os.makedirs(self.download_path, exist_ok=True)
            file_path = os.path.join(self.download_path, f"{safe_category_name}.html")

            page_source = self.driver.page_source # Получаем исходный код страницы
            if not page_source:
                self.logger.log("Не удалось получить исходный код страницы (page_source пуст).")
                self._save_error_screenshot("empty_page_source")
                return None

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(page_source)
            end_time = time.time() # Засекаем время окончания загрузки

            download_time = end_time - start_time
            self.logger.log(f"Время загрузки страницы категории: {download_time:.2f} секунд")
            self.logger.log(f"Страница категории успешно сохранена в {file_path}")
            return file_path

        except Exception as e:
            self.logger.log(f"Критическая ошибка при загрузке категории '{self.category_name}': {str(e)}")
            # Добавим сохранение скриншота и здесь, на случай критической ошибки
            self._save_error_screenshot("critical_error_saving_html")
            # Можно добавить выбрасывание исключения, если это критично для потока выполнения
            # raise e
            return None