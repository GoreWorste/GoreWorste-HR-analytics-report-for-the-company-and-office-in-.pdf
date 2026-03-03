# ✅ GitLab CI/CD Setup Checklist

## 📋 Чек-лист настройки (5-10 минут)

Используйте этот чек-лист для быстрой настройки GitLab CI/CD для проекта HR Analytics.

---

## 🎯 Предварительные требования

- [ ] У вас есть проект в GitLab
- [ ] У вас есть права Maintainer или Owner
- [ ] GitLab Runner доступен (shared или specific)

---

## 📝 Шаг 1: Подготовка файлов

- [ ] Файл `.gitlab-ci.yml` находится в корне проекта
- [ ] Файл `Dockerfile` находится в корне проекта
- [ ] Файл `Dockerfile.script` находится в корне проекта
- [ ] Файл `requirements.txt` находится в корне проекта

**Проверка:**
```bash
ls -la | grep -E "\.gitlab-ci\.yml|Dockerfile|requirements\.txt"
```

---

## ⚙️ Шаг 2: Настройка GitLab

### 2.1 Включение CI/CD

- [ ] Settings → General → Visibility → CI/CD → **Enable**
- [ ] Settings → General → Visibility → Container Registry → **Enable**

### 2.2 Настройка переменных

Перейдите: `Settings → CI/CD → Variables`

#### Обязательные переменные:

- [ ] `DATA_FILE_URL`
  - Value: `https://storage.yandexcloud.net/sds-hr/sds-hr/Реестр_сотрудников.xlsx`
  - Type: Variable
  - Protected: ✓
  - Masked: ✗
  - Expand: ✓

#### Опциональные (для деплоя):

- [ ] `STAGING_SERVER`
  - Value: `staging.example.com`
  - Protected: ✗
  - Masked: ✓

- [ ] `PRODUCTION_SERVER`
  - Value: `prod.example.com`
  - Protected: ✓
  - Masked: ✓

- [ ] `WEBHOOK_URL` (для уведомлений)
  - Value: `https://hooks.slack.com/...`
  - Protected: ✗
  - Masked: ✓

### 2.3 Настройка Runner (если нужен specific)

Если используете specific runner:

- [ ] Settings → CI/CD → Runners → Expand
- [ ] Скопируйте registration token
- [ ] Зарегистрируйте runner с тегами: `docker`, `linux`

**Команда регистрации:**
```bash
gitlab-runner register \
  --url https://gitlab.com \
  --registration-token YOUR_TOKEN \
  --executor docker \
  --docker-image docker:24-dind \
  --tag-list "docker,linux"
```

---

## 🚀 Шаг 3: Первый запуск

### 3.1 Проверка синтаксиса

- [ ] CI/CD → CI Lint
- [ ] Вставить содержимое `.gitlab-ci.yml`
- [ ] Нажать **Validate**
- [ ] Убедиться что "Syntax is correct"

### 3.2 Первый коммит

```bash
git add .gitlab-ci.yml
git commit -m "Add GitLab CI/CD pipeline"
git push origin main
```

- [ ] Коммит выполнен
- [ ] Push успешен

### 3.3 Проверка пайплайна

- [ ] CI/CD → Pipelines
- [ ] Новый пайплайн появился в списке
- [ ] Status: Running → Success (ожидание ~7-10 мин)

---

## 📊 Шаг 4: Проверка результатов

### 4.1 Stage: TEST

- [ ] `lint:python` - Completed (может быть Allow failure)
- [ ] `test:data-structure` - Passed
- [ ] `test:verify-metrics` - Passed

**Если failed:** Проверьте логи job → `Show complete raw`

### 4.2 Stage: BUILD

- [ ] `build:docker-api` - Passed
- [ ] `build:docker-script` - Passed
- [ ] Container Registry → 2 новых образа

**Проверка образов:**
```
Settings → Packages & Registries → Container Registry
```

### 4.3 Stage: REPORT

- [ ] `report:generate` - Passed
- [ ] Artifacts доступны для скачивания

**Скачать артефакты:**
```
Pipelines → [Ваш pipeline] → report:generate → Download artifacts
```

**Проверить содержимое:**
- [ ] `reports/HR-отчет-YYYY-MM-DD.pdf` существует
- [ ] `reports/HR-отчет-latest.pdf` существует
- [ ] `logs/hr_report.log` существует

### 4.4 Stage: DEPLOY

- [ ] `deploy:staging` - Manual (не запускать пока)
- [ ] `deploy:production` - Manual (не запускать пока)
- [ ] `notify:success` - Passed (или Allow failure если нет WEBHOOK_URL)

---

## ⏰ Шаг 5: Настройка расписания (опционально)

Для автоматической генерации отчетов:

