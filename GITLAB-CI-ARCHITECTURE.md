# GitLab CI/CD Architecture - HR Analytics

## 🏗️ Архитектура пайплайна

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          GITLAB CI/CD PIPELINE                           │
│                           HR Analytics Project                           │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   STAGE 1    │────▶│   STAGE 2    │────▶│   STAGE 3    │────▶│   STAGE 4    │
│     TEST     │     │    BUILD     │     │    REPORT    │     │    DEPLOY    │
│   (3 jobs)   │     │   (2 jobs)   │     │   (2 jobs)   │     │   (3 jobs)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
      │                     │                     │                     │
      │                     │                     │                     │
      ▼                     ▼                     ▼                     ▼

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ lint:python  │     │build:docker- │     │report:       │     │deploy:       │
│              │     │    api       │     │  generate    │     │  staging     │
│ Проверка     │     │              │     │              │     │              │
│ синтаксиса   │     │ Сборка API   │     │ Генерация    │     │ Деплой в     │
│ Python кода  │     │ образа для   │     │ HR-отчета    │     │ тестовое     │
│              │     │ FastAPI      │     │ в PDF        │     │ окружение    │
│ ~1-2 мин     │     │              │     │              │     │              │
│ Allow fail   │     │ ~3-5 мин     │     │ ~1-2 мин     │     │ Manual       │
└──────────────┘     │              │     │              │     └──────────────┘
                     │ Only: main,  │     │ Artifacts:   │
┌──────────────┐     │ develop,tags │     │ - PDF отчет  │     ┌──────────────┐
│test:data-    │     │              │     │ - Логи       │     │deploy:       │
│  structure   │     └──────────────┘     │              │     │  production  │
│              │                           │ Only: main,  │     │              │
│ Проверка     │     ┌──────────────┐     │ schedules,   │     │ Деплой в     │
│ структуры    │     │build:docker- │     │ web          │     │ продакшн     │
│ Excel файла  │     │    script    │     │              │     │              │
│              │     │              │     └──────────────┘     │ Only: main,  │
│ ~2-3 мин     │     │ Сборка для   │                          │ tags         │
│              │     │ скриптов     │     ┌──────────────┐     │              │
└──────────────┘     │              │     │report:       │     │ Manual       │
                     │ ~2-4 мин     │     │generate-     │     └──────────────┘
┌──────────────┐     │              │     │  custom      │
│test:verify-  │     │ Only: main,  │     │              │     ┌──────────────┐
│  metrics     │     │ develop      │     │ С кастомными │     │notify:       │
│              │     │              │     │ параметрами  │     │  success     │
│ Проверка     │     └──────────────┘     │              │     │              │
│ корректности │                           │ ~1-2 мин     │     │ Отправка     │
│ метрик       │                           │              │     │ уведомлений  │
│              │                           │ Manual       │     │              │
│ ~2-3 мин     │                           └──────────────┘     │ On success   │
└──────────────┘                                                └──────────────┘
```

---

## 📊 Детальная схема Stage: TEST

```
┌─────────────────────────────────────────────────────────────────┐
│                        STAGE: TEST                               │
│                    Проверка и валидация                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: lint:python                                                 │
├──────────────────────────────────────────────────────────────────┤
│ Image: python:3.11-slim                                          │
│ Trigger: merge_requests, main, develop                           │
│ Allow failure: true                                              │
├──────────────────────────────────────────────────────────────────┤
│ Steps:                                                           │
│   1. Install flake8, pylint                                      │
│   2. Run: flake8 main.py api.py --max-line-length=120          │
│   3. Check code style                                            │
├──────────────────────────────────────────────────────────────────┤
│ Output: Linting results (может иметь warnings)                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: test:data-structure                                         │
├──────────────────────────────────────────────────────────────────┤
│ Image: python:3.11-slim                                          │
│ Trigger: merge_requests, main, develop                           │
├──────────────────────────────────────────────────────────────────┤
│ Steps:                                                           │
│   1. Install system dependencies (fonts)                         │
│   2. Install Python requirements                                 │
│   3. Run: python TestCheck/analyze_excel_from_url.py            │
│   4. Verify Excel structure                                      │
├──────────────────────────────────────────────────────────────────┤
│ Output:                                                          │
│   ✓ Количество листов: 5                                        │
│   ✓ Лист "Список сотрудников": 741 сотрудников                 │
│   ✓ Лист "Увольнение": 791 записей                             │
│   ✓ Лист "Увольнения Склад и Торги": 192 записей              │
├──────────────────────────────────────────────────────────────────┤
│ Artifacts: test-results.xml (expire: 1 week)                     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: test:verify-metrics                                         │
├──────────────────────────────────────────────────────────────────┤
│ Image: python:3.11-slim                                          │
│ Trigger: merge_requests, main, develop                           │
├──────────────────────────────────────────────────────────────────┤
│ Steps:                                                           │
│   1. Install dependencies                                        │
│   2. Run: python TestCheck/verify_report_numbers.py             │
│   3. Calculate all HR metrics                                    │
│   4. Compare with expected values                                │
├──────────────────────────────────────────────────────────────────┤
│ Output:                                                          │
│   ✓ Численность: 741                                           │
│   ✓ Принято YTD: 181                                           │
│   ✓ Уволено YTD: 228                                           │
│   ✓ Текучесть: 29.82%                                          │
├──────────────────────────────────────────────────────────────────┤
│ Artifacts: Verification logs (expire: 1 week)                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🐳 Детальная схема Stage: BUILD

