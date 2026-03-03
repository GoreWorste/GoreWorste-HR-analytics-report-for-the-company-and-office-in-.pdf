# GitLab CI/CD Setup - HR Analytics

## 📋 Содержание

- [Обзор](#обзор)
- [Архитектура пайплайна](#архитектура-пайплайна)
- [Настройка](#настройка)
- [Переменные окружения](#переменные-окружения)
- [Запуск пайплайна](#запуск-пайплайна)
- [Артефакты](#артефакты)
- [Запланированные задачи](#запланированные-задачи)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Обзор

GitLab CI/CD пайплайн для проекта HR Analytics автоматизирует:

✅ **Тестирование** - проверка кода и данных  
✅ **Сборку Docker образов** - для API и скриптов  
✅ **Генерацию отчетов** - автоматически или по запросу  
✅ **Деплой** - в staging/production окружения  

---

## 🏗️ Архитектура пайплайна

Пайплайн состоит из 4 этапов:

```
┌─────────────────────────────────────────────────────────────┐
│                    GITLAB CI/CD PIPELINE                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   STAGE 1   │───▶│   STAGE 2   │───▶│   STAGE 3   │───▶│   STAGE 4   │
│    TEST     │    │    BUILD    │    │   REPORT    │    │   DEPLOY    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                   │                   │                   │
      ├─ lint:python      ├─ build:docker-api ├─ report:generate ├─ deploy:staging
      ├─ test:data-struct.├─ build:docker-scr.├─ report:generate- ├─ deploy:production
      └─ test:verify-metr.│                   │   custom          └─ notify:success
                           │                   │
                           └───────────────────┘
```

---

## ⚙️ Настройка

### 1. Включение GitLab Container Registry

В настройках проекта GitLab:

```
Settings → General → Visibility → Container Registry → Enable
```

### 2. Настройка GitLab Runner

Убедитесь, что у вас есть активные раннеры:

```
Settings → CI/CD → Runners
```

Рекомендуемые теги для раннеров:
- `docker` - для сборки Docker образов
- `linux` - для выполнения скриптов

### 3. Добавление переменных окружения

Перейдите в: `Settings → CI/CD → Variables`

#### Обязательные переменные:

| Переменная | Тип | Описание | Пример |
|------------|-----|----------|--------|
| `CI_REGISTRY` | Variable | GitLab Container Registry | `registry.gitlab.com` |
| `CI_REGISTRY_USER` | Variable | Пользователь registry | `gitlab-ci-token` |
| `CI_REGISTRY_PASSWORD` | Variable | Пароль registry | `$CI_JOB_TOKEN` (автоматически) |

#### Опциональные переменные:

| Переменная | Тип | Описание | Пример |
|------------|-----|----------|--------|
| `DATA_FILE_URL` | Variable | URL файла с данными | `https://storage.yandexcloud.net/...` |
| `STAGING_SERVER` | Variable | Адрес staging сервера | `staging.example.com` |
| `PRODUCTION_SERVER` | Variable | Адрес production сервера | `hr.example.com` |
| `WEBHOOK_URL` | Variable | URL для уведомлений | `https://hooks.slack.com/...` |
| `CUSTOM_DATA_FILE_URL` | Variable | Кастомный URL данных | (для ручных запусков) |

#### Защищенные переменные:

Для production рекомендуется использовать **Protected** и **Masked** переменные:

```bash
Settings → CI/CD → Variables → Add Variable
├─ Key: PRODUCTION_SERVER
├─ Value: prod.example.com
├─ Type: Variable
├─ Protected: ✓ (только для защищенных веток)
└─ Masked: ✓ (скрыть значение в логах)
```

---

## 🔑 Переменные окружения

### Встроенные переменные GitLab CI:

- `$CI_COMMIT_REF_SLUG` - имя ветки (slug формат)
- `$CI_COMMIT_SHORT_SHA` - короткий SHA коммита
- `$CI_PIPELINE_URL` - URL текущего пайплайна
- `$CI_PROJECT_DIR` - директория проекта
- `$CI_REGISTRY_IMAGE` - путь к Container Registry

### Кастомные переменные проекта:

```yaml
variables:
  DOCKER_IMAGE_NAME: $CI_REGISTRY_IMAGE
  DOCKER_IMAGE_TAG: $CI_COMMIT_REF_SLUG
  PYTHON_VERSION: "3.11"
  REPORT_OUTPUT_DIR: "reports"
```

---

## 🚀 Запуск пайплайна

### Автоматический запуск

Пайплайн запускается автоматически при:

1. **Push в ветку** `main` или `develop`:
   - ✅ Все этапы (test, build, report)
   - ⏸️ Deploy - только вручную

2. **Создание Merge Request**:
   - ✅ Только этап test
   - ❌ Build, Report, Deploy пропускаются

3. **Создание тега**:
   - ✅ Полный пайплайн с production deploy

### Ручной запуск

#### Способ 1: Через GitLab UI

```
CI/CD → Pipelines → Run pipeline
├─ Select branch: main
└─ Run pipeline
```

#### Способ 2: Через API

```bash
curl -X POST \
  -F token=YOUR_TRIGGER_TOKEN \
  -F ref=main \
  https://gitlab.com/api/v4/projects/PROJECT_ID/trigger/pipeline
```

#### Способ 3: Manual Jobs

Некоторые задачи требуют ручного запуска:

- `report:generate-custom` - генерация отчета с кастомными параметрами
- `deploy:staging` - деплой в staging
- `deploy:production` - деплой в production

**Запуск manual job:**

```
CI/CD → Pipelines → [Выбрать пайплайн] → [Нажать ▶️ на нужной задаче]
```

---

## 📦 Артефакты

### Типы артефактов

1. **HR-отчеты (PDF)**
   - Путь: `reports/HR-отчет-{дата}.pdf`
   - Срок хранения: 30 дней
   - Размер: ~50-100 KB

2. **Логи**
   - Путь: `logs/hr_report.log`
   - Срок хранения: 30 дней

3. **Docker образы**
   - Хранятся в GitLab Container Registry
   - Теги: `latest`, `{branch-name}`, `{tag}`

### Скачивание артефактов

#### Через GitLab UI:

```
CI/CD → Pipelines → [Выбрать пайплайн] → Download artifacts
```

#### Через API:

```bash
curl --header "PRIVATE-TOKEN: YOUR_TOKEN" \
  "https://gitlab.com/api/v4/projects/PROJECT_ID/jobs/JOB_ID/artifacts" \
  -o artifacts.zip
```

#### Напрямую (latest):

```bash
https://gitlab.com/PROJECT/PATH/-/jobs/artifacts/main/download?job=report:generate
```

---

## ⏰ Запланированные задачи

### Настройка Schedule

Для автоматической генерации отчетов по расписанию:

1. Перейдите в: `CI/CD → Schedules → New schedule`

2. Настройте параметры:

   ```
   Description: Ежедневная генерация HR-отчета
   Interval pattern: 0 9 * * 1-5
   Cron timezone: (UTC +03:00) Moscow
   Target branch: main
   Variables: (оставить пустым или добавить кастомные)
   Activated: ✓
   ```

3. Сохраните

### Примеры расписаний

| Описание | Cron | Значение |
|----------|------|----------|
| Каждый будний день в 9:00 | `0 9 * * 1-5` | Для ежедневных отчетов |
| Каждый понедельник в 8:00 | `0 8 * * 1` | Для еженедельных отчетов |
| 1-го числа каждого месяца | `0 9 1 * *` | Для ежемесячных отчетов |
| Каждый час (рабочее время) | `0 9-18 * * 1-5` | Для частых обновлений |

### Переменные для Schedule

Вы можете добавить переменные для запланированных запусков:

```yaml
SCHEDULE_TYPE: daily
NOTIFICATION_EMAIL: hr@company.com
```

---

## 🔧 Troubleshooting

### Проблема: Пайплайн не запускается

**Решение:**

1. Проверьте, что `.gitlab-ci.yml` находится в корне репозитория
2. Проверьте синтаксис YAML:
   ```
   CI/CD → CI Lint
   ```
3. Убедитесь, что включен CI/CD:
   ```
   Settings → General → Visibility → CI/CD → Enable
   ```

### Проблема: Docker образ не собирается

**Ошибка:**
```
Cannot connect to the Docker daemon
```

**Решение:**

1. Проверьте наличие раннера с тегом `docker`
2. Убедитесь, что используется `docker:dind` service:
   ```yaml
   services:
     - docker:24-dind
   ```

### Проблема: Отчет не генерируется

**Ошибка:**
```
FileNotFoundError: Файл не найден
```

**Решение:**

1. Проверьте переменную `DATA_FILE_URL`
2. Убедитесь, что URL файла доступен
3. Проверьте логи: `logs/hr_report.log`

### Проблема: Артефакты не сохраняются

**Решение:**

1. Проверьте, что директория `reports/` создается:
   ```yaml
   before_script:
     - mkdir -p reports
   ```
2. Проверьте путь в `artifacts.paths`:
   ```yaml
   artifacts:
     paths:
       - reports/
   ```

### Проблема: Нет прав на Container Registry

**Ошибка:**
```
denied: access forbidden
```

**Решение:**

1. Включите Container Registry:
   ```
   Settings → General → Visibility → Container Registry
   ```
2. Проверьте права доступа:
   ```
   Settings → Members → [Ваш пользователь] → Maintainer/Owner
   ```

### Проблема: Пайплайн зависает

**Решение:**

1. Проверьте таймауты раннеров:
   ```
   Settings → CI/CD → General pipelines → Timeout
   ```
2. Добавьте таймауты для долгих задач:
   ```yaml
   job_name:
     timeout: 30 minutes
   ```

---

## 📊 Мониторинг пайплайнов

### Просмотр статистики

```
CI/CD → Pipelines → Charts
```

Здесь вы можете увидеть:
- Количество успешных/неудачных пайплайнов
- Среднее время выполнения
- Частоту запусков

### Уведомления

Настройте уведомления о статусе пайплайна:

```
Settings → Integrations → [Выбрать сервис]
```

Поддерживаемые сервисы:
- Slack
- Microsoft Teams
- Email
- Webhooks

---

## 🔐 Безопасность

### Рекомендации:

1. ✅ Используйте **Protected branches** для `main`:
   ```
   Settings → Repository → Protected branches
   ```

2. ✅ Используйте **Masked variables** для секретов:
   ```
   Settings → CI/CD → Variables → Masked: ✓
   ```

3. ✅ Ограничьте доступ к раннерам:
   ```
   Settings → CI/CD → Runners → Lock to current projects
   ```

4. ✅ Сканируйте образы на уязвимости:
   ```yaml
   include:
     - template: Security/Container-Scanning.gitlab-ci.yml
   ```

---

## 📚 Дополнительные ресурсы

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [GitLab CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/)
- [GitLab Container Registry](https://docs.gitlab.com/ee/user/packages/container_registry/)
- [Cron Schedule Syntax](https://crontab.guru/)

---

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи пайплайна
2. Используйте CI Lint для проверки синтаксиса
3. Обратитесь к документации GitLab
4. Создайте issue в проекте

---

**Версия документа:** 1.0  
**Дата:** 30.12.2025  
**Автор:** HR Analytics Team

