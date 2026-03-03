# Быстрый старт: HR Report API на сервере с n8n

## 🚀 Запуск на сервере

### 1. Запуск Docker контейнера

```bash
docker-compose up -d
```

API будет доступен на: `http://localhost:8000`

### 2. Проверка работы

```bash
curl http://localhost:8000/health
```

## 📋 API Endpoints для n8n

### Вариант 1: Простая генерация (рекомендуется)
```
GET http://hr-report-api:8000/generate-report-from-server
```
Возвращает PDF файл напрямую.

### Вариант 2: С указанием URL
```
GET http://hr-report-api:8000/generate-report-from-url?url=<URL>
```
Возвращает JSON с информацией об отчете.

### Вариант 3: Загрузка файла
```
POST http://hr-report-api:8000/generate-report
Content-Type: multipart/form-data
Body: file=<Excel файл>
```

## 🔗 Интеграция с n8n

### Шаг 1: Создайте HTTP Request узел в n8n

**Настройки узла:**
- **Method**: `GET`
- **URL**: `http://hr-report-api:8000/generate-report-from-server`
- **Response Format**: `File`

### Шаг 2: Обработайте результат

После узла HTTP Request добавьте:
- **Save Binary File** - для сохранения на диск
- **Email Send** - для отправки по email
- **Slack** - для отправки в Slack
- **Google Drive** - для сохранения в облако

### Пример workflow:

```
Schedule Trigger (каждое 1-е число месяца)
    ↓
HTTP Request (генерация отчета)
    ↓
Email Send (отправка HR отделу)
```

## 📝 Примеры использования

### Ежедневная генерация в 9:00
- **Cron**: `0 9 * * *`
- **HTTP Request**: `/generate-report-from-server`
- **Email**: Отправка отчета

### Генерация при обновлении данных
- **Webhook**: Получение уведомления
- **HTTP Request**: `/generate-report-from-url?url={{$json.file_url}}`
- **Google Drive**: Сохранение отчета

## 🔧 Настройка

В `docker-compose.yml` можно изменить:
- URL файла данных: `DATA_FILE_URL`
- Порт: `8000:8000` → `8080:8000`

## 📊 Мониторинг

```bash
# Логи
docker-compose logs -f hr-report-api

# Health check
curl http://localhost:8000/health
```

## ❓ Помощь

- Подробная документация: `n8n-integration.md`
- Docker инструкции: `README-DOCKER.md`
- Пример workflow: `n8n-workflow-example.json`