- [ ] CI/CD → Schedules → New schedule
- [ ] Заполнить форму:
  - Description: `Ежедневная генерация HR-отчета`
  - Interval pattern: `0 9 * * 1-5`
  - Cron timezone: `(UTC +03:00) Moscow`
  - Target branch: `main`
  - Active: ✓
- [ ] Save pipeline schedule

**Тестирование:**
- [ ] Нажать **Play** (▶️) рядом с расписанием
- [ ] Проверить что пайплайн запустился

---

## 🔔 Шаг 6: Уведомления (опционально)

### Slack Integration:

- [ ] Settings → Integrations → Slack notifications
- [ ] Webhook URL: `https://hooks.slack.com/...`
- [ ] Trigger: Pipeline events
- [ ] Branches: `main`
- [ ] Save changes

### Email Notifications:

- [ ] Settings → Notifications
- [ ] Pipeline events: ✓
- [ ] Save changes

---

## 🧪 Шаг 7: Тестирование

### 7.1 Тест: Генерация отчета

- [ ] CI/CD → Pipelines → Run pipeline
- [ ] Select branch: `main`
- [ ] Run pipeline
- [ ] Дождаться завершения (~7-10 мин)
- [ ] Скачать и открыть PDF отчет
- [ ] Проверить что все метрики корректны

### 7.2 Тест: Manual job

- [ ] CI/CD → Pipelines → [Последний pipeline]
- [ ] Найти job `report:generate-custom`
- [ ] Нажать **Play** (▶️)
- [ ] Проверить что job выполнился успешно

### 7.3 Тест: API (если нужен деплой)

Только после настройки `STAGING_SERVER`:

- [ ] Запустить `deploy:staging` manual job
- [ ] Дождаться завершения
- [ ] Проверить health check:
```bash
curl http://$STAGING_SERVER:8000/health
```
- [ ] Ответ: `{"status": "healthy"}`

---

## 📚 Шаг 8: Документация

### Прочитать документацию:

- [ ] [GITLAB-CI-QUICKSTART.md](GITLAB-CI-QUICKSTART.md) - быстрый старт
- [ ] [GITLAB-CI-SETUP.md](GITLAB-CI-SETUP.md) - полная документация
- [ ] [GITLAB-CI-ARCHITECTURE.md](GITLAB-CI-ARCHITECTURE.md) - архитектура

### Сохранить важные ссылки:

- [ ] URL пайплайна: `https://gitlab.com/YOUR_PROJECT/-/pipelines`
- [ ] URL артефактов: `https://gitlab.com/YOUR_PROJECT/-/jobs/artifacts/main/download?job=report:generate`
- [ ] URL Container Registry: `https://gitlab.com/YOUR_PROJECT/container_registry`

---

## ✅ Финальная проверка

### Все работает если:

- ✅ Пайплайн запускается автоматически при push
- ✅ Все тесты проходят успешно
- ✅ Docker образы собираются и публикуются
- ✅ HR-отчет генерируется корректно
- ✅ Артефакты доступны для скачивания
- ✅ (Опционально) Расписание работает
- ✅ (Опционально) Уведомления приходят

---

## 🎉 Поздравляем!

Ваш GitLab CI/CD пайплайн настроен и работает!

### Что дальше?

1. **Настройте расписание** для автоматической генерации отчетов
2. **Настройте уведомления** в Slack/Email
3. **Настройте деплой** в staging/production
4. **Мониторьте** статистику в CI/CD → Charts

---

## 🆘 Troubleshooting

Если что-то не работает:

### Пайплайн не запускается:
```
1. Проверить: Settings → General → Visibility → CI/CD → Enabled
2. Проверить: .gitlab-ci.yml в корне проекта
3. Проверить: CI/CD → CI Lint (синтаксис)
```

### Тесты падают:
```
1. Проверить: переменная DATA_FILE_URL установлена
2. Проверить: URL доступен (curl $DATA_FILE_URL)
3. Проверить: логи job → Show complete raw
```

### Docker образы не собираются:
```
1. Проверить: Container Registry включен
2. Проверить: Runner имеет тег "docker"
3. Проверить: Dockerfile и Dockerfile.script в корне
```

### Отчет не генерируется:
```
1. Проверить: логи в artifacts → logs/hr_report.log
2. Запустить: python TestCheck/verify_report_numbers.py
3. Проверить: структуру Excel файла
```

### Полная документация:
- 📖 [GITLAB-CI-SETUP.md → Troubleshooting](GITLAB-CI-SETUP.md#troubleshooting)

---

## 📝 Changelog

- **30.12.2025** - Первая версия чек-листа
- **30.12.2025** - Добавлен учет увольнений склада в пайплайн

---

**Готово!** Сохраните этот чек-лист для будущих настроек. ✅

