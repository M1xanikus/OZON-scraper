#!/bin/bash

# Запуск обновления конфигурации
docker-compose exec ozon-scraper python run_update_config.py

echo "Конфигурация обновлена." 