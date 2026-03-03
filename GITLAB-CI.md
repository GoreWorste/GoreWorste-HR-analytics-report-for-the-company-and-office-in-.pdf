# 🚀 GitLab CI/CD для HR Analytics

## Быстрая навигация

📚 **Документация:**

| Документ | Описание | Время чтения |
|----------|----------|--------------|
| **[GITLAB-CI-QUICKSTART.md](GITLAB-CI-QUICKSTART.md)** | Быстрый старт за 5 минут | ⚡ 5 мин |
| **[GITLAB-CI-CHECKLIST.md](GITLAB-CI-CHECKLIST.md)** | Пошаговый чек-лист настройки | ✅ 10 мин |
| **[GITLAB-CI-SETUP.md](GITLAB-CI-SETUP.md)** | Полная документация | 📖 30 мин |
| **[GITLAB-CI-ARCHITECTURE.md](GITLAB-CI-ARCHITECTURE.md)** | Архитектура и диаграммы | 🏗️ 15 мин |
| **[.gitlab-ci-examples.sh](.gitlab-ci-examples.sh)** | Примеры команд | 📝 Справка |

---

## ⚡ Быстрый старт

### 1. Настройте переменные (1 мин)

```
Settings → CI/CD → Variables → Add Variable

Ключ: DATA_FILE_URL
Значение: https://storage.yandexcloud.net/sds-hr/sds-hr/Реестр_сотрудников.xlsx
```

### 2. Push в main (1 мин)

```bash
git add .gitlab-ci.yml
git commit -m "Add CI/CD"
git push origin main
```

### 3. Получите отчет (7-10 мин)

```
CI/CD → Pipelines → [Последний] → 
  report:generate → Download artifacts
```

**Готово!** ✅

---

## 📊 Что включено

### 🧪 Автоматическое тестирование

```yaml
✓ Проверка синтаксиса Python
✓ Валидация структуры Excel данных  
✓ Проверка корректности метрик
```

### 🐳 Docker образы

```yaml
✓ API образ (FastAPI + Uvicorn)
✓ Script образ (для batch обработки)
✓ Автоматическая публикация в Registry
```

### 📄 Генерация отчетов

```yaml
✓ Автоматически при push в main
✓ По расписанию (cron)
✓ По требованию (manual)
✓ С кастомными параметрами
```

### 🚀 Деплой

```yaml
✓ Staging окружение (manual)
✓ Production окружение (manual)
✓ Health check
✓ Rollback capability
```

---

## 🔄 Workflow

```
Developer Push → GitLab → Test → Build → Report → [Manual Deploy]
                            ↓      ↓        ↓           ↓
                           ✓ OK   🐳 Image  📄 PDF    🌐 Server
```

---

## ⏰ Автоматизация

### Запланированная генерация

**Настройка:** `CI/CD → Schedules → New schedule`

```yaml
Description: Ежедневный HR-отчет
Schedule: 0 9 * * 1-5  # Будние дни в 9:00
Branch: main
Active: ✓
```

**Результат:** Отчет генерируется автоматически каждый будний день!

---

## 📦 Артефакты

### Что сохраняется:

```
reports/
  ├── HR-отчет-2025-12-30.pdf  (дата генерации)
  └── HR-отчет-latest.pdf      (последний)

logs/
  └── hr_report.log             (диагностика)
```

### Срок хранения:

- Регулярные отчеты: **30 дней**
- Кастомные отчеты: **7 дней**

### Скачивание:

**Через UI:**
```
Pipelines → [Выбрать] → report:generate → Download
```

**Прямая ссылка:**
```
https://gitlab.com/YOUR_PROJECT/-/jobs/artifacts/main/raw/reports/HR-отчет-latest.pdf?job=report:generate
```

---

## 🎯 Типичные сценарии

### 1. Срочный отчет (5 мин)

```
CI/CD → Pipelines → Run pipeline → Branch: main → Run
↓
Дождаться завершения
↓
Download artifacts → reports/HR-отчет-latest.pdf
```

### 2. Отчет с другими данными (5 мин)

```
CI/CD → Pipelines → [Последний пайплайн]
↓
report:generate-custom → Play (▶️)
↓
Variables:
  CUSTOM_DATA_FILE_URL = https://your-url.com/data.xlsx
↓
Run job → Download artifacts
```

### 3. Деплой API в staging (3 мин)

```
CI/CD → Pipelines → [Последний успешный]
↓
deploy:staging → Play (▶️)
↓
Дождаться завершения
↓
curl http://$STAGING_SERVER:8000/health
```

### 4. Production деплой (требует approval)

```
CI/CD → Pipelines → [Последний из main или tag]
↓
deploy:production → Play (▶️)
↓
Confirm deployment
↓
Проверить: http://$PRODUCTION_SERVER:8000
```

---

## 📈 Мониторинг

### Статистика пайплайнов

```
CI/CD → Charts
```

Доступные метрики:
- Количество успешных/неудачных пайплайнов
- Среднее время выполнения
- Частота запусков
- Pipeline duration trend

