# Настройка n8n для работы с HR Report API

## ✅ Текущий статус

- ✅ Docker контейнер запущен и работает
- ✅ API доступен на `http://localhost:8000`
- ✅ Health check работает: `{"status":"healthy"}`
- ✅ Данные загружаются автоматически с сервера Yandex Cloud

## 🔗 Подключение n8n к API

### Вариант 1: n8n и API в одной Docker сети (рекомендуется)

Если n8n также запущен через Docker Compose, добавьте в `docker-compose.yml` n8n:

```yaml
services:
  n8n:
    # ... ваши настройки n8n
    networks:
      - default  # Та же сеть, что и hr-report-api
```

**URL для использования в n8n:**
```
http://hr-report-api:8000/generate-report-from-server
```

### Вариант 2: n8n на другом сервере или локально

**URL для использования:**
```
http://your-server-ip:8000/generate-report-from-server
```

Или если n8n на том же компьютере:
```
http://localhost:8000/generate-report-from-server
```

## 📋 Настройка узла HTTP Request в n8n

### Шаг 1: Создайте HTTP Request узел

1. В n8n перейдите в **Workflows** → **New Workflow**
2. Добавьте узел **HTTP Request**

### Шаг 2: Настройте узел

**Основные настройки:**
- **Method**: `GET`
- **URL**: `http://hr-report-api:8000/generate-report-from-server`
  - (или `http://localhost:8000` если n8n локально)
- **Response Format**: `File`

**Дополнительные настройки (Options):**
- **Response** → **Response Format**: `File`
- **Response** → **Full Response**: `false` (по умолчанию)

### Шаг 3: Обработайте результат

После узла HTTP Request добавьте один из узлов:

**Вариант A: Отправка по Email**
- Узел: **Email Send**
- **Attachments**: `={{ $binary.data }}`

**Вариант B: Сохранение на диск**
- Узел: **Save Binary File**
- **File Name**: `HR-отчет-{{ $now.format('YYYY-MM-DD') }}.pdf`
- **Data**: `={{ $binary.data }}`

**Вариант C: Отправка в Slack**
- Узел: **Slack**
- **Operation**: `Upload a File`
- **File**: `={{ $binary.data }}`

**Вариант D: Сохранение в Google Drive**
- Узел: **Google Drive**
- **Operation**: `Upload a File`
- **File**: `={{ $binary.data }}`

## 🕐 Пример: Ежемесячная автоматическая генерация

### Workflow структура:

```
1. Schedule Trigger (Cron)
   └─ Настройка: "0 9 1 * *" (каждое 1-е число месяца в 9:00)
   
2. HTTP Request
   └─ URL: http://hr-report-api:8000/generate-report-from-server
   └─ Response Format: File
   
3. Email Send
   └─ To: hr@company.com
   └─ Subject: HR Отчет за {{ $now.format('MMMM YYYY') }}
   └─ Attachments: {{ $binary.data }}
```

## 🔧 Дополнительные endpoints

### 1. Генерация с указанием URL файла

**URL**: `GET /generate-report-from-url?url=<URL>`

**Пример в n8n:**
- **Method**: `GET`
- **URL**: `http://hr-report-api:8000/generate-report-from-url`
- **Query Parameters**:
  - `url`: `{{ $json.data_file_url }}`
- **Response Format**: `JSON`

**Ответ:**
```json
{
  "status": "success",
  "file_path": "/app/HR-отчет.pdf",
  "file_size_bytes": 55390,
  "download_url": "/generate-report-from-server"
}
```

### 2. Загрузка файла и генерация

**URL**: `POST /generate-report`

**Пример в n8n:**
- **Method**: `POST`
- **URL**: `http://hr-report-api:8000/generate-report`
- **Body Content Type**: `multipart-form-data`
- **Body Parameters**:
  - `file`: Binary data (из предыдущего узла)
- **Response Format**: `File`

## 🐛 Troubleshooting

### Проблема: n8n не может подключиться к API

**Решение 1**: Проверьте, что контейнер запущен
```bash
docker-compose ps
```

**Решение 2**: Проверьте логи API
```bash
docker-compose logs hr-report-api
```

**Решение 3**: Проверьте доступность API
```bash
# В PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health
```

**Решение 4**: Если n8n в Docker, убедитесь, что они в одной сети
- Используйте имя сервиса: `http://hr-report-api:8000`
- Не используйте `localhost` или `127.0.0.1`

### Проблема: Ошибка при генерации отчета

**Решение**: Проверьте логи
```bash
docker-compose logs hr-report-api
# или
cat logs/hr_report.log
```

### Проблема: Файл не создается

**Решение**: Проверьте права доступа к директории
```bash
docker-compose exec hr-report-api ls -la /app
```

## 📊 Мониторинг

### Health Check
```bash
Invoke-WebRequest -Uri http://localhost:8000/health
```

### Просмотр логов в реальном времени
```bash
docker-compose logs -f hr-report-api
```

### Перезапуск сервиса
```bash
docker-compose restart hr-report-api
```

## 🔐 Безопасность (для продакшена)

1. **Ограничьте CORS** в `api.py`:
```python
allow_origins=["https://your-n8n-domain.com"]
```

2. **Добавьте аутентификацию** (API ключи, JWT)

3. **Используйте HTTPS** через reverse proxy (nginx)

4. **Ограничьте доступ** через firewall

## 📝 Примеры workflow

См. файл `n8n-workflow-example.json` для импорта готового workflow в n8n.