```
┌─────────────────────────────────────────────────────────────────┐
│                       STAGE: BUILD                               │
│                  Сборка Docker образов                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: build:docker-api                                            │
├──────────────────────────────────────────────────────────────────┤
│ Image: docker:24-dind                                            │
│ Service: docker:24-dind                                          │
│ Trigger: main, develop, tags                                     │
├──────────────────────────────────────────────────────────────────┤
│ Steps:                                                           │
│   1. Login to GitLab Container Registry                          │
│   2. Build: docker build -f Dockerfile .                         │
│   3. Tag: $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG               │
│   4. Tag: $CI_REGISTRY_IMAGE:latest                             │
│   5. Push both tags to registry                                  │
├──────────────────────────────────────────────────────────────────┤
│ Base Image: python:3.11-slim                                     │
│ Exposed Port: 8000                                               │
│ Entry Point: uvicorn api:app --host 0.0.0.0 --port 8000        │
├──────────────────────────────────────────────────────────────────┤
│ Output:                                                          │
│   📦 registry.gitlab.com/user/project:main                      │
│   📦 registry.gitlab.com/user/project:latest                    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: build:docker-script                                         │
├──────────────────────────────────────────────────────────────────┤
│ Image: docker:24-dind                                            │
│ Service: docker:24-dind                                          │
│ Trigger: main, develop                                           │
├──────────────────────────────────────────────────────────────────┤
│ Steps:                                                           │
│   1. Login to GitLab Container Registry                          │
│   2. Build: docker build -f Dockerfile.script .                  │
│   3. Tag: $CI_REGISTRY_IMAGE/script:$CI_COMMIT_REF_SLUG        │
│   4. Tag: $CI_REGISTRY_IMAGE/script:latest                      │
│   5. Push both tags to registry                                  │
├──────────────────────────────────────────────────────────────────┤
│ Base Image: python:3.11-slim                                     │
│ Entry Point: python TestCheck/count_terms.py                     │
├──────────────────────────────────────────────────────────────────┤
│ Output:                                                          │
│   📦 registry.gitlab.com/user/project/script:main               │
│   📦 registry.gitlab.com/user/project/script:latest             │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Детальная схема Stage: REPORT

```
┌─────────────────────────────────────────────────────────────────┐
│                      STAGE: REPORT                               │
│                  Генерация HR-отчетов                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: report:generate                                             │
├──────────────────────────────────────────────────────────────────┤
│ Image: python:3.11-slim                                          │
│ Trigger: main, schedules, web (manual run)                       │
│ When: always                                                     │
├──────────────────────────────────────────────────────────────────┤
│ Environment Variables:                                           │
│   DATA_FILE_URL = https://storage.yandexcloud.net/...          │
├──────────────────────────────────────────────────────────────────┤
│ Steps:                                                           │
│   1. Install system dependencies (fonts)                         │
│   2. Install Python requirements                                 │
│   3. Create reports directory                                    │
│   4. Run: python main.py                                         │
│   5. Copy: HR-отчет.pdf → reports/HR-отчет-{date}.pdf          │
│   6. Copy: HR-отчет.pdf → reports/HR-отчет-latest.pdf          │
├──────────────────────────────────────────────────────────────────┤
│ Process:                                                         │
│   1. Load "Список сотрудников" (741 rows)                       │
│   2. Load "Увольнение" (791 rows)                               │
│   3. Load "Увольнения Склад и Торги" (192 rows)                │
│   4. Merge termination data                                      │
│   5. Calculate metrics (hired, terminated, turnover)             │
│   6. Generate 2-page PDF with charts                             │
├──────────────────────────────────────────────────────────────────┤
│ Artifacts:                                                       │
│   Name: hr-report-{short-sha}                                    │
│   Paths:                                                         │
│     - reports/HR-отчет-2025-12-30.pdf                           │
│     - reports/HR-отчет-latest.pdf                               │
│     - logs/hr_report.log                                         │
│   Expire: 30 days                                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: report:generate-custom                                      │
├──────────────────────────────────────────────────────────────────┤
│ Image: python:3.11-slim                                          │
│ Trigger: main, develop (Manual only)                             │
├──────────────────────────────────────────────────────────────────┤
│ Custom Variables:                                                │
│   CUSTOM_DATA_FILE_URL = [User provided]                         │
├──────────────────────────────────────────────────────────────────┤
│ Steps: Same as report:generate                                   │
├──────────────────────────────────────────────────────────────────┤
│ Artifacts:                                                       │
│   Name: hr-report-custom-{short-sha}                             │
│   Paths: reports/, logs/                                         │
│   Expire: 7 days                                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Детальная схема Stage: DEPLOY

