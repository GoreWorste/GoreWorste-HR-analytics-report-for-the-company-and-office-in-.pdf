@echo off
REM Скрипт для запуска count_terms.py через Docker (Windows)

REM Создаем директории если их нет
if not exist data mkdir data
if not exist output mkdir output

REM Проверяем наличие файла данных
if "%~1"=="" (
    echo Использование: docker-run.bat ^<путь_к_файлу.xlsx^>
    echo Пример: docker-run.bat data\dataEmployees.xlsx
    exit /b 1
)

set DATA_FILE=%~1

REM Проверяем существование файла
if not exist "%DATA_FILE%" (
    echo Ошибка: Файл %DATA_FILE% не найден!
    exit /b 1
)

REM Копируем файл в директорию data если он не там
for %%F in ("%DATA_FILE%") do set FILENAME=%%~nxF
if not "%DATA_FILE:~0,4%"=="data" (
    copy "%DATA_FILE%" data\ >nul
    set DATA_FILE=data\%FILENAME%
)

REM Запускаем через docker-compose
docker-compose run --rm count-terms python TestCheck/count_terms.py "/app/%DATA_FILE%"





