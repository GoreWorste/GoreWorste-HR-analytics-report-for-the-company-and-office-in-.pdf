# GitLab CI/CD Quick Start Guide

## ⚡ Быстрый старт за 5 минут

### 1️⃣ Включите GitLab CI/CD

```
Settings → General → Visibility → CI/CD → Enable
```

### 2️⃣ Настройте минимальные переменные

Перейдите в: `Settings → CI/CD → Variables → Add Variable`

**Обязательные:**
```
Ключ: DATA_FILE_URL
Значение: https://storage.yandexcloud.net/sds-hr/sds-hr/Реестр_сотрудников.xlsx
Protected: ✓
Masked: ✗
```

### 3️⃣ Создайте файл `.gitlab-ci.yml`

Файл уже создан в корне проекта! Просто закоммитьте его:

```bash
git add .gitlab-ci.yml
git commit -m "Add GitLab CI/CD pipeline"
git push origin main
```

### 4️⃣ Проверьте пайплайн

Перейдите в: `CI/CD → Pipelines`

Вы должны увидеть запущенный пайплайн! 🎉

---

## 📊 Что делает пайплайн?

### Автоматически при push в `main`:

✅ **TEST** - Проверяет код и данные (2-3 мин)  
✅ **BUILD** - Собирает Docker образы (3-5 мин)  
✅ **REPORT** - Генерирует HR-отчет (1-2 мин)  
⏸️ **DEPLOY** - Готов к деплою (manual)

### Результат:

- 📄 **PDF-отчет** в артефактах
- 🐳 **Docker образы** в Container Registry
- 📝 **Логи** для диагностики

---

## 🔄 Автоматическая генерация отчетов

### Настройте расписание:

1. Перейдите: `CI/CD → Schedules → New schedule`

2. Заполните форму:
   ```
   Description: Ежедневный HR-отчет
   Interval: 0 9 * * 1-5
   Timezone: (UTC +03:00) Moscow
   Target: main
   Active: ✓
   ```

3. Сохраните

**Теперь отчет будет генерироваться каждый будний день в 9:00!** ⏰

---

## 📦 Скачать отчет

### Через GitLab UI:

```
CI/CD → Pipelines → [Выбрать последний] → 
  report:generate → Download artifacts → reports/HR-отчет-latest.pdf
```

### Прямая ссылка:

```
https://gitlab.com/YOUR_PROJECT/-/jobs/artifacts/main/raw/reports/HR-отчет-latest.pdf?job=report:generate
```

---

## 🎯 Типичные сценарии

### Сценарий 1: Срочный отчет

```
CI/CD → Pipelines → Run pipeline → Выбрать branch: main → Run
```

Отчет будет готов через ~5 минут в артефактах.

### Сценарий 2: Отчет с другими данными

```
CI/CD → Pipelines → [Последний пайплайн] → 
  report:generate-custom → Variables:
    CUSTOM_DATA_FILE_URL = https://your-url.com/data.xlsx
  → Play (▶️)
```

### Сценарий 3: Деплой API

```
CI/CD → Pipelines → [Последний пайплайн] → 
  deploy:staging → Play (▶️)
```

API будет доступен по адресу из настроек.

---

## 🚨 Что делать если...

### ❌ Пайплайн не запускается

1. Проверьте наличие `.gitlab-ci.yml` в корне
2. Проверьте синтаксис: `CI/CD → CI Lint`
3. Убедитесь что CI/CD включен (см. шаг 1)

### ❌ Отчет не генерируется

1. Проверьте переменную `DATA_FILE_URL`
2. Убедитесь что URL доступен
3. Посмотрите логи: `report:generate → Show complete raw`

### ❌ Нет артефактов

1. Дождитесь завершения job `report:generate`
2. Проверьте статус: должен быть зеленый ✓
3. Обновите страницу

---

## 📚 Дополнительная документация

- 📖 **[GITLAB-CI-SETUP.md](GITLAB-CI-SETUP.md)** - полная документация
- 📝 **[.gitlab-ci-examples.sh](.gitlab-ci-examples.sh)** - примеры команд
- 🐛 **[TROUBLESHOOTING](GITLAB-CI-SETUP.md#troubleshooting)** - решение проблем

---

## ✅ Готово!

Ваш GitLab CI/CD пайплайн настроен и работает! 🎉

**Что дальше?**

- ⏰ Настройте расписание для автоматической генерации
- 🔔 Добавьте уведомления (Slack/Email)
- 🚀 Настройте деплой в production
- 📊 Следите за статистикой в `CI/CD → Charts`

---

**Нужна помощь?** Смотрите полную документацию в [GITLAB-CI-SETUP.md](GITLAB-CI-SETUP.md)

