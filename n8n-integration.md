# Интеграция HR Report API с n8n

## Обзор

HR Report API предоставляет REST API для генерации HR-отчетов в формате PDF. API можно легко интегрировать с n8n для автоматизации генерации отчетов.

## Запуск на сервере через Docker

### 1. Запуск через docker-compose

```bash
docker-compose up -d
```

Сервис будет доступен по адресу: `http://localhost:8000`

### 2. Проверка работы

```bash
# Health check
curl http://localhost:8000/health

# Генерация отчета
curl http://localhost:8000/generate-report-from-server --output report.pdf
```

## API Endpoints

### 1. Health Check
- **URL**: `GET /health`
- **Описание**: Проверка работоспособности сервиса
- **Ответ**: `{"status": "healthy", "timestamp": "..."}`

### 2. Генерация отчета из данных на сервере
- **URL**: `GET /generate-report-from-server`
- **Описание**: Генерирует отчет из данных по URL (из переменной окружения)
- **Ответ**: PDF файл

### 3. Генерация отчета с указанием URL
- **URL**: `GET /generate-report-from-url?url=<URL>`
- **Описание**: Генерирует отчет из данных по указанному URL
- **Параметры**:
  - `url` (опционально): URL Excel-файла
- **Ответ**: JSON с информацией об отчете

### 4. Генерация отчета из загруженного файла
- **URL**: `POST /generate-report`
- **Описание**: Загружает Excel-файл и генерирует отчет
- **Тело запроса**: multipart/form-data с файлом
- **Ответ**: PDF файл

## Интеграция с n8n

### Вариант 1: Простая генерация отчета (HTTP Request)

1. Создайте новый workflow в n8n
2. Добавьте узел **HTTP Request**
3. Настройте узел:
   - **Method**: `GET`
   - **URL**: `http://hr-report-api:8000/generate-report-from-server`
   - **Response Format**: `File`
   - **Options** → **Response** → **Response Format**: `File`

4. Добавьте узел для сохранения файла (например, **Save Binary File** или отправка по email)

### Вариант 2: Генерация с указанием URL (для гибкости)

1. Добавьте узел **HTTP Request**
2. Настройте:
   - **Method**: `GET`
   - **URL**: `http://hr-report-api:8000/generate-report-from-url`
   - **Query Parameters**:
     - `url`: `{{ $json.data_file_url }}` (из предыдущего узла)
   - **Response Format**: `JSON`

3. Получите информацию об отчете в JSON
4. Используйте `download_url` для загрузки PDF

### Вариант 3: Загрузка файла и генерация

1. Добавьте узел для получения файла (например, из Google Drive, S3 и т.д.)
2. Добавьте узел **HTTP Request**:
   - **Method**: `POST`
   - **URL**: `http://hr-report-api:8000/generate-report`
   - **Body Content Type**: `multipart-form-data`
   - **Body Parameters**:
     - `file`: Binary data из предыдущего узла
   - **Response Format**: `File`

### Пример workflow для ежемесячной генерации

```json
{
  "nodes": [
    {
      "name": "Cron",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 9 1 * *"  // Каждое 1-е число месяца в 9:00
            }
          ]
        }
      }
    },
    {
      "name": "Generate Report",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "http://hr-report-api:8000/generate-report-from-server",
        "options": {
          "response": {
            "responseFormat": "file"
          }
        }
      }
    },
    {
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "to": "hr@company.com",
        "subject": "HR Отчет за месяц",
        "attachments": "={{ $binary.data }}"
      }
    }
  ]
}
```

## Переменные окружения

В `docker-compose.yml` можно настроить:

- `DATA_FILE_URL` - URL файла данных по умолчанию
- `DATA_FILE_PATH` - Путь к локальному файлу (если используется)

## Мониторинг и логи

Логи сохраняются в директории `./logs/hr_report.log`

Для просмотра логов:
```bash
docker-compose logs -f hr-report-api
```

## Безопасность

Для продакшена рекомендуется:

1. Ограничить CORS в `api.py`:
```python
allow_origins=["https://your-n8n-domain.com"]
```

2. Добавить аутентификацию (API ключи, JWT токены)

3. Использовать HTTPS

4. Ограничить доступ к API через firewall

## Примеры использования в n8n

### Пример 1: Ежедневная генерация и отправка в Slack

1. **Schedule Trigger** - каждый день в 8:00
2. **HTTP Request** - генерация отчета
3. **Slack** - отправка файла в канал

### Пример 2: Генерация при обновлении данных

1. **Webhook** - получает уведомление об обновлении данных
2. **HTTP Request** - генерация отчета
3. **Google Drive** - сохранение отчета в папку

### Пример 3: Генерация с параметрами

1. **Manual Trigger** - запуск вручную
2. **Set** - установка URL файла данных
3. **HTTP Request** - генерация с указанным URL
4. **IF** - проверка статуса
5. **Email** - отправка результата

## Troubleshooting

### Проблема: API не отвечает
- Проверьте, что контейнер запущен: `docker-compose ps`
- Проверьте логи: `docker-compose logs hr-report-api`
- Проверьте health check: `curl http://localhost:8000/health`

### Проблема: Ошибка генерации отчета
- Проверьте доступность URL файла данных
- Проверьте логи в `./logs/hr_report.log`
- Убедитесь, что файл имеет правильный формат Excel

### Проблема: n8n не может подключиться
- Убедитесь, что n8n и API находятся в одной Docker сети
- Используйте имя сервиса вместо localhost: `http://hr-report-api:8000`
- Проверьте настройки CORS в API


