# Запуск HR Report API на сервере через Docker

## Быстрый старт

### 1. Клонирование и подготовка

```bash
git clone <repository-url>
cd hr-analitics-dev
```

### 2. Запуск через docker-compose

```bash
docker-compose up -d
```

Сервис будет доступен по адресу: `http://localhost:8000`

### 3. Проверка работы

```bash
# Health check
curl http://localhost:8000/health

# Генерация отчета
curl http://localhost:8000/generate-report-from-server --output report.pdf
```

## Конфигурация

### Переменные окружения

В `docker-compose.yml` можно настроить:

- `DATA_FILE_URL` - URL файла данных по умолчанию
- `DATA_FILE_PATH` - Путь к локальному файлу (если используется)

Пример:
```yaml
environment:
  - DATA_FILE_URL=https://storage.yandexcloud.net/sds-hr/sds-hr/Реестр_сотрудников.xlsx
```

### Порты

По умолчанию API доступен на порту 8000. Для изменения порта отредактируйте `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"  # Внешний порт:Внутренний порт
```

## Мониторинг

### Просмотр логов

```bash
# Все логи
docker-compose logs -f hr-report-api

# Последние 100 строк
docker-compose logs --tail=100 hr-report-api
```

### Health Check

```bash
curl http://localhost:8000/health
```

Ответ:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00"
}
```

## Остановка и перезапуск

```bash
# Остановка
docker-compose stop

# Перезапуск
docker-compose restart

# Остановка и удаление контейнеров
docker-compose down

# Пересборка и запуск
docker-compose up -d --build
```

## Интеграция с n8n

См. файл `n8n-integration.md` для подробной инструкции по интеграции с n8n.

### Быстрый пример

В n8n создайте HTTP Request узел:
- **Method**: `GET`
- **URL**: `http://hr-report-api:8000/generate-report-from-server`
- **Response Format**: `File`

## Структура директорий

```
.
├── logs/           # Логи приложения
├── reports/        # Сохраненные отчеты (опционально)
├── docker-compose.yml
├── Dockerfile
└── ...
```

## Troubleshooting

### Проблема: Контейнер не запускается

1. Проверьте логи:
```bash
docker-compose logs hr-report-api
```

2. Проверьте, что порт 8000 свободен:
```bash
netstat -an | grep 8000
```

### Проблема: Ошибка при генерации отчета

1. Проверьте доступность URL файла данных
2. Проверьте логи в `./logs/hr_report.log`
3. Убедитесь, что файл имеет правильный формат Excel

### Проблема: n8n не может подключиться

1. Убедитесь, что n8n и API находятся в одной Docker сети
2. Используйте имя сервиса: `http://hr-report-api:8000`
3. Проверьте настройки CORS в `api.py`

## Обновление

```bash
# Остановка
docker-compose down

# Обновление кода
git pull

# Пересборка и запуск
docker-compose up -d --build
```

## Безопасность

Для продакшена:

1. Используйте HTTPS (через reverse proxy, например nginx)
2. Ограничьте CORS в `api.py`
3. Добавьте аутентификацию
4. Используйте секреты для переменных окружения


