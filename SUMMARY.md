# HR Analytics - Резюме проекта

## 📝 Краткое описание

**HR Analytics** - автоматизированная система генерации HR-отчетов в формате PDF на основе данных из Excel файлов.

### Ключевые возможности:

✅ **Автоматическая обработка данных**
- Загрузка из Excel (2 листа с увольнениями)
- Фильтрация и валидация
- Удаление дубликатов

✅ **Расчет HR-метрик**
- Численность персонала
- Принято/уволено (YTD и период)
- Текучесть кадров
- Средний стаж и возраст
- Распределение по полу

✅ **Визуализация**
- 2-страничный PDF отчет
- Графики и диаграммы
- Динамика по месяцам
- Статистика по отделам

✅ **API интерфейс**
- FastAPI REST API
- Генерация отчетов по запросу
- Health check endpoint

✅ **CI/CD автоматизация**
- GitLab CI/CD пайплайн
- Автоматическая генерация по расписанию
- Docker контейнеризация

---

## 📊 Исправленная проблема (30.12.2025)

### Что было найдено:

В отчете **НЕ учитывались увольнения склада** из листа "Увольнения Склад и Торги" (100 увольнений в 2025).

### Что исправлено:

✅ Добавлена загрузка второго листа с увольнениями  
✅ Объединение данных из обоих листов  
✅ Удаление дубликатов  
✅ Пересчет всех метрик  

### Результат:

| Метрика | Было ❌ | Стало ✅ | Разница |
|---------|---------|----------|---------|
| Уволено YTD | ~128 | **228** | +100 |
| Уволено за декабрь | ~11 | **19** | +8 |
| Текучесть за год | ~17% | **29.82%** | +12.82% |
| Текучесть за период | ~1.5% | **2.60%** | +1.1% |

---

## 🚀 Быстрый старт

### Локальный запуск:

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Генерация отчета
python main.py

# 3. Результат: HR-отчет.pdf
```

### Docker:

```bash
# API
docker-compose up -d

# Скрипты
docker build -f Dockerfile.script -t hr-script .
docker run hr-script
```

### GitLab CI/CD:

```bash
# 1. Настроить переменные (DATA_FILE_URL)
# 2. Push в main
git push origin main

# 3. Отчет в артефактах через ~5 минут
```

---

## 📚 Документация

### Основная:

- 📖 **[README.md](README.md)** - полная документация проекта
- 🐳 **[README-DOCKER.md](README-DOCKER.md)** - Docker инструкции
- ⚡ **[QUICK-START.md](QUICK-START.md)** - быстрый старт

### GitLab CI/CD:

- 🚀 **[GITLAB-CI-QUICKSTART.md](GITLAB-CI-QUICKSTART.md)** - быстрый старт CI/CD (5 минут)
- 📖 **[GITLAB-CI-SETUP.md](GITLAB-CI-SETUP.md)** - полная документация CI/CD
- 🏗️ **[GITLAB-CI-ARCHITECTURE.md](GITLAB-CI-ARCHITECTURE.md)** - архитектура пайплайна
- 📝 **[.gitlab-ci-examples.sh](.gitlab-ci-examples.sh)** - примеры команд

### Changelog:

- 📝 **[CHANGELOG.md](CHANGELOG.md)** - история изменений

---

## 📁 Структура проекта

```
hr-analitics-dev/
├── main.py                          # Основной скрипт генерации отчета
├── api.py                           # FastAPI REST API
├── requirements.txt                 # Python зависимости
│
├── .gitlab-ci.yml                   # GitLab CI/CD пайплайн
├── .gitlab-ci-examples.sh           # Примеры команд CI/CD
│
├── Dockerfile                       # Docker для API
├── Dockerfile.script                # Docker для скриптов
├── docker-compose.yml               # Docker Compose
│
├── TestCheck/                       # Проверочные скрипты
│   ├── analyze_excel_from_url.py   # Анализ структуры Excel
│   ├── verify_report_numbers.py    # Проверка метрик
│   └── ...
│
├── reports/                         # Сгенерированные отчеты
│   └── HR-отчет-latest.pdf
│
├── logs/                            # Логи приложения
│   └── hr_report.log
│
└── docs/                            # Документация
    ├── README.md
    ├── CHANGELOG.md
    ├── GITLAB-CI-*.md
    └── ...