### Pipeline Status Badge

Добавьте в README.md:

```markdown
[![pipeline status](https://gitlab.com/YOUR_PROJECT/badges/main/pipeline.svg)](https://gitlab.com/YOUR_PROJECT/-/commits/main)
```

---

## 🔔 Уведомления

### Slack

**Настройка:**
```
Settings → Integrations → Slack notifications
↓
Webhook URL: https://hooks.slack.com/services/...
Trigger: ✓ Pipeline events
Branches: main
```

### Email

**Настройка:**
```
Settings → Notifications
↓
Pipeline events: ✓
Failed pipelines: ✓
```

### Webhook (кастомный)

Добавьте переменную:
```
WEBHOOK_URL = https://your-webhook.com/endpoint
```

Job `notify:success` автоматически отправит POST запрос.

---

## 🔐 Безопасность

### Protected Branches

```
Settings → Repository → Protected branches
↓
Branch: main
Allowed to merge: Maintainers
Allowed to push: Maintainers
```

### Protected Variables

```
Settings → CI/CD → Variables
↓
For production:
  Protected: ✓
  Masked: ✓
```

### Manual Approval

Production deploy **всегда** требует ручного подтверждения.

---

## 🆘 Помощь

### Быстрые ответы:

**Q: Пайплайн не запускается?**
```
A: Проверьте:
   1. CI/CD включен (Settings → General → Visibility)
   2. .gitlab-ci.yml в корне
   3. Синтаксис (CI/CD → CI Lint)
```

**Q: Отчет не генерируется?**
```
A: Проверьте:
   1. Переменная DATA_FILE_URL установлена
   2. URL доступен (curl)
   3. Логи (artifacts → logs/hr_report.log)
```

**Q: Docker образы не собираются?**
```
A: Проверьте:
   1. Container Registry включен
   2. Runner с тегом "docker"
   3. Dockerfile в корне
```

### Полная документация:

📖 **[GITLAB-CI-SETUP.md#troubleshooting](GITLAB-CI-SETUP.md#troubleshooting)**

---

## 📊 Pipeline Stages

### STAGE 1: TEST (2-3 мин)

```
✓ lint:python           - Проверка кода
✓ test:data-structure   - Валидация Excel
✓ test:verify-metrics   - Проверка метрик
```

### STAGE 2: BUILD (3-5 мин)

```
✓ build:docker-api      - Сборка API образа
✓ build:docker-script   - Сборка Script образа
```

### STAGE 3: REPORT (1-2 мин)

```
✓ report:generate       - Генерация отчета (auto)
⏸ report:generate-custom - С параметрами (manual)
```

### STAGE 4: DEPLOY (1-3 мин)

```
⏸ deploy:staging        - Staging деплой (manual)
⏸ deploy:production     - Production деплой (manual)
✓ notify:success        - Уведомления (auto)
```

**Итого:** ~7-10 минут (без manual jobs)

---

## 🔧 Кастомизация

### Изменить расписание

Edit `.gitlab-ci.yml`:

```yaml
variables:
  # Изменить версию Python
  PYTHON_VERSION: "3.12"
  
  # Изменить срок хранения артефактов
  # В секции artifacts:
  expire_in: 60 days  # было 30 days
```

### Добавить новый stage

```yaml
stages:
  - test
  - build
  - report
  - deploy
  - cleanup  # новый

cleanup:old-reports:
  stage: cleanup
  script:
    - echo "Cleaning up..."
  when: manual
```

### Добавить уведомления в Telegram

```yaml
notify:telegram:
  stage: deploy
  image: curlimages/curl:latest
  script:
    - |
      curl -X POST https://api.telegram.org/bot${BOT_TOKEN}/sendMessage \
        -d chat_id=${CHAT_ID} \
        -d text="Pipeline completed!"
  when: on_success
```

---

## 📚 Дополнительные ресурсы

### Официальная документация GitLab:

- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/)
- [Container Registry](https://docs.gitlab.com/ee/user/packages/container_registry/)
- [Pipeline Schedules](https://docs.gitlab.com/ee/ci/pipelines/schedules.html)

### Наша документация:

- 📖 [README.md](README.md) - основная документация проекта
- 📝 [CHANGELOG.md](CHANGELOG.md) - история изменений
- 📊 [SUMMARY.md](SUMMARY.md) - краткое резюме

---

## ✅ Готово!

GitLab CI/CD настроен и готов к использованию! 🎉

### Следующие шаги:

1. ✅ Прочитайте [GITLAB-CI-QUICKSTART.md](GITLAB-CI-QUICKSTART.md)
2. ✅ Следуйте [GITLAB-CI-CHECKLIST.md](GITLAB-CI-CHECKLIST.md)
3. ✅ Настройте расписание для автоматической генерации
4. ✅ Добавьте уведомления (Slack/Email)

---

**Вопросы?** Смотрите [GITLAB-CI-SETUP.md](GITLAB-CI-SETUP.md) или создайте issue в проекте.

**Версия:** 1.0  
**Дата:** 30.12.2025  
**Команда:** HR Analytics

