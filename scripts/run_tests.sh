#!/bin/bash

# Скрипт для запуска тестов в Docker

set -e

echo " Starting tests in Docker..."

# Останавливаем предыдущие контейнеры если есть
docker-compose -f docker-compose.test.yml down

# Запускаем тесты
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Копируем отчеты покрытия на хост
docker-compose -f docker-compose.test.yml run test-runner sh -c "cp -r htmlcov /app/reports/ 2>/dev/null || true"

echo " Tests completed!"
echo " Coverage report available in ./reports/htmlcov/index.html"