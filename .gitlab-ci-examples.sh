#!/bin/bash
# Примеры команд для работы с GitLab CI/CD
# HR Analytics Project

# =============================================================================
# НАСТРОЙКА
# =============================================================================

# Установка переменных (замените на свои значения)
export GITLAB_URL="https://gitlab.com"
export GITLAB_TOKEN="your-private-token"
export PROJECT_ID="12345"  # ID вашего проекта
export PROJECT_PATH="username/hr-analitics"

# =============================================================================
# ПРОВЕРКА .gitlab-ci.yml
# =============================================================================

# Проверка синтаксиса локально
echo "Проверка синтаксиса .gitlab-ci.yml..."
docker run --rm -v $(pwd):/builds/project \
  gitlab/gitlab-runner:latest \
  exec shell --builds-dir /builds \
  lint:python

# Проверка через GitLab API
curl --header "Content-Type: application/json" \
     --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
     --data "$(cat .gitlab-ci.yml | jq -Rs .)" \
     "$GITLAB_URL/api/v4/projects/$PROJECT_ID/ci/lint"

# =============================================================================
# ЗАПУСК ПАЙПЛАЙНА
# =============================================================================

# Запуск пайплайна для ветки main
curl -X POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipeline?ref=main"

# Запуск пайплайна с переменными
curl -X POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --form ref=main \
  --form "variables[CUSTOM_DATA_FILE_URL]=https://example.com/data.xlsx" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipeline"

# =============================================================================
# РАБОТА С ПАЙПЛАЙНАМИ
# =============================================================================

# Получить список пайплайнов
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines"

# Получить статус последнего пайплайна
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines/latest"

# Отменить пайплайн
PIPELINE_ID=123
curl -X POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines/$PIPELINE_ID/cancel"

# Перезапустить пайплайн
curl -X POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines/$PIPELINE_ID/retry"

# =============================================================================
# РАБОТА С JOBS
# =============================================================================

# Получить список jobs для пайплайна
PIPELINE_ID=123
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines/$PIPELINE_ID/jobs"

# Запустить manual job
JOB_ID=456
curl -X POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/jobs/$JOB_ID/play"

# Получить логи job
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/jobs/$JOB_ID/trace"

# =============================================================================
# РАБОТА С АРТЕФАКТАМИ
# =============================================================================

# Скачать артефакты последнего успешного job
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/jobs/artifacts/main/download?job=report:generate" \
  -o artifacts.zip

# Скачать артефакты конкретного job
JOB_ID=456
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/jobs/$JOB_ID/artifacts" \
  -o artifacts.zip

# Извлечь артефакты
unzip artifacts.zip
ls -lh reports/

# Скачать конкретный файл из артефактов
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/jobs/artifacts/main/raw/reports/HR-отчет-latest.pdf?job=report:generate" \
  -o HR-отчет.pdf

# =============================================================================
# РАБОТА С CONTAINER REGISTRY
# =============================================================================

# Логин в GitLab Container Registry
echo $GITLAB_TOKEN | docker login registry.gitlab.com -u gitlab-ci-token --password-stdin

# Список образов
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/registry/repositories"

# Pull образа
docker pull registry.gitlab.com/$PROJECT_PATH:latest

# Запуск контейнера из образа
docker run -d \
  -p 8000:8000 \
  -e DATA_FILE_URL="https://storage.yandexcloud.net/..." \
  registry.gitlab.com/$PROJECT_PATH:latest

# =============================================================================
# РАБОТА С ПЕРЕМЕННЫМИ
# =============================================================================

# Получить список переменных
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables"

# Добавить переменную
curl -X POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --form "key=DATA_FILE_URL" \
  --form "value=https://example.com/data.xlsx" \
  --form "protected=false" \
  --form "masked=false" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables"

# Обновить переменную
curl -X PUT \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --form "value=https://new-url.com/data.xlsx" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables/DATA_FILE_URL"

# Удалить переменную
curl -X DELETE \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables/DATA_FILE_URL"

# =============================================================================
# РАБОТА С SCHEDULES
# =============================================================================

# Получить список расписаний
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipeline_schedules"

# Создать новое расписание (ежедневно в 9:00)
curl -X POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --form "description=Ежедневная генерация отчета" \
  --form "ref=main" \
  --form "cron=0 9 * * 1-5" \
  --form "cron_timezone=Europe/Moscow" \
  --form "active=true" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipeline_schedules"

# Запустить расписание вручную
SCHEDULE_ID=789
curl -X POST \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipeline_schedules/$SCHEDULE_ID/play"