```
┌─────────────────────────────────────────────────────────────────┐
│                      STAGE: DEPLOY                               │
│                 Развертывание приложения                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: deploy:staging                                              │
├──────────────────────────────────────────────────────────────────┤
│ Image: docker:24-dind                                            │
│ Trigger: develop (Manual only)                                   │
├──────────────────────────────────────────────────────────────────┤
│ Environment:                                                     │
│   name: staging                                                  │
│   url: http://${STAGING_SERVER}:8000                            │
├──────────────────────────────────────────────────────────────────┤
│ Steps:                                                           │
│   1. Install openssh-client                                      │
│   2. Connect to staging server                                   │
│   3. Pull Docker image from registry                             │
│   4. Deploy using docker-compose                                 │
├──────────────────────────────────────────────────────────────────┤
│ Deployment Commands:                                             │
│   ssh user@$STAGING_SERVER \                                     │
│     "cd /opt/hr-analytics &&                                     │
│      docker-compose pull &&                                      │
│      docker-compose up -d"                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: deploy:production                                           │
├──────────────────────────────────────────────────────────────────┤
│ Image: docker:24-dind                                            │
│ Trigger: main, tags (Manual only)                                │
├──────────────────────────────────────────────────────────────────┤
│ Environment:                                                     │
│   name: production                                               │
│   url: http://${PRODUCTION_SERVER}:8000                         │
├──────────────────────────────────────────────────────────────────┤
│ Steps: Same as deploy:staging                                    │
├──────────────────────────────────────────────────────────────────┤
│ Security: Requires manual approval                               │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Job: notify:success                                              │
├──────────────────────────────────────────────────────────────────┤
│ Image: curlimages/curl:latest                                    │
│ Trigger: main (On success only)                                  │
│ Allow failure: true                                              │
├──────────────────────────────────────────────────────────────────┤
│ Steps:                                                           │
│   1. Check if WEBHOOK_URL is set                                 │
│   2. Send POST request with pipeline status                      │
├──────────────────────────────────────────────────────────────────┤
│ Payload:                                                         │
│   {                                                              │
│     "text": "✅ Pipeline успешно завершен!",                    │
│     "pipeline": "$CI_PIPELINE_URL",                             │
│     "commit": "$CI_COMMIT_SHORT_SHA"                            │
│   }                                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flow диаграмма: От Push до Deploy

```
    Developer                GitLab                   Runner                  Server
        │                      │                        │                       │
        │  git push            │                        │                       │
        ├─────────────────────▶│                        │                       │
        │                      │                        │                       │
        │                      │  Trigger Pipeline      │                       │
        │                      ├───────────────────────▶│                       │
        │                      │                        │                       │
        │                      │                        │  [STAGE: TEST]        │
        │                      │                        ├─────────────┐         │
        │                      │                        │             │         │
        │                      │                        │  lint       │         │
        │                      │                        │  data-check │         │
        │                      │                        │  verify     │         │
        │                      │                        │◀────────────┘         │
        │                      │                        │                       │
        │                      │  ✓ Tests passed        │                       │
        │                      │◀───────────────────────┤                       │
        │                      │                        │                       │
        │                      │                        │  [STAGE: BUILD]       │
        │                      │                        ├─────────────┐         │
        │                      │                        │             │         │
        │                      │                        │  docker-api │         │
        │                      │                        │  docker-scr │         │
        │                      │                        │◀────────────┘         │
        │                      │                        │                       │
        │                      │                        │  Push to Registry     │
        │                      │                        ├──────────────────────▶│
        │                      │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤                       │
        │                      │                        │                       │
        │                      │                        │  [STAGE: REPORT]      │
        │                      │                        ├─────────────┐         │
        │                      │                        │             │         │
        │                      │                        │  generate   │         │
        │                      │                        │  PDF        │         │
        │                      │                        │◀────────────┘         │
        │                      │                        │                       │
        │                      │  ✓ Report ready        │                       │
        │                      │◀───────────────────────┤                       │
        │                      │                        │                       │
        │  View artifacts      │                        │                       │
        │◀─────────────────────┤                        │                       │
        │                      │                        │                       │
        │  Manual: deploy      │                        │                       │
        ├─────────────────────▶│                        │                       │
        │                      │                        │                       │
        │                      │  [STAGE: DEPLOY]       │                       │
        │                      ├───────────────────────▶│                       │
        │                      │                        │                       │
        │                      │                        │  SSH to server        │
        │                      │                        ├──────────────────────▶│
        │                      │                        │                       │
        │                      │                        │  docker-compose up    │
        │                      │                        ├──────────────────────▶│
        │                      │                        │                       │
        │                      │                        │  ✓ Deployed           │
        │                      │                        │◀──────────────────────┤
        │                      │                        │                       │
        │                      │  ✓ Pipeline complete   │                       │
        │                      │◀───────────────────────┤                       │
        │                      │                        │                       │
        │  Send notification   │                        │                       │
        │◀─────────────────────┤                        │                       │
        │                      │                        │                       │
