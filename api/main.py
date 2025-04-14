import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

# Добавляем корневую директорию проекта в путь Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from api.facade import OzonScraperFacade

# Создаем экземпляр FastAPI
app = FastAPI(
    title="OZON Scraper API",
    description="API для скрапинга данных с OZON",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем экземпляр фасада
scraper = OzonScraperFacade()

# Модели для запросов
class CategoryRequest(BaseModel):
    category_name: str
    links_file: str = "product_links.txt"

class ProductRequest(BaseModel):
    product_url: str

class BatchDownloadRequest(BaseModel):
    links_file: str = "product_links.txt"
    limit: Optional[int] = None

class ConfigUpdateRequest(BaseModel):
    html_file_path: Optional[str] = None

# Эндпоинты
@app.get("/")
async def root():
    """
    Корневой эндпоинт, возвращает информацию о API.
    """
    return {
        "name": "OZON Scraper API",
        "version": "1.0.0",
        "description": "API для скрапинга данных с OZON",
        "endpoints": [
            "/process_category",
            "/process_product",
            "/download_category",
            "/download_product",
            "/extract_links",
            "/batch_download",
            "/update_config_from_html"
        ]
    }

@app.post("/process_category")
async def process_category(request: CategoryRequest):
    """
    Обрабатывает категорию: загружает страницу и извлекает ссылки на продукты.
    
    Args:
        request: Запрос с названием категории и именем файла для сохранения ссылок.
        
    Returns:
        Результат обработки категории.
    """
    result = scraper.process_category(request.category_name, request.links_file)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/process_product")
async def process_product(request: ProductRequest):
    """
    Обрабатывает продукт: загружает страницу и извлекает данные.
    
    Args:
        request: Запрос с URL продукта.
        
    Returns:
        Результат обработки продукта.
    """
    result = scraper.process_product(request.product_url)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/download_category")
async def download_category(category_name: str = Query(..., description="Название категории для поиска на OZON")):
    """
    Загружает страницу категории.
    
    Args:
        category_name: Название категории для поиска на OZON.
        
    Returns:
        Результат загрузки страницы категории.
    """
    result = scraper.download_category_page(category_name)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/download_product")
async def download_product(request: ProductRequest):
    """
    Загружает страницу продукта.
    
    Args:
        request: Запрос с URL продукта.
        
    Returns:
        Результат загрузки страницы продукта.
    """
    result = scraper.download_product_page(request.product_url)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/extract_links")
async def extract_links(html: str = Query(..., description="HTML-код страницы"), 
                       links_file: str = Query("product_links.txt", description="Имя файла для сохранения ссылок")):
    """
    Извлекает ссылки на продукты из HTML.
    
    Args:
        html: HTML-код страницы.
        links_file: Имя файла для сохранения ссылок.
        
    Returns:
        Результат извлечения ссылок.
    """
    result = scraper.extract_product_links(html, links_file)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/batch_download")
async def batch_download(request: BatchDownloadRequest):
    """
    Пакетно скачивает товары из файла с ссылками и сохраняет их в JSON.
    
    Args:
        request: Запрос с путем к файлу с ссылками и лимитом скачивания.
        
    Returns:
        Результат пакетного скачивания.
    """
    result = scraper.batch_download_products(request.links_file, request.limit)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/update_config_from_html")
async def update_config_from_html(request: ConfigUpdateRequest):
    """
    Обновляет конфигурацию на основе HTML-файла или скачивает HTML с зафиксированного URL.
    Аналог скрипта run_update_config.py.
    
    Args:
        request: Запрос с путем к HTML-файлу (опционально).
        
    Returns:
        Результат обновления конфигурации.
    """
    result = scraper.update_config_from_html(request.html_file_path)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result 