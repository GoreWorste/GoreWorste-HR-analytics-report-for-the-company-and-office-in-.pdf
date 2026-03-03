#!/bin/bash
# Скрипт для запуска count_terms.py через Docker

# Создаем директории если их нет
mkdir -p data
mkdir -p output

# Проверяем наличие файла данных
if [ -z "$1" ]; then
    echo "Использование: ./docker-run.sh <путь_к_файлу.xlsx>"
    echo "Пример: ./docker-run.sh data/dataEmployees.xlsx"
    exit 1
fi

DATA_FILE="$1"

# Проверяем существование файла
if [ ! -f "$DATA_FILE" ]; then
    echo "Ошибка: Файл $DATA_FILE не найден!"
    exit 1
fi

# Копируем файл в директорию data если он не там
if [ "$(dirname "$DATA_FILE")" != "data" ]; then
    cp "$DATA_FILE" data/
    DATA_FILE="data/$(basename "$DATA_FILE")"
fi

# Запускаем через docker-compose
docker-compose run --rm count-terms python TestCheck/count_terms.py "/app/$DATA_FILE"





