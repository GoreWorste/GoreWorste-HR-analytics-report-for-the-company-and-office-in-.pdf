# 📚 HR Analytics - Навигация по документации

## 🎯 Быстрый доступ

### ⚡ Хочу начать прямо сейчас:
→ **[GITLAB-CI-QUICKSTART.md](GITLAB-CI-QUICKSTART.md)** - 5 минут до первого отчета

### 📋 Хочу пошаговую инструкцию:
→ **[GITLAB-CI-CHECKLIST.md](GITLAB-CI-CHECKLIST.md)** - Чек-лист настройки

### 📖 Хочу понять как все работает:
→ **[GITLAB-CI.md](GITLAB-CI.md)** - Главная страница CI/CD

### 🆘 У меня проблема:
→ **[GITLAB-CI-SETUP.md#troubleshooting](GITLAB-CI-SETUP.md#troubleshooting)** - Решение проблем

---

## 📂 Структура документации

### 🚀 GitLab CI/CD (новое!)

| Документ | Тип | Для кого | Время |
|----------|-----|----------|-------|
| **[GITLAB-CI.md](GITLAB-CI.md)** | Обзор | Все | 10 мин |
| **[GITLAB-CI-QUICKSTART.md](GITLAB-CI-QUICKSTART.md)** | Quick Start | Начинающие | 5 мин |
| **[GITLAB-CI-CHECKLIST.md](GITLAB-CI-CHECKLIST.md)** | Чек-лист | Администраторы | 10 мин |
| **[GITLAB-CI-SETUP.md](GITLAB-CI-SETUP.md)** | Полная документация | DevOps | 30 мин |
| **[GITLAB-CI-ARCHITECTURE.md](GITLAB-CI-ARCHITECTURE.md)** | Техническая | Архитекторы | 15 мин |
| **[GITLAB-CI-SUMMARY.md](GITLAB-CI-SUMMARY.md)** | Итоги | Менеджеры | 10 мин |
| **[.gitlab-ci-examples.sh](.gitlab-ci-examples.sh)** | Примеры | Разработчики | Справка |

### 📊 Основная документация

| Документ | Описание | Для кого |
|----------|----------|----------|
| **[README.md](README.md)** | Полная документация проекта | Все |
| **[SUMMARY.md](SUMMARY.md)** | Краткое резюме проекта | Новички |
| **[CHANGELOG.md](CHANGELOG.md)** | История изменений | Разработчики |
| **[QUICK-START.md](QUICK-START.md)** | Быстрый старт (локально) | Начинающие |

### 🐳 Docker

| Документ | Описание |
|----------|----------|
| **[README-DOCKER.md](README-DOCKER.md)** | Docker инструкции |
| **[docker-compose.yml](docker-compose.yml)** | Docker Compose конфигурация |
| **[Dockerfile](Dockerfile)** | Docker образ для API |
| **[Dockerfile.script](Dockerfile.script)** | Docker образ для скриптов |

### 🔗 Интеграции

| Документ | Описание |
|----------|----------|
| **[n8n-integration.md](n8n-integration.md)** | Интеграция с n8n |
| **[N8N-SETUP.md](N8N-SETUP.md)** | Настройка n8n |
| **[n8n-workflow-example.json](n8n-workflow-example.json)** | Пример workflow |

---

## 🎓 Сценарии использования

### Сценарий 1: "Я новый разработчик"

```
1. Прочитать: README.md (общее понимание)
   ↓
2. Прочитать: SUMMARY.md (краткий обзор)
   ↓
3. Запустить локально: QUICK-START.md
   ↓
4. Настроить CI/CD: GITLAB-CI-QUICKSTART.md
```

### Сценарий 2: "Мне нужен срочный отчет"

```
1. Локально:
   python main.py
   → HR-отчет.pdf

2. Через CI/CD:
   GitLab → CI/CD → Pipelines → Run pipeline
   → Download artifacts
```

### Сценарий 3: "Настроить автоматизацию"

```
1. Прочитать: GITLAB-CI-CHECKLIST.md
   ↓
2. Настроить переменные (5 мин)
   ↓
3. Настроить Schedule (2 мин)
   ↓
4. Настроить уведомления (3 мин)
   ↓
✅ Готово! Отчеты автоматически каждый день
```

### Сценарий 4: "Проблема с отчетом"

```
1. Проверить логи:
   logs/hr_report.log

2. Запустить проверку:
   python TestCheck/verify_report_numbers.py

3. Если не помогло:
   GITLAB-CI-SETUP.md#troubleshooting
```

### Сценарий 5: "Деплой в production"

```
1. Прочитать: GITLAB-CI-SETUP.md
   ↓
2. Настроить переменные окружения
   ↓
3. Протестировать в staging
   ↓
4. Manual deploy в production
```

---

## 🔍 Поиск по темам

### Тема: Установка и настройка

```
README.md → Установка зависимостей
QUICK-START.md → Локальный запуск
GITLAB-CI-QUICKSTART.md → CI/CD за 5 минут
GITLAB-CI-CHECKLIST.md → Пошаговая настройка
```

### Тема: Docker

```
README-DOCKER.md → Полная документация Docker
docker-compose.yml → Конфигурация
Dockerfile → API образ
Dockerfile.script → Script образ
```

### Тема: CI/CD

```
GITLAB-CI.md → Обзор
GITLAB-CI-SETUP.md → Настройка
GITLAB-CI-ARCHITECTURE.md → Архитектура
.gitlab-ci.yml → Конфигурация
```

### Тема: Интеграции

```
n8n-integration.md → n8n интеграция
N8N-SETUP.md → Настройка n8n
api.py → REST API endpoints
```

### Тема: Troubleshooting

```
GITLAB-CI-SETUP.md#troubleshooting → CI/CD проблемы
logs/hr_report.log → Логи приложения
TestCheck/*.py → Проверочные скрипты
```

---

## 🗂️ Файлы по категориям

### 📝 Конфигурация

```
.gitlab-ci.yml              GitLab CI/CD пайплайн
docker-compose.yml          Docker Compose
requirements.txt            Python зависимости
Dockerfile                  Docker образ (API)
Dockerfile.script          Docker образ (Script)
```

### 📖 Документация

```
README.md                   Основная документация
SUMMARY.md                  Краткое резюме
CHANGELOG.md               История изменений
INDEX.md                   Этот файл (навигация)

QUICK-START.md             Быстрый старт (локально)
README-DOCKER.md           Docker документация

GITLAB-CI.md               CI/CD обзор
GITLAB-CI-QUICKSTART.md    CI/CD быстрый старт
GITLAB-CI-CHECKLIST.md     CI/CD чек-лист
GITLAB-CI-SETUP.md         CI/CD документация
GITLAB-CI-ARCHITECTURE.md  CI/CD архитектура
GITLAB-CI-SUMMARY.md       CI/CD итоги

n8n-integration.md         n8n интеграция
N8N-SETUP.md               n8n настройка
```

### 💻 Код

```
main.py                    Основной скрипт генерации
api.py                     FastAPI REST API
verification_report.py     Проверочный скрипт

TestCheck/
  ├── analyze_excel_from_url.py
  ├── verify_report_numbers.py
  ├── check_terminations.py
  └── ...
```

### 📊 Результаты

```
HR-отчет.pdf              Сгенерированный отчет
reports/                   Директория отчетов
logs/                      Логи приложения
```

### 📜 Скрипты

```
.gitlab-ci-examples.sh     Примеры команд CI/CD
docker-run.sh              Запуск Docker (Linux)
docker-run.bat             Запуск Docker (Windows)
```

---

## 🎯 Чек-листы

### ✅ Я хочу запустить проект локально

- [ ] Установить Python 3.11+
- [ ] `pip install -r requirements.txt`
- [ ] `python main.py`
- [ ] Открыть `HR-отчет.pdf`
- [ ] См. [QUICK-START.md](QUICK-START.md)

### ✅ Я хочу запустить в Docker

- [ ] Установить Docker
- [ ] `docker-compose up -d`
- [ ] Открыть `http://localhost:8000`
- [ ] См. [README-DOCKER.md](README-DOCKER.md)

### ✅ Я хочу настроить CI/CD

- [ ] Создать проект в GitLab
- [ ] Настроить переменную `DATA_FILE_URL`
- [ ] Push `.gitlab-ci.yml`
- [ ] Проверить пайплайн
- [ ] См. [GITLAB-CI-QUICKSTART.md](GITLAB-CI-QUICKSTART.md)

### ✅ Я хочу автоматические отчеты

- [ ] Настроить CI/CD
- [ ] Создать Schedule (cron)
- [ ] Настроить уведомления
- [ ] Проверить работу
- [ ] См. [GITLAB-CI-CHECKLIST.md](GITLAB-CI-CHECKLIST.md)

---

## 🆘 Получить помощь

### Где искать ответы:

1. **Этот файл (INDEX.md)** - навигация
2. **SUMMARY.md** - краткий обзор
3. **README.md** - основная документация
4. **GITLAB-CI-SETUP.md#troubleshooting** - решение проблем

### Типичные вопросы:

**Q: Как сгенерировать отчет?**
```
A: python main.py
   или через GitLab CI/CD → Run pipeline
```

**Q: Где скачать готовый отчет?**
```
A: GitLab → CI/CD → Pipelines → Download artifacts
```

**Q: Как настроить автоматическую генерацию?**
```
A: GitLab → CI/CD → Schedules → New schedule
```

**Q: Не работает CI/CD?**
```
A: GITLAB-CI-SETUP.md#troubleshooting
```

**Q: Неправильные цифры в отчете?**
```
A: python TestCheck/verify_report_numbers.py
   См. CHANGELOG.md (исправление увольнений склада)
```

---

## 📊 Статистика документации

```
Всего документов:     15 файлов
Строк документации:   ~4000 строк
Примеров кода:        50+ примеров
Диаграмм:             10+ диаграмм
Чек-листов:           5 чек-листов
```

---

## 🎓 Рекомендуемый порядок изучения

### Для новичков (30 мин):

```
1. INDEX.md (этот файл)        - 5 мин
2. SUMMARY.md                   - 5 мин
3. GITLAB-CI-QUICKSTART.md     - 10 мин
4. Практика: Запуск пайплайна  - 10 мин
```

### Для разработчиков (1 час):

```
1. README.md                    - 15 мин
2. QUICK-START.md              - 10 мин
3. GITLAB-CI.md                - 15 мин
4. Практика: Изменение кода    - 20 мин
```

### Для DevOps (2 часа):

```
1. GITLAB-CI-SETUP.md          - 30 мин
2. GITLAB-CI-ARCHITECTURE.md   - 20 мин
3. .gitlab-ci-examples.sh      - 10 мин
4. Практика: Настройка всего   - 60 мин
```

---

## ✅ Готово!

**Вы знаете где искать нужную информацию!**

### Быстрые ссылки:

- 🚀 Начать: [GITLAB-CI-QUICKSTART.md](GITLAB-CI-QUICKSTART.md)
- 📋 Настроить: [GITLAB-CI-CHECKLIST.md](GITLAB-CI-CHECKLIST.md)
- 📖 Изучить: [GITLAB-CI-SETUP.md](GITLAB-CI-SETUP.md)
- 🆘 Помощь: [GITLAB-CI-SETUP.md#troubleshooting](GITLAB-CI-SETUP.md#troubleshooting)

**Успехов! 🎉**

---

**Документ:** Documentation Index  
**Версия:** 1.0  
**Дата:** 30.12.2025  
**Обновлено:** 30.12.2025

