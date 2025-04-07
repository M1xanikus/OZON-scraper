import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
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

# Создаем экземпляр фасада
scraper = OzonScraperFacade()

# Модели для запросов
class CategoryRequest(BaseModel):
    category_name: str
    links_file: Optional[str] = "product_links.txt"

class ProductRequest(BaseModel):
    product_url: HttpUrl

class BatchDownloadRequest(BaseModel):
    links_file: str = "product_links.txt"
    limit: Optional[int] = None

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
            "/batch_download"
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
    Обрабатывает продукт: загружает страницу, извлекает данные и обновляет конфигурацию.
    
    Args:
        request: Запрос с URL продукта.
        
    Returns:
        Результат обработки продукта.
    """
    result = scraper.process_product(str(request.product_url))
    
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
    result = scraper.download_product_page(str(request.product_url))
    
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