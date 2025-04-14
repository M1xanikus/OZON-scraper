import time
import random
import os
import sys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from logs.logger import Logger

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

class PageDownloader:
    def __init__(self, url: str, download_path: str, log_file: str = "log.txt"):
        """
        Инициализация класса PageDownloader.

        :param url: URL страницы для загрузки.
        :param download_path: Путь для сохранения HTML файлов.
        :param log_file: Имя файла для логирования.
        """
        self.download_path = download_path
        self.url = url
        self.logger = Logger(log_file)
        self.driver = None
        self.max_retries = 3
        self.retry_delay = 5

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
        Настройка undetected-chromedriver для работы с Chrome.
        """
        try:
            options = uc.ChromeOptions()
            
            # Случайный User-Agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ]
            options.add_argument(f"user-agent={random.choice(user_agents)}")

            # Настройки для работы в Docker
            options.add_argument('--no-sandbox')
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--no-first-run')
            options.add_argument('--no-service-autorun')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--password-store=basic')
            options.add_argument('--no-zygote')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-component-update')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-translate')
            options.add_argument('--metrics-recording-only')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-features=Translate')
            options.add_argument('--disable-features=NetworkService')
            options.add_argument('--disable-features=NetworkServiceInProcess')
            options.add_argument('--disable-features=IsolateOrigins')
            options.add_argument('--disable-features=site-per-process')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1920,1080')
            
            # Дополнительные настройки для обхода обнаружения
            options.add_argument('--disable-infobars')
            options.add_argument('--start-maximized')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-site-isolation-trials')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-save-password-bubble')
            options.add_argument('--disable-single-click-autofill')
            options.add_argument('--disable-autofill-keyboard-accessory-view')
            options.add_argument('--disable-translate')
            options.add_argument('--disable-zero-browsers-open-for-tests')

            # Инициализация драйвера с повторными попытками
            for attempt in range(self.max_retries):
                try:
                    self.driver = uc.Chrome(
                        options=options,
                        version_main=None,  # Автоматическое определение версии
                        use_subprocess=True,
                        driver_executable_path=None  # Позволяем undetected-chromedriver самому найти драйвер
                    )
                    
                    # Установка таймаутов
                    self.driver.set_page_load_timeout(30)
                    self.driver.implicitly_wait(10)
                    
                    # Установка дополнительных свойств для обхода обнаружения
                    self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                        "userAgent": random.choice(user_agents)
                    })
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    
                    # Проверка работоспособности драйвера
                    self.driver.get("about:blank")
                    return
                    
                except Exception as e:
                    self.logger.log(f"Попытка {attempt + 1} инициализации драйвера не удалась: {str(e)}")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                    else:
                        raise Exception(f"Не удалось инициализировать драйвер после {self.max_retries} попыток")

        except Exception as e:
            self.logger.log(f"Критическая ошибка при настройке драйвера: {str(e)}")
            raise

    def _smooth_scroll(self):
        self.logger.log("Начало прокрутки страницы")
        """Плавная прокрутка с общей продолжительностью ~n секунд"""

        start_time = time.time()
        max_duration = 15
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
        self.logger.log("Окончание прокрутки страницы")

    def emulate_human_behavior(self):
        """Обновленный метод с учетом времени"""
        # Увеличиваем базовую задержку
        time.sleep(random.uniform(2, 6))

        # Основная прокрутка (~10 сек)
        self._smooth_scroll()

        # Дополнительные действия после прокрутки
        actions = ActionChains(self.driver)
        actions.move_to_element(
            self.driver.find_element(By.TAG_NAME, 'body')
        ).pause(1).perform()

        # Финальная пауза перед сохранением
        time.sleep(random.uniform(2, 3))

    def extract_product_name_from_url(self):
        """
        Извлечение названия продукта из URL.

        Пример:
        Вход: https://ozon.by/product/krossovki-lexsan-1585614406/?__rr=1&abt_att=1
        Выход: krossovki-lexsan-1585614406

        :return: Название продукта.
        """
        # Извлекаем часть URL после /product/
        product_part = self.url.split("/product/")[-1]

        # Удаляем параметры запроса (всё после ?)
        product_name = product_part.split("?")[0]

        # Удаляем слеши в конце, если они есть
        product_name = product_name.rstrip("/")

        return product_name

    def save_html_to_file(self):
        if not self.driver:
            raise RuntimeError("Драйвер не инициализирован")

        try:
            self.logger.log(f"Начало загрузки страницы: {self.url}")
            start_time = time.time()  # Засекаем время начала загрузки
            self.driver.get(self.url)

            # Эмуляция поведения
            self.emulate_human_behavior()

            # Сохранение
            product_name = self.extract_product_name_from_url()
            os.makedirs(self.download_path, exist_ok=True)
            file_path = os.path.join(self.download_path, f"{product_name}.html")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            end_time = time.time()  # Засекаем время окончания загрузки

            download_time = end_time - start_time
            self.logger.log(f"Время загрузки страницы: {download_time:.2f} секунд")
            self.logger.log(f"Страница успешно сохранена в {file_path}")
            return file_path

        except Exception as e:
            self.logger.log(f"Критическая ошибка: {str(e)}")
            return None

    def close_driver(self):
        """
        Закрытие драйвера.
        """
        if self.driver:
            self.logger.log("Закрытие драйвера")
            self.driver.quit()