```

---

## 📅 Scheduled Pipeline Flow

```
    Scheduler            GitLab                Runner               Artifacts
        │                  │                     │                     │
        │  Cron: 0 9 * * 1-5                    │                     │
        ├─────────────────▶│                     │                     │
        │                  │                     │                     │
        │                  │  Trigger Pipeline   │                     │
        │                  ├────────────────────▶│                     │
        │                  │                     │                     │
        │                  │                     │  Run: report:generate
        │                  │                     ├───────────┐         │
        │                  │                     │           │         │
        │                  │                     │  1. Load data       │
        │                  │                     │  2. Calculate       │
        │                  │                     │  3. Generate PDF    │
        │                  │                     │◀──────────┘         │
        │                  │                     │                     │
        │                  │                     │  Save artifacts     │
        │                  │                     ├────────────────────▶│
        │                  │                     │                     │
        │                  │  ✓ Complete         │                     │
        │                  │◀────────────────────┤                     │
        │                  │                     │                     │
        │                  │  Send notification  │                     │
        │                  ├─────────▶ 📧        │                     │
        │                  │                     │                     │
        
        Результат: Автоматический HR-отчет каждый будний день в 9:00
                   Доступен для скачивания в артефактах
```

---

## 🔐 Security & Access Control

```
┌──────────────────────────────────────────────────────────────┐
│                   Security Layers                             │
└──────────────────────────────────────────────────────────────┘

┌────────────────┐
│  Git Push      │  Protected Branches
│  (Developer)   │  ├─ main: Maintainer+
└───────┬────────┘  └─ tags: Maintainer+
        │
        ▼
┌────────────────┐
│  CI/CD Vars    │  Masked & Protected
│                │  ├─ GITLAB_TOKEN
└───────┬────────┘  ├─ PRODUCTION_SERVER
        │           └─ WEBHOOK_URL
        ▼
┌────────────────┐
│  Runner        │  Specific Runner or Shared
│                │  ├─ Tag: docker
└───────┬────────┘  └─ Tag: linux
        │
        ▼
┌────────────────┐
│  Container     │  Private Registry
│  Registry      │  ├─ Login required
└───────┬────────┘  └─ Deploy tokens
        │
        ▼
┌────────────────┐
│  Deploy        │  Manual Approval
│  Production    │  ├─ Maintainer only
└────────────────┘  └─ SSH keys required
```

---

**Документ:** GitLab CI/CD Architecture  
**Версия:** 1.0  
**Дата:** 30.12.2025