```

---

## 🔧 Технологии

- **Python 3.11** - основной язык
- **pandas** - обработка данных
- **matplotlib** - визуализация
- **openpyxl** - работа с Excel
- **FastAPI** - REST API
- **Docker** - контейнеризация
- **GitLab CI/CD** - автоматизация

---

## 📊 GitLab CI/CD Pipeline

### Структура:

```
TEST → BUILD → REPORT → DEPLOY
  ├─ Lint          ├─ Docker API    ├─ Generate      ├─ Staging
  ├─ Data Check    └─ Docker Script └─ Custom         └─ Production
  └─ Verify Metrics
```

### Возможности:

✅ Автоматическое тестирование при push  
✅ Сборка Docker образов  
✅ Генерация отчетов по расписанию  
✅ Деплой в staging/production  
✅ Уведомления о статусе  

### Время выполнения:

- **TEST**: ~2-3 минуты
- **BUILD**: ~3-5 минут
- **REPORT**: ~1-2 минуты
- **Итого**: ~7-10 минут

---

## 📅 Автоматизация

### Запланированная генерация отчетов:

```yaml
Schedule: 0 9 * * 1-5  # Каждый будний день в 9:00
Target: main
Result: PDF отчет в артефактах (срок хранения: 30 дней)
```

### Ручная генерация:

```
CI/CD → Pipelines → Run pipeline
```

---

## 🌐 API Endpoints

```
GET  /health                  - Health check
GET  /                        - Информация о API
POST /generate-report         - Генерация отчета
     ?data_url=...            - URL Excel файла (опционально)
```

**Пример:**

```bash
curl -X POST http://localhost:8000/generate-report \
  -H "Content-Type: application/json" \
  -d '{"data_url": "https://example.com/data.xlsx"}'
```

---

## 📈 Метрики в отчете

### Страница 1: Общие показатели

- Количество сотрудников
- Средний стаж (лет)
- Средний возраст (лет)
- Распределение по полу (М/Ж)
- Динамика за 7 месяцев

### Страница 2: Найм и увольнения

- Принято с начала года
- Уволено с начала года
- Принято за месяц
- Уволено за месяц
- Текучесть за год (%)
- Текучесть за период (%)
- Динамика по отделам
- Динамика текучести

---

## 🔐 Безопасность

- ✅ Protected branches (main)
- ✅ Masked variables для секретов
- ✅ Manual approval для production deploy
- ✅ Private Container Registry
- ✅ SSH keys для деплоя

---

## 🆘 Поддержка

### Проблемы с отчетом:

1. Проверьте логи: `logs/hr_report.log`
2. Запустите проверку: `python TestCheck/verify_report_numbers.py`
3. Проверьте структуру: `python TestCheck/analyze_excel_from_url.py`

### Проблемы с CI/CD:

1. Проверьте синтаксис: `CI/CD → CI Lint`
2. Проверьте переменные: `Settings → CI/CD → Variables`
3. См. [GITLAB-CI-SETUP.md](GITLAB-CI-SETUP.md#troubleshooting)

---

## 📊 Статистика проекта

- **Строк кода**: ~1500 (main.py + api.py)
- **Тестовых скриптов**: 6
- **Документации**: 8 файлов
- **CI/CD jobs**: 10
- **Docker образов**: 2

---

## 🎯 Roadmap

- [ ] Добавить unit тесты
- [ ] Интеграция с n8n
- [ ] Kubernetes деплой
- [ ] Prometheus метрики
- [ ] Grafana дашборды
- [ ] Email уведомления
- [ ] Telegram bot

---

## 👥 Команда

**HR Analytics Team**  
**Дата создания**: Декабрь 2025  
**Последнее обновление**: 30.12.2025

---

## 📜 Лицензия

Internal use only

---

**🚀 Готово к использованию!**

Все компоненты настроены и работают. Начните с [QUICK-START.md](QUICK-START.md) или [GITLAB-CI-QUICKSTART.md](GITLAB-CI-QUICKSTART.md).