# =============================================================================
# ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ CI/CD
# =============================================================================

# Установка gitlab-runner локально (Linux)
curl -LJO "https://gitlab-runner-downloads.s3.amazonaws.com/latest/deb/gitlab-runner_amd64.deb"
sudo dpkg -i gitlab-runner_amd64.deb

# Запуск job локально
gitlab-runner exec docker test:verify-metrics

# Запуск с переменными
gitlab-runner exec docker report:generate \
  --env DATA_FILE_URL="https://example.com/data.xlsx"

# =============================================================================
# МОНИТОРИНГ
# =============================================================================

# Получить статистику пайплайнов за последний месяц
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines?per_page=100&updated_after=$(date -d '1 month ago' +%Y-%m-%d)" \
  | jq '[.[] | {id, status, ref, created_at}]'

# Подсчет успешных/неудачных пайплайнов
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines?per_page=100" \
  | jq '[.[] | .status] | group_by(.) | map({status: .[0], count: length})'

# Средняя длительность пайплайна
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines?per_page=50" \
  | jq '[.[] | .duration] | add / length'

# =============================================================================
# WEBHOOK ДЛЯ УВЕДОМЛЕНИЙ (Slack)
# =============================================================================

# Пример отправки уведомления в Slack
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
curl -X POST \
  -H 'Content-type: application/json' \
  --data '{
    "text": "✅ HR Analytics Pipeline завершен успешно!",
    "attachments": [{
      "color": "good",
      "fields": [
        {"title": "Pipeline", "value": "'"$GITLAB_URL/$PROJECT_PATH/-/pipelines/$PIPELINE_ID"'", "short": false},
        {"title": "Branch", "value": "main", "short": true},
        {"title": "Status", "value": "Success", "short": true}
      ]
    }]
  }' \
  $SLACK_WEBHOOK

# =============================================================================
# ОЧИСТКА
# =============================================================================

# Удаление старых артефактов (через API недоступно, только через UI)
echo "Удаление старых артефактов доступно только через GitLab UI:"
echo "$GITLAB_URL/$PROJECT_PATH/-/settings/ci_cd#js-artifacts-settings"

# Удаление старых образов из Container Registry
REPOSITORY_ID=123
curl -X DELETE \
  --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "$GITLAB_URL/api/v4/projects/$PROJECT_ID/registry/repositories/$REPOSITORY_ID/tags/old-tag"

# =============================================================================
# ПРИМЕРЫ ДЛЯ АВТОМАТИЗАЦИИ
# =============================================================================

# Скрипт для автоматической генерации отчета и отправки по email
generate_and_send_report() {
  echo "Запуск генерации отчета..."
  
  # Запуск пайплайна
  RESPONSE=$(curl -s -X POST \
    --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipeline?ref=main")
  
  PIPELINE_ID=$(echo $RESPONSE | jq -r '.id')
  echo "Пайплайн запущен: $PIPELINE_ID"
  
  # Ожидание завершения
  while true; do
    STATUS=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
      "$GITLAB_URL/api/v4/projects/$PROJECT_ID/pipelines/$PIPELINE_ID" \
      | jq -r '.status')
    
    echo "Статус: $STATUS"
    
    if [ "$STATUS" = "success" ]; then
      echo "Пайплайн завершен успешно!"
      break
    elif [ "$STATUS" = "failed" ]; then
      echo "Пайплайн завершен с ошибкой!"
      exit 1
    fi
    
    sleep 30
  done
  
  # Скачивание отчета
  echo "Скачивание отчета..."
  curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/api/v4/projects/$PROJECT_ID/jobs/artifacts/main/raw/reports/HR-отчет-latest.pdf?job=report:generate" \
    -o HR-отчет-$(date +%Y-%m-%d).pdf
  
  # Отправка по email (требует настройки mail)
  # echo "Отчет во вложении" | mail -s "HR-отчет $(date +%Y-%m-%d)" \
  #   -A HR-отчет-$(date +%Y-%m-%d).pdf \
  #   hr@company.com
  
  echo "Готово!"
}

# Раскомментируйте для запуска:
# generate_and_send_report

# =============================================================================
# ЗАМЕТКИ
# =============================================================================

# 1. Замените переменные в начале файла на ваши значения
# 2. Получить GITLAB_TOKEN: Settings → Access Tokens → Create token (scopes: api)
# 3. Получить PROJECT_ID: Settings → General → Project ID
# 4. Для работы с API требуется установленный jq: apt-get install jq
# 5. Документация API: https://docs.gitlab.com/ee/api/

echo "✅ Примеры команд загружены. Настройте переменные и используйте нужные команды."

