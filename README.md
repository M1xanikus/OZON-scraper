# OZON Scraper

Скрапер для сбора данных о товарах с сайта OZON.ru. Проект включает в себя API на FastAPI, пакетное скачивание товаров и автоматическое обновление конфигурации для парсинга.

## Возможности

- Поиск категорий на OZON и получение ссылок на товары
- Пакетное скачивание товаров из файла с ссылками
- Парсинг данных о товарах и сохранение в JSON
- Автоматическое обновление конфигурации для парсинга
- REST API для взаимодействия со скрапером
- Docker-окружение для простого развертывания

## Требования

- Docker
- Docker Compose

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/OZON-SCRAPER.git
cd OZON-SCRAPER
```

### 2. Подготовка директорий и файлов
```bash
mkdir -p htmldata/html_config json_data
touch product_links.txt used_links.txt
```

### 3. Запуск Docker-контейнера
```bash
docker-compose up --build -d
```
Это запустит API-сервер на порту 8000.

### 4. Обновление конфигурации (опционально)
Если вам нужно обновить конфигурацию для парсинга:
```bash
chmod +x update_config.sh
./update_config.sh
```

## Использование API

### Поиск категории и получение ссылок
```bash
curl -X POST "http://localhost:8000/process_category" \
     -H "Content-Type: application/json" \
     -d '{"category_name": "смартфоны"}'
```
Это создаст файл `product_links.txt` с ссылками на товары в категории "смартфоны".

### Пакетное скачивание товаров
```bash
curl -X POST "http://localhost:8000/batch_download" \
     -H "Content-Type: application/json" \
     -d '{"links_file": "product_links.txt", "limit": 10}'
```
Это скачает до 10 товаров из файла `product_links.txt` и сохранит их данные в JSON-файлы в директории `json_data`.

### Скачивание отдельного товара
```bash
curl -X POST "http://localhost:8000/process_product" \
     -H "Content-Type: application/json" \
     -d '{"product_url": "https://www.ozon.ru/product/123456789/"}'
```
Это скачает страницу товара, извлечет данные и обновит конфигурацию.

## Документация API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура проекта

```
OZON-SCRAPER/
├── api/
│   ├── __init__.py
│   ├── facade.py
│   └── main.py
├── htmldata/
│   └── html_config/
│       └── config_html_file.html
├── json_data/
├── scraper/
│   ├── __init__.py
│   ├── batchDownloader.py
│   ├── categoryPageDownloader.py
│   └── pageDownloader.py
├── htmlParser/
│   ├── __init__.py
│   ├── htmlMainPageParser.py
│   ├── htmlProductParser.py
│   └── configUpdater/
│       ├── __init__.py
│       ├── htmlConfigUpdater.py
│       ├── config.json
│       └── template.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── run_update_config.py
├── update_config.sh
├── product_links.txt
└── used_links.txt
```

## Процесс обновления конфигурации

1. Скрипт `run_update_config.py` скачивает страницу товара с OZON
2. Затем он сравнивает эту страницу с шаблоном `htmldata/html_config/config_html_file.html`
3. На основе сравнения обновляется файл конфигурации `htmlParser/configUpdater/config.json`
4. Обновленная конфигурация используется для парсинга товаров

## Остановка контейнера

```bash
docker-compose down
```

## Лицензия

MIT 