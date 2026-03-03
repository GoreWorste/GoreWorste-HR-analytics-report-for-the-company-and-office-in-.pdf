import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
import calendar
import requests
from io import BytesIO
import logging
from logging.handlers import RotatingFileHandler

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "hr_report.log")
    
    # Формат логов
    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настройка root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Очистка существующих handlers
    logger.handlers.clear()
    
    # Handler для файла (ротация при достижении 10MB, хранить 5 файлов)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024, 
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    
    # Handler для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Инициализация логирования
logger = setup_logging()

# URL файла на сервере (по умолчанию)
DATA_FILE_URL = os.getenv("DATA_FILE_URL", "https://storage.yandexcloud.net/sds-hr/sds-hr/%D0%A0%D0%B5%D0%B5%D1%81%D1%82%D1%80_%D1%81%D0%BE%D1%82%D1%80%D1%83%D0%B4%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2.xlsx")

# Путь к Excel-файлу (для локальной загрузки, если указан)
DATA_FILE_PATH = os.getenv("DATA_FILE_PATH", None)

DATA_MODE = "real"  

COLOR_BLUE = "#2E5C8A"
COLOR_BLUE_TITLE = "#0066B3" 
COLOR_RED = "#E74C3C"
COLOR_GREEN = "#27AE60"
COLOR_ORANGE = "#ED7D31"
COLOR_GRAY = "#44546A"
COLOR_GRAY_TEXT = "#2C3E50"
COLOR_GRAY_AXIS = "#7F8C8D"
COLOR_LIGHT_GRAY = "#D0CECE"
COLOR_GRID = "#E5E5E5"
COLOR_BLACK = "#000000"

# Цвета для полосы внизу
COLOR_YELLOW = "#FFC000"
COLOR_PURPLE = "#7030A0"
COLOR_PINK = "#FF00FF"

# Настройка шрифтов
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.unicode_minus"] = False


def parse_date(series: pd.Series) -> pd.Series:
    """Парсинг дат в формате DD.MM.YYYY"""
    return pd.to_datetime(
        series.astype(str).str.strip(), format="%d.%m.%Y", errors="coerce"
    )


def _fill_hire_date_from_other_columns(
    df_term: pd.DataFrame,
    df_raw: pd.DataFrame,
    termination_col: str = "Дата увольнения",
    logger_instance=None,
) -> None:
    """
    Заполняет hire_date в df_term из других столбцов сырых данных, если hire_date пустой.
    Ищет столбцы с названиями, похожими на дату приёма (трудоустройство, приём и т.д.).
    """
    if df_term["hire_date"].notna().all():
        return
    # Выравниваем по индексу (df_term мог быть отфильтрован из df_raw)
    for col in df_raw.columns:
        if col == termination_col:
            continue
        c = str(col).strip().lower()
        if "трудоустройств" not in c and "прием" not in c and "приём" not in c:
            continue
        try:
            raw_vals = df_raw.loc[df_term.index, col] if df_term.index.isin(df_raw.index).all() else df_raw.reindex(df_term.index)[col]
            parsed = pd.to_datetime(raw_vals, errors="coerce")
        except Exception:
            continue
        if parsed.isna().all():
            continue
        # Не используем столбцы с числами, распознанными как 1970-01-01
        years = parsed.dt.year.dropna()
        if len(years) > 0 and (years < 1990).all():
            continue
        mask_missing = df_term["hire_date"].isna()
        mask_before_term = parsed < df_term["termination_date"]
        fill_mask = mask_missing & df_term["termination_date"].notna() & mask_before_term
        if fill_mask.any():
            df_term.loc[fill_mask, "hire_date"] = pd.to_datetime(parsed.loc[fill_mask]).dt.normalize()
            if logger_instance:
                logger_instance.info(
                    f"Дата трудоустройства заполнена из столбца '{col}' для {fill_mask.sum()} записей уволенных"
                )
        break


def load_data_from_url(url: str) -> BytesIO:
    """
    Загружает Excel-файл из URL и возвращает его как BytesIO объект.
    
    Args:
        url: URL файла для загрузки
        
    Returns:
        BytesIO объект с содержимым файла
        
    Raises:
        Exception: Если не удалось загрузить файл
    """
    logger.info(f"Начало загрузки данных из URL: {url}")
    try:
        logger.debug(f"Отправка GET запроса к {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Проверяем успешность запроса
        file_size = len(response.content)
        logger.info(f"Файл успешно загружен, размер: {file_size} байт ({file_size/1024:.2f} KB)")
        logger.debug(f"Content-Type: {response.headers.get('Content-Type', 'неизвестно')}")
        return BytesIO(response.content)
    except requests.exceptions.Timeout as e:
        logger.error(f"Таймаут при загрузке файла: {e}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP ошибка при загрузке файла: {e}, статус код: {response.status_code}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при загрузке файла: {e}", exc_info=True)
        raise


# Русские названия месяцев
MONTH_NAMES_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}


def generate_report(data_file_path: str = None, data_file_url: str = None) -> str:
    """
    Генерирует HR-отчёт в формате PDF.
    
    Args:
        data_file_path: Путь к локальному Excel-файлу с данными. Если не указан, используется загрузка из URL.
        data_file_url: URL Excel-файла с данными. Если не указан, используется DATA_FILE_URL из переменной окружения.
    
    Returns:
        Путь к созданному PDF-файлу.
    """
    logger.info("=" * 80)
    logger.info("НАЧАЛО ГЕНЕРАЦИИ HR-ОТЧЕТА")
    logger.info("=" * 80)
    
    # ========== ЗАГРУЗКА ДАННЫХ ==========
    logger.info("Этап 1: Загрузка данных")
    # Приоритет: 1) переданный локальный путь, 2) локальный путь из переменной окружения, 3) URL
    data_source = None
    
    if data_file_path is not None:
        # Используем переданный локальный путь
        logger.info(f"Использование локального файла (параметр): {data_file_path}")
        if not os.path.exists(data_file_path):
            logger.error(f"Файл не найден: {data_file_path}")
            raise FileNotFoundError(f"Файл не найден: {data_file_path}")
        file_size = os.path.getsize(data_file_path)
        logger.info(f"Размер локального файла: {file_size} байт ({file_size/1024:.2f} KB)")
        data_source = data_file_path
    elif DATA_FILE_PATH is not None:
        # Используем путь из переменной окружения
        logger.info(f"Использование локального файла (переменная окружения): {DATA_FILE_PATH}")
        if not os.path.exists(DATA_FILE_PATH):
            logger.error(f"Файл не найден: {DATA_FILE_PATH}")
            raise FileNotFoundError(f"Файл не найден: {DATA_FILE_PATH}")
        file_size = os.path.getsize(DATA_FILE_PATH)
        logger.info(f"Размер локального файла: {file_size} байт ({file_size/1024:.2f} KB)")
        data_source = DATA_FILE_PATH
    else:
        # Загружаем из URL
        url = data_file_url if data_file_url is not None else DATA_FILE_URL
        logger.info(f"Использование URL для загрузки данных: {url}")
        data_source = load_data_from_url(url)
    
    # Лист "Список сотрудников" (основные сотрудники, заголовки в строке 2)
    logger.info("Загрузка листа 'Список сотрудников'...")
    try:
        df_main_raw = pd.read_excel(data_source, sheet_name="Список сотрудников", header=2)
        logger.info(f"Лист 'Список сотрудников' загружен: {len(df_main_raw)} строк, {len(df_main_raw.columns)} столбцов")
        logger.debug(f"Столбцы листа 'Список сотрудников': {list(df_main_raw.columns)[:10]}")
    except Exception as e:
        logger.warning(f"Не удалось загрузить лист 'Список сотрудников' по имени: {e}")
        logger.info("Попытка загрузки по индексу 0...")
        df_main_raw = pd.read_excel(data_source, sheet_name=0, header=2)
        logger.info(f"Лист загружен по индексу 0: {len(df_main_raw)} строк, {len(df_main_raw.columns)} столбцов")
    
    # Проверка и исключение первой строки, если она служебная
    if len(df_main_raw) > 0:
        first_row_fio_raw = df_main_raw.iloc[0].get("ФИО", "") if "ФИО" in df_main_raw.columns else ""
        first_row_fio = str(first_row_fio_raw).strip().lower() if pd.notna(first_row_fio_raw) else ""
        # Проверяем, является ли первая строка служебной
        service_keywords = ["итого", "всего", "сумма", "total", "summary", "итог", "заголовок", "header"]
        if first_row_fio in service_keywords or first_row_fio == "" or first_row_fio == "nan":
            logger.warning(f"Первая строка содержит служебные данные или пустое ФИО: '{first_row_fio_raw}' - исключаем из расчета")
            df_main_raw = df_main_raw.iloc[1:].reset_index(drop=True)
            logger.info(f"После исключения первой строки: {len(df_main_raw)} строк")
        else:
            logger.debug(f"Первая строка содержит валидные данные: ФИО='{first_row_fio_raw}'")

    # Лист "Увольнение" (уволенные, заголовки в строке 2)
    logger.info("Загрузка листа 'Увольнение'...")
    try:
        df_term_raw = pd.read_excel(data_source, sheet_name="Увольнение", header=2)
        logger.info(f"Лист 'Увольнение' загружен: {len(df_term_raw)} строк, {len(df_term_raw.columns)} столбцов")
        logger.debug(f"Столбцы листа 'Увольнение': {list(df_term_raw.columns)[:10]}")
    except Exception as e:
        logger.warning(f"Не удалось загрузить лист 'Увольнение' по имени: {e}")
        logger.info("Попытка загрузки по индексу 1...")
        df_term_raw = pd.read_excel(data_source, sheet_name=1, header=2)
        logger.info(f"Лист загружен по индексу 1: {len(df_term_raw)} строк, {len(df_term_raw.columns)} столбцов")
    
    # Проверка и исключение первой строки, если она служебная
    if len(df_term_raw) > 0:
        first_row_fio_raw = df_term_raw.iloc[0].get("ФИО", "") if "ФИО" in df_term_raw.columns else ""
        first_row_fio = str(first_row_fio_raw).strip().lower() if pd.notna(first_row_fio_raw) else ""
        # Проверяем, является ли первая строка служебной
        service_keywords = ["итого", "всего", "сумма", "total", "summary", "итог", "заголовок", "header"]
        if first_row_fio in service_keywords or first_row_fio == "" or first_row_fio == "nan":
            logger.warning(f"Первая строка таблицы увольнений содержит служебные данные или пустое ФИО: '{first_row_fio_raw}' - исключаем из расчета")
            df_term_raw = df_term_raw.iloc[1:].reset_index(drop=True)
            logger.info(f"После исключения первой строки таблицы увольнений: {len(df_term_raw)} строк")
        else:
            logger.debug(f"Первая строка таблицы увольнений содержит валидные данные: ФИО='{first_row_fio_raw}'")

    # Лист "Увольнения Склад и Торги" (дополнительные увольнения, заголовки в строке 0)
    logger.info("Загрузка листа 'Увольнения Склад и Торги'...")
    df_term_warehouse_raw = None
    try:
        df_term_warehouse_raw = pd.read_excel(data_source, sheet_name="Увольнения Склад и Торги", header=0)
        logger.info(f"Лист 'Увольнения Склад и Торги' загружен: {len(df_term_warehouse_raw)} строк, {len(df_term_warehouse_raw.columns)} столбцов")
        logger.debug(f"Столбцы листа 'Увольнения Склад и Торги': {list(df_term_warehouse_raw.columns)[:10]}")
    except Exception as e:
        logger.warning(f"Не удалось загрузить лист 'Увольнения Склад и Торги' по имени: {e}")
        logger.info("Попытка загрузки по индексу 2...")
        try:
            df_term_warehouse_raw = pd.read_excel(data_source, sheet_name=2, header=0)
            logger.info(f"Лист загружен по индексу 2: {len(df_term_warehouse_raw)} строк, {len(df_term_warehouse_raw.columns)} столбцов")
        except Exception as e2:
            logger.warning(f"Не удалось загрузить лист по индексу 2: {e2}")
            logger.warning("ВНИМАНИЕ: Лист с увольнениями склада не найден! Увольнения склада не будут учтены в отчете.")
    
    # Проверка и исключение первой строки из df_term_warehouse_raw, если она служебная
    if df_term_warehouse_raw is not None and len(df_term_warehouse_raw) > 0:
        first_row_fio_raw = df_term_warehouse_raw.iloc[0].get("ФИО", "") if "ФИО" in df_term_warehouse_raw.columns else ""
        first_row_fio = str(first_row_fio_raw).strip().lower() if pd.notna(first_row_fio_raw) else ""
        service_keywords = ["итого", "всего", "сумма", "total", "summary", "итог", "заголовок", "header"]
        if first_row_fio in service_keywords or first_row_fio == "" or first_row_fio == "nan":
            logger.warning(f"Первая строка таблицы увольнений склада содержит служебные данные или пустое ФИО: '{first_row_fio_raw}' - исключаем из расчета")
            df_term_warehouse_raw = df_term_warehouse_raw.iloc[1:].reset_index(drop=True)
            logger.info(f"После исключения первой строки таблицы увольнений склада: {len(df_term_warehouse_raw)} строк")
        else:
            logger.debug(f"Первая строка таблицы увольнений склада содержит валидные данные: ФИО='{first_row_fio_raw}'")

    # Диагностика: проверяем названия столбцов
    logger.info("Этап 2: Диагностика структуры данных")
    logger.info("--- Лист 'Список сотрудников' ---")
    logger.info(f"Всего строк: {len(df_main_raw)}, столбцов: {len(df_main_raw.columns)}")
    logger.debug(f"Все столбцы: {list(df_main_raw.columns)}")
    
    required_columns_main = ["Пол", "Дата рождения", "ФИО", "Дата трудоустройства", "ОтделФакт"]
    for col in required_columns_main:
        if col in df_main_raw.columns:
            non_null_count = df_main_raw[col].notna().sum()
            logger.info(f"Столбец '{col}' найден: {non_null_count} заполненных значений из {len(df_main_raw)}")
            if col == "Пол":
                unique_vals = df_main_raw[col].dropna().unique()[:20]
                logger.debug(f"Уникальные значения в столбце 'Пол': {list(unique_vals)}")
        else:
            logger.warning(f"Столбец '{col}' не найден в листе 'Список сотрудников'!")

    logger.info("--- Лист 'Увольнение' ---")
    logger.info(f"Всего строк: {len(df_term_raw)}, столбцов: {len(df_term_raw.columns)}")
    logger.debug(f"Все столбцы: {list(df_term_raw.columns)}")
    
    required_columns_term = ["Дата увольнения", "ФИО", "Дата трудоустройства", "ОтделФакт"]
    for col in required_columns_term:
        if col in df_term_raw.columns:
            non_null_count = df_term_raw[col].notna().sum()
            logger.info(f"Столбец '{col}' найден: {non_null_count} заполненных значений из {len(df_term_raw)}")
        else:
            logger.warning(f"Столбец '{col}' не найден в листе 'Увольнение'!")

    # Период отчёта: дата на момент формирования (данные из таблицы «как есть» на сегодня)
    _today = datetime.now()
    now = datetime(_today.year, _today.month, _today.day)
    TARGET_YEAR = now.year
    current_month_name = MONTH_NAMES_RU.get(now.month, now.strftime("%B"))
    logger.info(f"Период отчета: {current_month_name} {TARGET_YEAR} (на дату {now.strftime('%d.%m.%Y')})")

    # ========== НОРМАЛИЗАЦИЯ ДАННЫХ ==========
    logger.info("Этап 2.1: Нормализация данных")
    df_main = df_main_raw.copy()
    
    # Фильтрация: исключаем строки с пустым или некорректным ФИО
    initial_count = len(df_main)
    df_main = df_main[df_main["ФИО"].notna()].copy()
    df_main = df_main[df_main["ФИО"].astype(str).str.strip() != ""].copy()
    # Исключаем служебные строки
    service_keywords = ["итого", "всего", "сумма", "total", "summary", "итог", "заголовок", "header"]
    df_main = df_main[~df_main["ФИО"].astype(str).str.strip().str.lower().isin(service_keywords)].copy()
    filtered_count = len(df_main)
    if initial_count != filtered_count:
        logger.info(f"Отфильтровано {initial_count - filtered_count} строк с некорректным ФИО. Осталось: {filtered_count} строк")

    # Нормализация пола: строго по первой букве "м" / "ж" из столбца "Пол"
    def normalize_gender(gender_str):
        """Нормализует значение пола к 'м' или 'ж' строго по первой букве"""
        if pd.isna(gender_str):
            return None
        s = str(gender_str).strip().lower()
        if not s:
            return None
        first = s[0]
        if first == 'м':
            return 'м'
        if first == 'ж':
            return 'ж'
        return None

    # Дата трудоустройства — явный парсинг DD.MM.YYYY для единообразия
    if "Дата трудоустройства" in df_main.columns:
        ser_hire = df_main["Дата трудоустройства"].astype(str).str.strip()
        df_main["hire_date"] = parse_date(ser_hire)
        still_na = df_main["hire_date"].isna() & (ser_hire != "") & (ser_hire.str.lower() != "nan")
        if still_na.any():
            df_main.loc[still_na, "hire_date"] = pd.to_datetime(df_main.loc[still_na, "Дата трудоустройства"], errors="coerce")
    else:
        df_main["hire_date"] = pd.to_datetime(df_main_raw.iloc[:, 20], errors="coerce")
    
    df_main["termination_date_hr"] = pd.NaT  # В основной таблице нет дат увольнения
    df_main["birth_date"] = pd.to_datetime(df_main["Дата рождения"], errors="coerce")
    df_main["department"] = df_main["ОтделФакт"]
    df_main["gender_raw"] = df_main["Пол"].apply(normalize_gender)

    df_term = df_term_raw.copy()
    
    # Фильтрация: исключаем строки с пустым или некорректным ФИО
    initial_count_term = len(df_term)
    df_term = df_term[df_term["ФИО"].notna()].copy()
    df_term = df_term[df_term["ФИО"].astype(str).str.strip() != ""].copy()
    # Исключаем служебные строки
    df_term = df_term[~df_term["ФИО"].astype(str).str.strip().str.lower().isin(service_keywords)].copy()
    filtered_count_term = len(df_term)
    if initial_count_term != filtered_count_term:
        logger.info(f"Отфильтровано {initial_count_term - filtered_count_term} строк с некорректным ФИО в таблице увольнений. Осталось: {filtered_count_term} строк")
    
    # Дата трудоустройства в реестре уволенных: нужна, чтобы учитывать «принято с начала года» в т.ч. уже уволенных
    hire_date_col_term = None
    for col_name in ["Дата трудоустройства", "Дата приема", "Дата приёма"]:
        if col_name in df_term.columns:
            hire_date_col_term = col_name
            break
    if hire_date_col_term:
        # Сначала пробуем формат DD.MM.YYYY, затем общий парсинг (Excel может отдавать дату по-разному)
        ser = df_term[hire_date_col_term].astype(str).str.strip()
        df_term["hire_date"] = parse_date(ser)
        still_na = df_term["hire_date"].isna() & (ser != "") & (ser.str.lower() != "nan")
        if still_na.any():
            df_term.loc[still_na, "hire_date"] = pd.to_datetime(df_term.loc[still_na, hire_date_col_term], errors="coerce")
        logger.info(f"Дата трудоустройства в листе 'Увольнение': столбец '{hire_date_col_term}'")
    else:
        try:
            df_term["hire_date"] = pd.to_datetime(df_term_raw.iloc[:, 20], errors="coerce")
            logger.debug("Дата трудоустройства в листе 'Увольнение': по индексу столбца 20")
        except IndexError:
            df_term["hire_date"] = pd.NaT
            logger.warning("В листе 'Увольнение' не найден столбец с датой трудоустройства — принятые и уволенные в том же году могут не попасть в метрику «принято с начала года»")
    # Дата увольнения — явный парсинг DD.MM.YYYY
    if "Дата увольнения" in df_term.columns:
        ser_term = df_term["Дата увольнения"].astype(str).str.strip()
        df_term["termination_date"] = parse_date(ser_term)
        still_na = df_term["termination_date"].isna() & ser_term.ne("").ne(ser_term.isna())
        if still_na.any():
            df_term.loc[still_na, "termination_date"] = pd.to_datetime(df_term.loc[still_na, "Дата увольнения"], errors="coerce")
    else:
        df_term["termination_date"] = pd.to_datetime(df_term_raw.iloc[:, 21], errors="coerce")
    # Попытка заполнить пустые hire_date из других столбцов листа (другое название столбца)
    _fill_hire_date_from_other_columns(df_term, df_term_raw, "Дата увольнения", logger)
    # Дополнительно: если всё ещё есть пустые — пробуем соседние индексы столбцов (18, 19, 21)
    if df_term["hire_date"].isna().any() and df_term["termination_date"].notna().any():
        ncols = len(df_term_raw.columns)
        for idx in [18, 19, 21]:
            if idx >= ncols or idx == 20:
                continue
            try:
                col = df_term_raw.columns[idx]
                parsed = pd.to_datetime(df_term_raw.loc[df_term.index, col], errors="coerce")
            except Exception:
                continue
            if parsed.isna().all():
                continue
            years = parsed.dt.year.dropna()
            if len(years) > 0 and (years < 1990).all():
                continue
            mask_na = df_term["hire_date"].isna()
            mask_ok = parsed.notna() & (parsed < df_term["termination_date"])
            fill = mask_na & mask_ok
            if fill.any():
                df_term.loc[fill, "hire_date"] = pd.to_datetime(parsed.loc[fill]).dt.normalize()
                logger.info(f"Дата трудоустройства заполнена из столбца с индексом {idx} ('{col}') для {fill.sum()} записей уволенных")
                break
    # Последний запасной вариант: перебрать столбцы листа — дата раньше даты увольнения подойдёт как дата приёма (только реальные календарные даты, не числа)
    if df_term["hire_date"].isna().any() and df_term["termination_date"].notna().any():
        term_col = "Дата увольнения" if "Дата увольнения" in df_term_raw.columns else df_term_raw.columns[21] if len(df_term_raw.columns) > 21 else None
        skip_cols = {term_col, "Дата рождения"}  # дату рождения не подставляем как дату приёма
        for col in df_term_raw.columns:
            if col in skip_cols:
                continue
            try:
                raw_vals = df_term_raw.loc[df_term.index, col] if df_term.index.isin(df_term_raw.index).all() else df_term_raw.reindex(df_term.index)[col]
                parsed = pd.to_datetime(raw_vals, errors="coerce")
            except Exception:
                continue
            if parsed.isna().all():
                continue
            # Пропускаем столбцы с числами, которые pandas превратил в 1970-01-01 (наносекунды с эпохи)
            years = parsed.dt.year.dropna()
            if len(years) > 0 and (years < 1990).all():
                continue
            mask_na = df_term["hire_date"].isna()
            mask_before = parsed < df_term["termination_date"]
            fill = mask_na & mask_before
            if fill.any():
                vals = pd.to_datetime(parsed.loc[fill]).dt.normalize()
                df_term.loc[fill, "hire_date"] = vals
                logger.info(f"Дата трудоустройства заполнена из столбца '{col}' для {fill.sum()} записей (приняты и уволились в том же периоде)")
                break
    df_term["birth_date"] = pd.to_datetime(df_term["Дата рождения"], errors="coerce")
    df_term["department"] = df_term["ОтделФакт"]
    df_term["gender_raw"] = df_term["Пол"].apply(normalize_gender)

    # Обработка данных из листа "Увольнения Склад и Торги"
    if df_term_warehouse_raw is not None and len(df_term_warehouse_raw) > 0:
        logger.info("Обработка данных из листа 'Увольнения Склад и Торги'...")
        df_term_warehouse = df_term_warehouse_raw.copy()
        
        # Фильтрация: исключаем строки с пустым или некорректным ФИО
        initial_count_warehouse = len(df_term_warehouse)
        df_term_warehouse = df_term_warehouse[df_term_warehouse["ФИО"].notna()].copy()
        df_term_warehouse = df_term_warehouse[df_term_warehouse["ФИО"].astype(str).str.strip() != ""].copy()
        # Исключаем служебные строки
        df_term_warehouse = df_term_warehouse[~df_term_warehouse["ФИО"].astype(str).str.strip().str.lower().isin(service_keywords)].copy()
        filtered_count_warehouse = len(df_term_warehouse)
        if initial_count_warehouse != filtered_count_warehouse:
            logger.info(f"Отфильтровано {initial_count_warehouse - filtered_count_warehouse} строк с некорректным ФИО в таблице увольнений склада. Осталось: {filtered_count_warehouse} строк")
        
        # Дата трудоустройства (для учёта «принято с начала года» по всем листам)
        hire_date_col_wh = None
        for col_name in ["Дата трудоустройства", "Дата приема", "Дата приёма"]:
            if col_name in df_term_warehouse.columns:
                hire_date_col_wh = col_name
                break
        if hire_date_col_wh:
            ser_wh = df_term_warehouse[hire_date_col_wh].astype(str).str.strip()
            df_term_warehouse["hire_date"] = parse_date(ser_wh)
            still_na = df_term_warehouse["hire_date"].isna() & (ser_wh != "") & (ser_wh.str.lower() != "nan")
            if still_na.any():
                df_term_warehouse.loc[still_na, "hire_date"] = pd.to_datetime(df_term_warehouse.loc[still_na, hire_date_col_wh], errors="coerce")
        else:
            logger.warning("Столбец 'Дата трудоустройства' не найден в листе увольнений склада")
            df_term_warehouse["hire_date"] = pd.NaT
        
        # Дата увольнения
        if "Дата увольнения" in df_term_warehouse.columns:
            ser_tw = df_term_warehouse["Дата увольнения"].astype(str).str.strip()
            df_term_warehouse["termination_date"] = parse_date(ser_tw)
            still_na_t = df_term_warehouse["termination_date"].isna() & (ser_tw != "") & (ser_tw.str.lower() != "nan")
            if still_na_t.any():
                df_term_warehouse.loc[still_na_t, "termination_date"] = pd.to_datetime(df_term_warehouse.loc[still_na_t, "Дата увольнения"], errors="coerce")
        else:
            logger.warning("Столбец 'Дата увольнения' не найден в листе увольнений склада")
            df_term_warehouse["termination_date"] = pd.NaT
        
        # Дата рождения
        if "Дата рождения" in df_term_warehouse.columns:
            df_term_warehouse["birth_date"] = pd.to_datetime(df_term_warehouse["Дата рождения"], errors="coerce")
        else:
            logger.warning("Столбец 'Дата рождения' не найден в листе увольнений склада")
            df_term_warehouse["birth_date"] = pd.NaT
        
        # Отдел
        if "ОтделФакт" in df_term_warehouse.columns:
            df_term_warehouse["department"] = df_term_warehouse["ОтделФакт"]
        elif "Отдел" in df_term_warehouse.columns:
            df_term_warehouse["department"] = df_term_warehouse["Отдел"]
        else:
            logger.warning("Столбец 'ОтделФакт' или 'Отдел' не найден в листе увольнений склада")
            df_term_warehouse["department"] = None
        
        # Пол
        if "Пол" in df_term_warehouse.columns:
            df_term_warehouse["gender_raw"] = df_term_warehouse["Пол"].apply(normalize_gender)
        else:
            logger.warning("Столбец 'Пол' не найден в листе увольнений склада")
            df_term_warehouse["gender_raw"] = None
        
        # Объединяем два датафрейма с увольнениями
        logger.info(f"Объединение данных об увольнениях: основная таблица ({len(df_term)} строк) + склад ({len(df_term_warehouse)} строк)")
        df_term_combined = pd.concat([df_term, df_term_warehouse], ignore_index=True)
        
        # Убираем дубликаты по ФИО и дате увольнения
        before_dedup = len(df_term_combined)
        df_term_combined = df_term_combined.drop_duplicates(subset=["ФИО", "termination_date"], keep="first")
        after_dedup = len(df_term_combined)
        if before_dedup != after_dedup:
            logger.warning(f"Найдено и удалено {before_dedup - after_dedup} дубликатов увольнений")
        
        # Заменяем df_term на объединенный датафрейм
        df_term = df_term_combined
        logger.info(f"Итого увольнений после объединения: {len(df_term)} строк")
        
        # Статистика по увольнениям из листа склада
        warehouse_terms_with_date = df_term_warehouse["termination_date"].notna().sum()
        logger.info(f"Увольнений из листа 'Склад и Торги' с датой увольнения: {warehouse_terms_with_date}")
    else:
        logger.warning("ВНИМАНИЕ: Лист 'Увольнения Склад и Торги' не загружен! Увольнения склада НЕ учитываются в отчете!")

    # Объединенный датафрейм для расчета показателей во времени (как в проверочных скриптах)
    df_all = pd.concat(
    [
        pd.DataFrame(
            {
                "ФИО": df_main["ФИО"],
                "hire_date": df_main["hire_date"],
                "termination_date": df_main["termination_date_hr"],
                "birth_date": df_main["birth_date"],
                "department": df_main["department"],
                "gender_raw": df_main["gender_raw"],
            }
        ),
        pd.DataFrame(
            {
                "ФИО": df_term["ФИО"],
                "hire_date": df_term["hire_date"],
                "termination_date": df_term["termination_date"],
                "birth_date": df_term["birth_date"],
                "department": df_term["department"],
                "gender_raw": df_term["gender_raw"],
            }
        ),
    ],
    ignore_index=True,
    )

    # Убираем дубликаты, оставляя одну запись на одного сотрудника с конкретной датой найма
    df_all = df_all.drop_duplicates(subset=["ФИО", "hire_date"], keep="first")

    # ========== РАСЧЕТ МЕТРИК (только из данных таблиц) ==========
    logger.info("Этап 3: Расчет метрик")
    
    # Добавляем расчет возраста и стажа в df_main
    logger.debug("Расчет возраста и стажа сотрудников...")
    df_main["age"] = (now - df_main["birth_date"]).dt.days / 365.25
    df_main["tenure"] = (now - df_main["hire_date"]).dt.days / 365.25
    logger.debug(f"Средний возраст (предварительно): {df_main['age'].mean():.2f} лет")
    logger.debug(f"Средний стаж (предварительно): {df_main['tenure'].mean():.2f} лет")

    # ИНИЦИАЛЬНЫЕ МЕТРИКИ (будут позже синхронизированы с помесячными сериями)
    # Количество сотрудников: из основной таблицы (df_main) — все записи с ФИО
    total_employees = df_main["ФИО"].notna().sum()
    logger.info(f"Общая численность сотрудников (предварительно): {total_employees}")

    # Средний стаж и возраст: пока считаем по df_main (для диагностики),
    # далее переопределим значениями за последний месяц из помесячных серий
    df_main_with_data = df_main[df_main["ФИО"].notna()]
    avg_tenure = df_main_with_data["tenure"].mean() if not df_main_with_data.empty and df_main_with_data["tenure"].notna().any() else 0.0
    avg_age = df_main_with_data["age"].mean() if not df_main_with_data.empty and df_main_with_data["age"].notna().any() else 0.0
    logger.info(f"Средний стаж (предварительно): {avg_tenure:.2f} лет")
    logger.info(f"Средний возраст (предварительно): {avg_age:.2f} лет")

    # Сотрудники по полу: начальные значения из df_main (для диагностики),
    # реальные метрики для отчета будут взяты из помесячных серий за последний месяц
    gender_series = df_main[df_main["ФИО"].notna()]["gender_raw"]
    male_count = (gender_series == "м").sum()
    female_count = (gender_series == "ж").sum()
    logger.info(f"Распределение по полу (предварительно): Мужчин: {male_count}, Женщин: {female_count}, Всего: {male_count + female_count}")
    
    unique_genders = gender_series.unique()
    logger.debug(f"Уникальные значения пола после нормализации: {list(unique_genders)}")

    # Год - используем данные только ДО текущего месяца включительно
    year_start = datetime(TARGET_YEAR, 1, 1)
    # Изменяем на конец текущего месяца вместо конца года
    current_month_end = now
    logger.debug(f"Период расчета YTD: с {year_start.strftime('%Y-%m-%d')} по {current_month_end.strftime('%Y-%m-%d')}")

    # --- Принято с начала года: с 01.01 по дату формирования отчёта, по ВСЕМ листам (Список сотрудников + Увольнение + Увольнения Склад и Торги) ---
    # Период: 1 января TARGET_YEAR — дата формирования отчёта (включительно). Учитываем всех, кого приняли в этом периоде, в т.ч. уже уволенных.
    logger.info("Расчет «принято с начала года» (01.01 — дата отчёта) по всем листам: Список сотрудников + Увольнение + Увольнения Склад и Торги...")
    period_start = year_start  # 1 января
    period_end = current_month_end  # дата формирования отчёта

    # Таблица 1 — «Список сотрудников»: дата приёма в периоде
    mask_main = (
        df_main["hire_date"].notna()
        & (df_main["hire_date"] >= period_start)
        & (df_main["hire_date"] <= period_end)
    )
    hired_ytd_from_list = mask_main.sum()

    # Таблица 2 — все листы увольнений («Увольнение» + «Увольнения Склад и Торги»): считаем принятыми с 01.01 по дату отчёта:
    # (1) дата приёма в периоде; (2) даты приёма нет, но дата увольнения в периоде; (3) приём в дек. прошлого года, увольнение в этом году;
    # (4) дата приёма в том же году что и увольнение (год = TARGET_YEAR), но дата не попала в период из-за формата — тоже считаем принятыми за год
    prev_year_end = datetime(TARGET_YEAR - 1, 12, 31)
    dec_prev_year_start = datetime(TARGET_YEAR - 1, 12, 1)

    mask_term_with_hire = (
        df_term["hire_date"].notna()
        & (df_term["hire_date"] >= period_start)
        & (df_term["hire_date"] <= period_end)
    )
    mask_term_no_hire_but_terminated_in_period = (
        df_term["hire_date"].isna()
        & (df_term["termination_date"].notna())
        & (df_term["termination_date"] >= period_start)
        & (df_term["termination_date"] <= period_end)
    )
    # Приняты в декабре прошлого года и уволены в этом году
    mask_term_hire_dec_prev_terminated_this = (
        df_term["hire_date"].notna()
        & (df_term["hire_date"] >= dec_prev_year_start)
        & (df_term["hire_date"] <= prev_year_end)
        & (df_term["termination_date"].notna())
        & (df_term["termination_date"] >= period_start)
        & (df_term["termination_date"] <= period_end)
        & ~mask_term_with_hire
    )
    # Уволены в отчётном году и дата приёма тоже в отчётном году (приняты и уволены в одном году) — на случай ошибки парсинга даты
    mask_term_hire_year_equals_term_year = (
        (df_term["termination_date"].notna())
        & (df_term["termination_date"] >= period_start)
        & (df_term["termination_date"] <= period_end)
        & (df_term["hire_date"].notna())
        & (df_term["hire_date"].dt.year == TARGET_YEAR)
        & ~mask_term_with_hire
        & ~mask_term_hire_dec_prev_terminated_this
    )
    hired_ytd_from_terminated = (
        mask_term_with_hire.sum()
        + mask_term_no_hire_but_terminated_in_period.sum()
        + mask_term_hire_dec_prev_terminated_this.sum()
        + mask_term_hire_year_equals_term_year.sum()
    )
    extra_from_no_hire_date = mask_term_no_hire_but_terminated_in_period.sum()
    extra_from_dec_prev = mask_term_hire_dec_prev_terminated_this.sum()
    extra_from_same_year = mask_term_hire_year_equals_term_year.sum()

    # Итого принято за год = из первой таблицы + из второй таблицы (один человек не может быть в обеих таблицах одновременно)
    hired_ytd = int(hired_ytd_from_list) + int(hired_ytd_from_terminated)
    logger.info(
        f"Принято с начала года: период {period_start.strftime('%d.%m.%Y')} — {period_end.strftime('%d.%m.%Y')}. "
        f"Лист «Список сотрудников»: {hired_ytd_from_list} чел.; листы увольнений (Увольнение + Склад и Торги): {hired_ytd_from_terminated} чел. "
        f"(с датой приёма в периоде; без даты приёма по дате увольнения: +{extra_from_no_hire_date}; приём в дек. прошлого года: +{extra_from_dec_prev}; приём и увольнение в одном году: +{extra_from_same_year}); всего: {hired_ytd} чел."
    )
    if extra_from_no_hire_date > 0:
        logger.info(
            f"Учтено {extra_from_no_hire_date} чел.: уволены в текущем году, дата приёма в реестре не заполнена — считаем принятыми в этом году."
        )
    if extra_from_dec_prev > 0:
        logger.info(
            f"Учтено {extra_from_dec_prev} чел.: дата приёма в декабре {TARGET_YEAR - 1} г., увольнение в {TARGET_YEAR} г. — считаем принятыми за отчётный год."
        )
    if extra_from_same_year > 0:
        logger.info(
            f"Учтено {extra_from_same_year} чел.: дата приёма и увольнения в {TARGET_YEAR} г. (приняты и уволены в одном году)."
        )

    # Диагностика: уволенные в 2026 — сколько с датой приёма в периоде, сколько без
    term_in_period = (df_term["termination_date"].notna() & (df_term["termination_date"] >= period_start) & (df_term["termination_date"] <= period_end))
    term_in_period_with_hire = term_in_period & df_term["hire_date"].notna() & (df_term["hire_date"] >= period_start) & (df_term["hire_date"] <= period_end)
    term_in_period_hire_outside = term_in_period & df_term["hire_date"].notna() & ~((df_term["hire_date"] >= period_start) & (df_term["hire_date"] <= period_end))
    term_in_period_no_hire = term_in_period & df_term["hire_date"].isna()
    logger.info(
        f"Уволенных в периоде {period_start.date()}—{period_end.date()}: всего {term_in_period.sum()}; "
        f"с датой приёма в периоде (учтены): {term_in_period_with_hire.sum()}; "
        f"с датой приёма вне периода: {term_in_period_hire_outside.sum()}; "
        f"без даты приёма (учтены по дате увольнения): {term_in_period_no_hire.sum()}."
    )
    if term_in_period_hire_outside.any():
        sample = df_term.loc[term_in_period_hire_outside, ["ФИО", "hire_date", "termination_date"]].head(5)
        for _, r in sample.iterrows():
            logger.info(f"  Пример: {r['ФИО']} — приём {r['hire_date']} увольнение {r['termination_date']}")
        # Если ожидается больше принятых в отчётном году: у части уволенных в этом году дата приёма в реестре указана за прошлые годы — проверьте в Excel столбец «Дата трудоустройства» для тех, кого приняли и уволили в одном году
        if term_in_period_hire_outside.sum() >= 2:
            logger.warning(
                f"У {term_in_period_hire_outside.sum()} уволенных в {TARGET_YEAR} г. в реестре указана дата приёма не в {TARGET_YEAR} г. "
                "Если среди них есть принятые и уволенные в этом же году — исправьте «Дата трудоустройства» в листе «Увольнение» на фактическую дату приёма в этом году."
            )

    # В лог (INFO) список ФИО для сверки метрики
    fios_list = list(df_main.loc[mask_main, "ФИО"].dropna().astype(str).str.strip())
    fios_term = list(df_term.loc[mask_term_with_hire, "ФИО"].dropna().astype(str).str.strip())
    fios_term_dec_prev = list(df_term.loc[mask_term_hire_dec_prev_terminated_this, "ФИО"].dropna().astype(str).str.strip())
    fios_term_same_year = list(df_term.loc[mask_term_hire_year_equals_term_year, "ФИО"].dropna().astype(str).str.strip())
    fios_term_no_hire = list(df_term.loc[mask_term_no_hire_but_terminated_in_period, "ФИО"].dropna().astype(str).str.strip())
    logger.info(
        f"Принято с начала года — список для сверки: из «Список сотрудников» ({len(fios_list)}): {fios_list[:30]}{'...' if len(fios_list) > 30 else ''}"
    )
    logger.info(
        f"Принято с начала года — из «Увольнение» с датой приёма в периоде ({len(fios_term)}): {fios_term[:30]}{'...' if len(fios_term) > 30 else ''}"
    )
    if fios_term_dec_prev:
        logger.info(f"Принято с начала года — из листов увольнений, приём в дек. прошлого года ({len(fios_term_dec_prev)}): {fios_term_dec_prev}")
    if fios_term_same_year:
        logger.info(f"Принято с начала года — из листов увольнений, приём и увольнение в одном году ({len(fios_term_same_year)}): {fios_term_same_year}")
    if fios_term_no_hire:
        logger.info(f"Принято с начала года — из листов увольнений, без даты приёма, по дате увольнения ({len(fios_term_no_hire)}): {fios_term_no_hire}")

    # Диагностика: кто именно попал в «принято с начала года» (в лог на уровне DEBUG)
    _list_main = df_main.loc[mask_main, ["ФИО", "hire_date"]].copy()
    _list_main["hire_date"] = _list_main["hire_date"].dt.strftime("%d.%m.%Y")
    _list_main["источник"] = "Список сотрудников"
    _list_term1 = df_term.loc[mask_term_with_hire, ["ФИО", "hire_date"]].copy()
    _list_term1["hire_date"] = _list_term1["hire_date"].dt.strftime("%d.%m.%Y")
    _list_term1["источник"] = "Увольнение (дата приёма)"
    _list_term2 = df_term.loc[mask_term_no_hire_but_terminated_in_period, ["ФИО", "termination_date"]].copy()
    _list_term2["hire_date"] = "(нет в реестре)"
    _list_term2["источник"] = "Увольнение (учтено по дате увольнения)"
    for _, row in _list_main.iterrows():
        logger.debug(f"  Принят YTD [список]: {row['ФИО']} — дата приёма {row['hire_date']}")
    for _, row in _list_term1.iterrows():
        logger.debug(f"  Принят YTD [уволен]: {row['ФИО']} — дата приёма {row['hire_date']}")
    for _, row in _list_term2.iterrows():
        td = row["termination_date"]
        td_str = td.strftime("%d.%m.%Y") if pd.notna(td) and hasattr(td, "strftime") else "?"
        logger.debug(f"  Принят YTD [без даты приёма]: {row['ФИО']} — уволен {td_str}")

    logger.debug("Расчет уволенных сотрудников с начала года...")
    terminated_ytd = df_term[
        (df_term["termination_date"].notna())
        & (df_term["termination_date"] >= year_start)
        & (df_term["termination_date"] <= current_month_end)
    ].shape[0]

    # Применяем фиксированные значения в режиме DEMO
    if DATA_MODE == "demo":
        logger.info("Режим DEMO: использование фиксированных значений")
        hired_ytd = 96
        terminated_ytd = 68
    
    logger.info(f"Принято с начала года (YTD): {hired_ytd} человек")
    logger.info(f"Уволено с начала года (YTD): {terminated_ytd} человек")

    # Текущий месяц: с 1-го числа по сегодня (данные на момент отчёта)
    month_start = now.replace(day=1)
    month_end = now
    logger.debug(f"Текущий месяц: с {month_start.strftime('%Y-%m-%d')} по {month_end.strftime('%Y-%m-%d')} (на дату отчёта)")

    # --- Принято / уволено за текущий месяц: принято — по df_all (все принятые за месяц, в т.ч. уже уволенные) ---
    logger.debug("Расчет принятых сотрудников за текущий месяц...")
    hires_month = df_all[
        (df_all["hire_date"].notna())
        & (df_all["hire_date"] >= month_start)
        & (df_all["hire_date"] <= month_end)
    ].shape[0]

    logger.debug("Расчет уволенных сотрудников за текущий месяц...")
    terms_month = df_term[
        (df_term["termination_date"].notna())
        & (df_term["termination_date"] >= month_start)
        & (df_term["termination_date"] <= month_end)
    ].shape[0]

    # Применяем фиксированные значения в режиме DEMO
    if DATA_MODE == "demo":
        hires_month = 9
        terms_month = 4
    
    logger.info(f"Принято за текущий месяц: {hires_month} человек")
    logger.info(f"Уволено за текущий месяц: {terms_month} человек")

    # Текучесть
    logger.info("Расчет текучести персонала...")
    if DATA_MODE == "demo":
        logger.info("Режим DEMO: использование фиксированных значений текучести")
        turnover_ytd = 17.3
        turnover_period = 1.00
    else:
        # Текучесть за год (как в hrAnaliticSecondList): Уволено с начала года / численность на дату отчёта × 100
        headcount_at_now = df_main["ФИО"].notna().sum()
        turnover_ytd = (
            terminated_ytd / headcount_at_now * 100
            if headcount_at_now > 0
            else 0
        )
        logger.info(f"Текучесть за год: {turnover_ytd:.2f}% (знаменатель: численность на дату отчёта {headcount_at_now})")
        # Текучесть за период будет взята из помесячной серии (последний месяц),
        # по формуле эталона: уволено за месяц / численность на конец месяца × 100

    # ========== ПОМЕСЯЧНЫЕ СЕРИИ (последние 7 месяцев) ==========
    logger.info("Этап 3.1: Расчет помесячных серий (последние 7 месяцев)")
    month_labels_7 = []
    month_labels_7_short = []
    headcount_7 = []
    avg_tenure_7 = []
    avg_age_7 = []
    male_count_7 = []
    female_count_7 = []
    male_pct_7 = []
    female_pct_7 = []
    turnover_series_7 = []          # Общий коэффициент текучести, %
    terminations_7 = []             # Количество уволенных сотрудников за месяц (все)
    male_turnover_7 = []            # Текучесть по мужчинам, %
    female_turnover_7 = []          # Текучесть по женщинам, %
    male_termed_7 = []              # Количество уволенных мужчин за месяц
    female_termed_7 = []            # Количество уволенных женщин за месяц

    logger.debug("Начало расчета помесячных метрик...")
    for offset in range(6, -1, -1):
        m_start = month_start - pd.DateOffset(months=offset)
        # Для текущего месяца — по сегодня; для прошлых — по конец месяца
        if offset == 0:
            m_end = now
        else:
            m_end = m_start + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        logger.debug(f"Расчет для месяца: {m_start.strftime('%Y-%m')} по {m_end.strftime('%Y-%m-%d')} (offset={offset})")

        # Активные сотрудники на конец месяца: как в проверочном скрипте (df_all)
        active_end_m = df_all[
            (df_all["hire_date"].notna())
            & (df_all["hire_date"] <= m_end)
            & (df_all["termination_date"].isna() | (df_all["termination_date"] > m_end))
        ]
        headcount_7.append(active_end_m.shape[0])
        
        # Средний стаж и возраст на конец месяца: считаем по активным на конец месяца
        tenure_m_values = (m_end - active_end_m["hire_date"]).dt.days / 365.25
        age_m_values = (m_end - active_end_m["birth_date"]).dt.days / 365.25
        
        tenure_m = tenure_m_values.mean() if tenure_m_values.notna().any() else 0.0
        age_m = age_m_values.mean() if age_m_values.notna().any() else 0.0
        avg_tenure_7.append(tenure_m)
        avg_age_7.append(age_m)

        # Пол по активным на конец месяца
        gender_series_m = active_end_m["gender_raw"]
        male_m = (gender_series_m == "м").sum()
        female_m = (gender_series_m == "ж").sum()
        male_count_7.append(male_m)
        female_count_7.append(female_m)
        
        total_gender = male_m + female_m
        if total_gender > 0:
            male_pct_7.append(male_m / total_gender * 100)
            female_pct_7.append(female_m / total_gender * 100)
        else:
            male_pct_7.append(0)
            female_pct_7.append(0)

        # Текучесть (общая): используем df_all (активные на начало месяца) и df_term (уволенные)
        active_start_m = df_all[
            (df_all["hire_date"].notna())
            & (df_all["hire_date"] <= m_start)
            & (df_all["termination_date"].isna() | (df_all["termination_date"] > m_start))
        ].shape[0]

        termed_m_df = df_term[
            (df_term["termination_date"].notna())
            & (df_term["termination_date"] >= m_start)
            & (df_term["termination_date"] <= m_end)
        ]
        termed_m = termed_m_df.shape[0]
        terminations_7.append(termed_m)

        # Текучесть за месяц (как в hrAnaliticSecondList): уволено за месяц / численность на конец месяца × 100
        headcount_end_m = headcount_7[-1]
        turnover_m = termed_m / headcount_end_m * 100 if headcount_end_m > 0 else 0
        turnover_series_7.append(turnover_m)

        # Текучесть по полу: (уволено по полу / среднесписочная численность по полу) * 100%
        # Активные на начало месяца по полу
        active_start_m_gender = df_all[
            (df_all["hire_date"].notna())
            & (df_all["hire_date"] <= m_start)
            & (df_all["termination_date"].isna() | (df_all["termination_date"] > m_start))
        ]
        gender_series_start = active_start_m_gender["gender_raw"]
        male_start_m = (gender_series_start == "м").sum()
        female_start_m = (gender_series_start == "ж").sum()

        # Уволенные за месяц по полу
        termed_m_gender = termed_m_df
        male_termed_m = (termed_m_gender["gender_raw"] == "м").sum()
        female_termed_m = (termed_m_gender["gender_raw"] == "ж").sum()

        # Среднесписочная численность по полу за месяц (среднее между началом и концом месяца)
        male_avg_headcount_m = (male_start_m + male_m) / 2 if (male_start_m + male_m) > 0 else 0
        female_avg_headcount_m = (female_start_m + female_m) / 2 if (female_start_m + female_m) > 0 else 0

        male_turnover = male_termed_m / male_avg_headcount_m * 100 if male_avg_headcount_m > 0 else 0
        female_turnover = female_termed_m / female_avg_headcount_m * 100 if female_avg_headcount_m > 0 else 0

        male_turnover_7.append(male_turnover)
        female_turnover_7.append(female_turnover)
        male_termed_7.append(male_termed_m)
        female_termed_7.append(female_termed_m)

        month_labels_7.append(MONTH_NAMES_RU.get(m_start.month, m_start.strftime("%B")))
        month_labels_7_short.append(MONTH_NAMES_RU.get(m_start.month, m_start.strftime("%b"))[:3])
        logger.info(f"Месяц {month_labels_7[-1]} ({m_start.strftime('%Y-%m')}): численность={headcount_7[-1]}, текучесть={turnover_m:.2f}%, уволено={termed_m}, стаж={tenure_m:.2f}л, возраст={age_m:.2f}л")
    
    logger.info(f"Помесячные серии рассчитаны для {len(month_labels_7)} месяцев: {', '.join(month_labels_7)}")
    logger.info(f"Численность по месяцам: {headcount_7}")
    logger.info(f"Текучесть по месяцам: {[f'{x:.2f}%' for x in turnover_series_7]}")
    logger.info(f"Средний стаж по месяцам: {[f'{x:.2f}' for x in avg_tenure_7]}")
    logger.info(f"Средний возраст по месяцам: {[f'{x:.2f}' for x in avg_age_7]}")
    
    # Проверка, что все 7 месяцев рассчитаны
    if len(month_labels_7) != 7:
        logger.warning(f"ВНИМАНИЕ: Рассчитано только {len(month_labels_7)} месяцев вместо 7!")
    else:
        logger.info("✓ Все 7 месяцев успешно рассчитаны")

    # Текучесть за период = последняя точка графика (текущий месяц), чтобы цифра и график совпадали
    if DATA_MODE != "demo" and turnover_series_7:
        turnover_period = turnover_series_7[-1]
        logger.info(f"Текучесть за период (текущий месяц, как на графике): {turnover_period:.2f}%")

    # СИНХРОНИЗАЦИЯ ВЕРХНИХ МЕТРИК С ПОМЕСЯЧНЫМИ СЕРИЯМИ
    # Для численности используем правильное значение из df_main (только активные сотрудники)
    # Для остальных метрик берем значения за последний месяц из рассчитанных рядов
    if headcount_7:
        last_idx = len(headcount_7) - 1
        
        # ВАЖНО: Используем правильную численность из df_main, а не из headcount_7
        # headcount_7 рассчитывается на основе df_all, который может давать неточные результаты
        # Правильная численность - это количество активных сотрудников в df_main
        total_employees_correct = df_main["ФИО"].notna().sum()
        logger.info(f"Правильная численность из df_main: {total_employees_correct}")
        logger.info(f"Численность из headcount_7 (последний месяц): {headcount_7[last_idx]}")
        
        # Используем правильное значение
        total_employees = total_employees_correct
        
        avg_tenure = avg_tenure_7[last_idx] if avg_tenure_7 else 0.0
        avg_age = avg_age_7[last_idx] if avg_age_7 else 0.0
        
        # Для распределения по полу также используем правильные значения из df_main
        gender_series_correct = df_main[df_main["ФИО"].notna()]["gender_raw"]
        male_count = (gender_series_correct == "м").sum()
        female_count = (gender_series_correct == "ж").sum()
        
        logger.info("Синхронизация метрик")
        logger.info(f"Месяц: {month_labels_7[last_idx]}")
        logger.info(f"Численность (исправлено): {total_employees}")
        logger.info(f"Средний стаж: {avg_tenure:.2f} лет")
        logger.info(f"Средний возраст: {avg_age:.2f} лет")
        logger.info(f"Распределение по полу: Мужчин: {male_count}, Женщин: {female_count}")

    # Применяем фиксированные данные текучести в режиме DEMO
    if DATA_MODE == "demo":
        # Фиксированные значения: Февраль 2.59%, Март 3.40%, Апрель 2.02%, Май 2.17%, Июнь 2.07%, Июль 0.76%, Август 1.00%
        turnover_series_7 = [2.59, 3.40, 2.02, 2.17, 2.07, 0.76, 1.00]
        # Убеждаемся что месяцы правильные: Февраль, Март, Апрель, Май, Июнь, Июль, Август
        month_labels_7 = ["Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август"]
        month_labels_7_short = ["Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг"]


    # ========== ДАННЫЕ ПО ОТДЕЛАМ (только для текущего месяца) ==========
    logger.info("Этап 3.2: Расчет данных по отделам")
    if DATA_MODE == "demo":
        logger.info("Режим DEMO: использование фиксированных данных по отделам")
        # Фиксированные данные для демонстрации
        dept_data_sorted = [
        {"name": "Отдел маркетинга", "hired": 2, "terminated": 0},
        {"name": "IT", "hired": 1, "terminated": 0},
        {"name": "Администрация", "hired": 1, "terminated": 1},
        {"name": "Отдел закупок", "hired": 1, "terminated": 0},
        {"name": "Отдел поддержки продаж", "hired": 1, "terminated": 0},
        {"name": "Отдел развития", "hired": 1, "terminated": 1},
        {"name": "Финансовый отдел", "hired": 1, "terminated": 0},
        {"name": "Электроторг", "hired": 1, "terminated": 1},
        {"name": "E-commerce", "hired": 0, "terminated": 1},
        {"name": "ФСК", "hired": 0, "terminated": 1},
        ]
        dept_names = [d["name"] for d in dept_data_sorted]
        dept_names = [d["name"] for d in dept_data_sorted]
        dept_hired_list = [d["hired"] for d in dept_data_sorted]
        dept_term_list = [-d["terminated"] for d in dept_data_sorted]
        logger.info(f"Использовано {len(dept_names)} отделов из демо-данных")
    else:
        logger.debug("Расчет данных по отделам из реальных данных...")
        dept_data = []
        unique_depts = df_main["department"].dropna().unique()
        logger.debug(f"Найдено уникальных отделов: {len(unique_depts)}")
        for dept in unique_depts:
            # Принято по отделу за текущий месяц (по дате трудоустройства U)
            hired_dept = df_all[
                (df_all["department"] == dept)
                & (df_all["hire_date"].notna())
                & (df_all["hire_date"] >= month_start)
                & (df_all["hire_date"] <= month_end)
            ].shape[0]

            # Уволено по отделу за текущий месяц (по дате увольнения V)
            term_dept = df_term[
                (df_term["department"] == dept)
                & (df_term["termination_date"].notna())
                & (df_term["termination_date"] >= month_start)
                & (df_term["termination_date"] <= month_end)
            ].shape[0]
        
            if hired_dept > 0 or term_dept > 0:
                dept_data.append({
                    "name": dept,
                    "hired": hired_dept,
                    "terminated": term_dept,
                    "total": hired_dept + term_dept
                })
                logger.debug(f"Отдел '{dept}': принято={hired_dept}, уволено={term_dept}")

        # Сортируем по общему количеству и берем топ-10
        dept_data_sorted = sorted(dept_data, key=lambda x: x["total"], reverse=True)[:10]
        dept_names = [d["name"] for d in dept_data_sorted]
        dept_hired_list = [d["hired"] for d in dept_data_sorted]
        dept_term_list = [-d["terminated"] for d in dept_data_sorted]
        logger.info(f"Топ-10 отделов по движению: {len(dept_names)} отделов")
        logger.debug(f"Отделы: {dept_names}")

    # Списки принятых и уволенных за текущий месяц (для таблиц на листе 2); принятые — из df_all (в т.ч. уже уволенные)
    list_hired_month = df_all[
        (df_all["hire_date"].notna())
        & (df_all["hire_date"] >= month_start)
        & (df_all["hire_date"] <= month_end)
    ][["ФИО", "department", "hire_date"]].copy()
    list_hired_month = list_hired_month.sort_values("hire_date")
    list_hired_month["date_str"] = list_hired_month["hire_date"].dt.strftime("%d.%m.%Y")
    list_hired_month["dept_str"] = list_hired_month["department"].fillna("—").astype(str)

    list_term_month = df_term[
        (df_term["termination_date"].notna())
        & (df_term["termination_date"] >= month_start)
        & (df_term["termination_date"] <= month_end)
    ][["ФИО", "department", "termination_date"]].copy()
    list_term_month = list_term_month.sort_values("termination_date")
    list_term_month["date_str"] = list_term_month["termination_date"].dt.strftime("%d.%m.%Y")
    list_term_month["dept_str"] = list_term_month["department"].fillna("—").astype(str)

    logger.info(f"Для листа 2: принятых за месяц {len(list_hired_month)}, уволенных за месяц {len(list_term_month)}")

    # ========== ГЕНЕРАЦИЯ PDF ==========
    logger.info("Этап 4: Генерация PDF отчета")
    import os
    # Используем английское имя для надежности, но можно вернуть русское
    report_filename = os.path.abspath("HR-отчет.pdf")
    logger.info(f"Путь к файлу отчета: {report_filename}")

    try:
        logger.debug("Создание PDF файла...")
        with PdfPages(report_filename) as pdf:
            # ==================== ЛИСТ 1: HR-АНАЛИТИКА ====================
            logger.debug("Генерация листа 1: HR-аналитика...")
            fig1 = plt.figure(figsize=(16, 9))
            fig1.patch.set_facecolor("white")
            
            gs1 = GridSpec(4, 3, figure=fig1, 
                   height_ratios=[0.45, 1.8, 2.2, 0.25],
                   width_ratios=[1, 1, 1],
                   hspace=0.32, wspace=0.32,
                   left=0.05, right=0.97, top=0.94, bottom=0.06)

            # --- ЗАГОЛОВОК + ЛОГОТИП SDS справа ---
            ax_title1 = fig1.add_subplot(gs1[0, :])
            ax_title1.axis("off")
            ax_title1.text(0.01, 0.75, "HR-аналитика", 
                   fontsize=32, fontweight="bold", color=COLOR_BLUE, 
                   va="center", ha="left")
            ax_title1.text(0.01, 0.15, f"{current_month_name} {TARGET_YEAR}", 
                   fontsize=18, color="black", 
                   va="center", ha="left")
            ax_title1.text(0.99, 0.5, "SDS", 
                   fontsize=26, fontweight="bold", color=COLOR_BLUE, 
                   va="center", ha="right")

            # --- KPI КАРТОЧКИ С ВСТРОЕННЫМИ ГРАФИКАМИ (РЯД 2) ---
            logger.debug(f"Подготовка графиков: {len(month_labels_7_short)} месяцев")
            logger.debug(f"Метки месяцев (короткие): {month_labels_7_short}")
            logger.debug(f"Данные для графиков: headcount_7={len(headcount_7)}, avg_tenure_7={len(avg_tenure_7)}, avg_age_7={len(avg_age_7)}")
            x_pos = range(len(month_labels_7_short))
    
            # Карточка 1: Количество сотрудников + график численности
            ax_kpi11 = fig1.add_subplot(gs1[1, 0])
            ax_kpi11.axis("off")
            ax_kpi11.set_xlim(0, 1)
            ax_kpi11.set_ylim(0, 1)
    
            # Заголовок и значение
            ax_kpi11.text(0.05, 0.95, "Количество\nсотрудников, чел", 
                  fontsize=11, color=COLOR_GRAY, ha="left", va="top")
            ax_kpi11.text(0.95, 0.95, f"{total_employees:.0f}", 
                  fontsize=32, fontweight="bold", color=COLOR_BLUE, ha="right", va="top")
    
            # Встроенный график (максимально крупный и высокий)
            ax_chart1 = ax_kpi11.inset_axes([0.02, -0.02, 0.96, 0.68])
            ax_chart1.plot(x_pos, headcount_7, marker="o", markersize=7, 
                   linewidth=3, color=COLOR_BLUE)
            # Добавляем padding сверху для подписей
            y_range = max(headcount_7) - min(headcount_7)
            ax_chart1.set_ylim(min(headcount_7) - y_range*0.05, max(headcount_7) + y_range*0.15)
            for i, (x, y) in enumerate(zip(x_pos, headcount_7)):
                ax_chart1.text(x, y, f"{int(y)}", fontsize=9, ha="center", va="bottom", fontweight="bold")
            ax_chart1.set_xticks(x_pos)
            ax_chart1.set_xticklabels(month_labels_7_short, fontsize=9, rotation=45, ha="right")
            ax_chart1.grid(True, color=COLOR_LIGHT_GRAY, linestyle="--", alpha=0.3, linewidth=0.5)
            ax_chart1.spines["top"].set_visible(False)
            ax_chart1.spines["right"].set_visible(False)
            ax_chart1.tick_params(labelsize=9, pad=1)

            # Карточка 2: Средний стаж + график стажа
            ax_kpi12 = fig1.add_subplot(gs1[1, 1])
            ax_kpi12.axis("off")
            ax_kpi12.set_xlim(0, 1)
            ax_kpi12.set_ylim(0, 1)
    
            # Заголовок и значение
            ax_kpi12.text(0.05, 0.95, "Средний стаж, лет", 
                  fontsize=11, color=COLOR_GRAY, ha="left", va="top")
            ax_kpi12.text(0.95, 0.95, f"{avg_tenure:.2f}", 
                  fontsize=32, fontweight="bold", color=COLOR_BLUE, ha="right", va="top")
    
            # Встроенный график (максимально крупный и высокий)
            ax_chart2 = ax_kpi12.inset_axes([0.02, -0.02, 0.96, 0.68])
            ax_chart2.plot(x_pos, avg_tenure_7, marker="o", markersize=7, 
                   linewidth=3, color=COLOR_BLUE)
            # Добавляем padding сверху для подписей
            y_range = max(avg_tenure_7) - min(avg_tenure_7)
            ax_chart2.set_ylim(min(avg_tenure_7) - y_range*0.05, max(avg_tenure_7) + y_range*0.2)
            for i, (x, y) in enumerate(zip(x_pos, avg_tenure_7)):
                ax_chart2.text(x, y, f"{y:.2f}", fontsize=9, ha="center", va="bottom", fontweight="bold")
            ax_chart2.set_xticks(x_pos)
            ax_chart2.set_xticklabels(month_labels_7_short, fontsize=9, rotation=45, ha="right")
            ax_chart2.grid(True, color=COLOR_LIGHT_GRAY, linestyle="--", alpha=0.3, linewidth=0.5)
            ax_chart2.spines["top"].set_visible(False)
            ax_chart2.spines["right"].set_visible(False)
            ax_chart2.tick_params(labelsize=9, pad=1)

            # Карточка 3: Средний возраст + график возраста
            ax_kpi13 = fig1.add_subplot(gs1[1, 2])
            ax_kpi13.axis("off")
            ax_kpi13.set_xlim(0, 1)
            ax_kpi13.set_ylim(0, 1)
    
            # Заголовок и значение
            ax_kpi13.text(0.05, 0.95, "Средний возраст, лет", 
                  fontsize=11, color=COLOR_GRAY, ha="left", va="top")
            ax_kpi13.text(0.95, 0.95, f"{avg_age:.2f}", 
                  fontsize=32, fontweight="bold", color=COLOR_BLUE, ha="right", va="top")
    
            # Встроенный график (максимально крупный и высокий)
            ax_chart3 = ax_kpi13.inset_axes([0.02, -0.02, 0.96, 0.68])
            ax_chart3.plot(x_pos, avg_age_7, marker="o", markersize=7, 
                   linewidth=3, color=COLOR_BLUE)
            # Добавляем padding сверху для подписей
            y_range = max(avg_age_7) - min(avg_age_7)
            ax_chart3.set_ylim(min(avg_age_7) - y_range*0.05, max(avg_age_7) + y_range*0.2)
            for i, (x, y) in enumerate(zip(x_pos, avg_age_7)):
                ax_chart3.text(x, y, f"{y:.2f}", fontsize=9, ha="center", va="bottom", fontweight="bold")
            ax_chart3.set_xticks(x_pos)
            ax_chart3.set_xticklabels(month_labels_7_short, fontsize=9, rotation=45, ha="right")
            ax_chart3.grid(True, color=COLOR_LIGHT_GRAY, linestyle="--", alpha=0.3, linewidth=0.5)
            ax_chart3.spines["top"].set_visible(False)
            ax_chart3.spines["right"].set_visible(False)
            ax_chart3.tick_params(labelsize=9, pad=1)

            # --- РЯД 3: PIE CHART (пол) слева + GROUPED BAR CHART справа ---
            # PIE CHART слева (сплошной круг)
            ax_gender = fig1.add_subplot(gs1[2, 0])
            pos_pie = ax_gender.get_position()
            ax_gender.set_position([pos_pie.x0, pos_pie.y0 - 0.06, pos_pie.width, pos_pie.height * 0.92])
            gender_labels = ["М", "Ж"]
            gender_counts = [male_count, female_count]
            colors_gender = [COLOR_BLUE, COLOR_RED]
    
            wedges, texts, autotexts = ax_gender.pie(
                gender_counts, 
                labels=None,
                autopct=lambda pct: f'{int(pct/100*sum(gender_counts))}\n({pct:.0f}%)',
                colors=colors_gender, 
                startangle=90, 
                textprops={'fontsize': 13, 'fontweight': 'bold'},
                wedgeprops={'linewidth': 3, 'edgecolor': 'white'}  # Убрали width для сплошного круга
            )
    
            for i, autotext in enumerate(autotexts):
                autotext.set_color('white')
    
            # Легенда
            legend_labels = [f"{gender_labels[i]}" for i in range(len(gender_labels))]
            ax_gender.legend(wedges, legend_labels,
                     loc="center", bbox_to_anchor=(0.5, -0.12), fontsize=12, ncol=2)
    
            ax_gender.set_title("Количество сотрудников по\nполу", 
                        fontsize=13, fontweight="bold", color="black", pad=10)

            # GROUPED BAR CHART справа - динамика сотрудников по полу, % (доля мужчин и женщин по месяцам)
            ax_gender_dyn = fig1.add_subplot(gs1[2, 1:])
            pos_dyn = ax_gender_dyn.get_position()
            ax_gender_dyn.set_position([pos_dyn.x0, pos_dyn.y0 - 0.06, pos_dyn.width, pos_dyn.height * 0.92])
    
            # Ширина столбца и отступ между группами
            bar_width = 0.35
            x_male = [x - bar_width/2 for x in x_pos]
            x_female = [x + bar_width/2 for x in x_pos]
    
            # Рисуем столбцы: доля мужчин и женщин в общей численности за месяц (в процентах)
            bars_male = ax_gender_dyn.bar(x_male, male_pct_7, bar_width, 
                                   color=COLOR_BLUE, alpha=0.9, label="М")
            bars_female = ax_gender_dyn.bar(x_female, female_pct_7, bar_width, 
                                     color=COLOR_RED, alpha=0.9, label="Ж")
    
            # Подписи значений НАД столбцами (в процентах)
            for i, (m_val, f_val) in enumerate(zip(male_pct_7, female_pct_7)):
                ax_gender_dyn.text(x_male[i], m_val, f"{m_val:.2f}%", 
                           fontsize=9, ha="center", va="bottom", 
                           color="black", fontweight="bold")
                ax_gender_dyn.text(x_female[i], f_val, f"{f_val:.2f}%", 
                           fontsize=9, ha="center", va="bottom", 
                           color="black", fontweight="bold")
    
            # Настройка осей и внешнего вида
            ax_gender_dyn.set_xticks(x_pos)
            ax_gender_dyn.set_xticklabels(month_labels_7_short, fontsize=10)
            ax_gender_dyn.set_ylabel("%", fontsize=11)
    
            # Устанавливаем верхний предел с запасом для подписей (до 100% с небольшим запасом)
            max_pct = max(max(male_pct_7 or [0]), max(female_pct_7 or [0]))
            upper_limit = min(100, max(50, max_pct * 1.2)) if max_pct > 0 else 100
            ax_gender_dyn.set_ylim(0, upper_limit)
    
            ax_gender_dyn.set_title("Динамика сотрудников по полу, %", 
                            fontsize=13, fontweight="bold", color="black", pad=10)
            ax_gender_dyn.legend(loc="center", bbox_to_anchor=(0.5, -0.12), fontsize=11, framealpha=0.95, ncol=2)
            ax_gender_dyn.grid(True, axis='y', color=COLOR_LIGHT_GRAY, linestyle="--", alpha=0.4, linewidth=0.5)
            ax_gender_dyn.spines["top"].set_visible(False)
            ax_gender_dyn.spines["right"].set_visible(False)
            ax_gender_dyn.tick_params(labelsize=9)

            logger.debug("Сохранение листа 1 в PDF...")
            pdf.savefig(fig1, dpi=150)
            plt.close(fig1)
            logger.debug("Лист 1 сохранен")

            # ==================== ЛИСТ 2: по шаблону HR-аналитика [месяц] ====================
            logger.debug("Генерация листа 2 по шаблону...")
            fig2 = plt.figure(figsize=(16, 9))
            fig2.patch.set_facecolor("white")

            # Сетка: верхние данные (две равные колонки) + два графика
            gs2 = GridSpec(2, 2, figure=fig2,
                   height_ratios=[1.05, 2.1],
                   width_ratios=[1, 1],
                   hspace=0.35, wspace=0.28,
                   left=0.06, right=0.94, top=0.92, bottom=0.06)

            # --- Верхний ряд: две симметричные колонки ---
            ax_top_left = fig2.add_subplot(gs2[0, 0])
            ax_top_right = fig2.add_subplot(gs2[0, 1])
            for ax in (ax_top_left, ax_top_right):
                ax.axis("off")
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)

            # Левая колонка: заголовок и показатели за месяц
            ax_top_left.text(0.02, 0.95, "HR-аналитика", fontsize=28, fontweight="bold", color=COLOR_BLUE, va="top", ha="left")
            ax_top_left.text(0.02, 0.72, current_month_name, fontsize=20, color="black", va="top", ha="left")
            ax_top_left.text(0.02, 0.52, "Принято сотрудников, чел", fontsize=10, color="black", ha="left", va="top")
            ax_top_left.text(0.02, 0.36, f"{hires_month}", fontsize=26, fontweight="bold", color="black", ha="left", va="center")
            ax_top_left.text(0.22, 0.36, "▲", fontsize=18, color=COLOR_GREEN, va="center", ha="left")
            ax_top_left.text(0.02, 0.22, "Уволено сотрудников, чел", fontsize=10, color="black", ha="left", va="top")
            ax_top_left.text(0.02, 0.06, f"{terms_month}", fontsize=26, fontweight="bold", color="black", ha="left", va="center")
            ax_top_left.text(0.22, 0.06, "▼", fontsize=18, color=COLOR_RED, va="center", ha="left")

            # Правая колонка: YTD и текучесть (в две колонки внутри блока)
            turnover_ytd_str = f"{turnover_ytd:.2f}%".replace(".", ",")
            turnover_period_str = f"{turnover_period:.2f}%".replace(".", ",")
            col_left = 0.02
            col_right = 0.52
            top_label_y = 0.92
            top_value_y = 0.70
            bottom_label_y = 0.42
            bottom_value_y = 0.18

            ax_top_right.text(col_left, top_label_y, "Принято с начала года, чел", fontsize=9, color="black", ha="left", va="top")
            ax_top_right.text(col_left, top_value_y, f"{hired_ytd}", fontsize=26, fontweight="bold", color="black", ha="left", va="center")
            ax_top_right.text(col_left + 0.22, top_value_y, "▲", fontsize=22, color=COLOR_GREEN, va="center", ha="left")

            ax_top_right.text(col_right, top_label_y, "Уволено с начала года, чел", fontsize=9, color="black", ha="left", va="top")
            ax_top_right.text(col_right, top_value_y, f"{terminated_ytd}", fontsize=26, fontweight="bold", color="black", ha="left", va="center")
            ax_top_right.text(col_right + 0.22, top_value_y, "▼", fontsize=22, color=COLOR_RED, va="center", ha="left")

            ax_top_right.text(col_left, bottom_label_y, "Текучесть за год", fontsize=10, color="black", ha="left", va="top")
            ax_top_right.text(col_left, bottom_value_y, turnover_ytd_str, fontsize=24, fontweight="bold", color="black", ha="left", va="center")
            ax_top_right.text(col_right, bottom_label_y, "Текучесть за период", fontsize=10, color="black", ha="left", va="top")
            ax_top_right.text(col_right, bottom_value_y, turnover_period_str, fontsize=24, fontweight="bold", color="black", ha="left", va="center")

            # --- Ряд 1 слева: Принятые/уволенные по отделам (график уменьшен, чтобы верхние данные были видны) ---
            ax_tornado = fig2.add_subplot(gs2[1, 0])
            pos_tornado = ax_tornado.get_position()
            ax_tornado.set_position([pos_tornado.x0, pos_tornado.y0 + 0.11, pos_tornado.width, pos_tornado.height * 0.84])
            if dept_names:
                x_pos_dept = range(len(dept_names))
                width = 0.5
                # Столбцы одной линией: зелёный вверх (принято) и красный вниз (уволено) от одной нулевой оси по каждому отделу
                bars_h = ax_tornado.bar(x_pos_dept, dept_hired_list, width, color=COLOR_GREEN, alpha=1.0, label="Принято")
                bars_t = ax_tornado.bar(x_pos_dept, dept_term_list, width, color=COLOR_RED, alpha=1.0, label="Уволено")
                for i, (h, t) in enumerate(zip(dept_hired_list, dept_term_list)):
                    if h > 0:
                        ax_tornado.text(i, h / 2, f"{int(h)}", va="center", ha="center", fontsize=9, fontweight="bold", color="white")
                    if t < 0:
                        ax_tornado.text(i, t / 2, f"{int(-t)}", va="center", ha="center", fontsize=9, fontweight="bold", color="white")
                short_names = [name[:28] + "..." if len(name) > 28 else name for name in dept_names]
                ax_tornado.set_xticks(x_pos_dept)
                ax_tornado.set_xticklabels(short_names, fontsize=8, rotation=45, ha="right", va="top")
                ax_tornado.axhline(0, color="black", linewidth=0.8)
                ax_tornado.grid(True, axis="y", color=COLOR_LIGHT_GRAY, linestyle="-", alpha=0.3, linewidth=0.5)
                ax_tornado.set_ylabel("")
                ax_tornado.spines["top"].set_visible(False)
                ax_tornado.spines["right"].set_visible(False)
                ax_tornado.tick_params(labelsize=8, pad=2)
                legend_elements = [
                    mpatches.Patch(facecolor=COLOR_GREEN, label="Принято"),
                    mpatches.Patch(facecolor=COLOR_RED, label="Уволено"),
                ]
                ax_tornado.legend(handles=legend_elements, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=9, frameon=False)
                ax_tornado.set_title("Принятые/уволенные по отделам, чел", fontsize=12, fontweight="normal", pad=8)
            else:
                ax_tornado.axis("off")
                ax_tornado.text(0.5, 0.5, "Нет движения по отделам за месяц", ha="center", va="center", fontsize=11, color=COLOR_GRAY)

            # --- Ряд 1 справа: Динамика коэффициента текучести, % (как на шаблоне: значения над точками) ---
            ax_turnover = fig2.add_subplot(gs2[1, 1])
            ax_turnover.plot(x_pos, turnover_series_7, marker="o", markersize=8, markeredgecolor="white", markeredgewidth=1.5, linewidth=2.5, color=COLOR_BLUE)
            y_max = max(turnover_series_7) if turnover_series_7 else 4.0
            y_min = min(turnover_series_7) if turnover_series_7 else 0
            y_range = y_max - y_min if y_max != y_min else 1
            ax_turnover.set_ylim(y_min - y_range * 0.05, y_max + y_range * 0.25)
            for x, y in zip(x_pos, turnover_series_7):
                ax_turnover.text(x, y + y_range * 0.03, f"{y:.2f}", fontsize=9, ha="center", va="bottom", color="black")
            ax_turnover.set_xticks(x_pos)
            ax_turnover.set_xticklabels(month_labels_7, fontsize=8, color=COLOR_GRAY)
            ax_turnover.set_ylabel("")
            ax_turnover.grid(True, axis="y", color=COLOR_LIGHT_GRAY, linestyle="-", alpha=0.3, linewidth=0.5)
            ax_turnover.spines["top"].set_visible(False)
            ax_turnover.spines["right"].set_visible(False)
            ax_turnover.tick_params(labelsize=8, colors=COLOR_GRAY)
            ax_turnover.set_title("Динамика коэффициента текучести, %", fontsize=12, fontweight="normal", pad=8)

            logger.debug("Сохранение листа 2 в PDF...")
            pdf.savefig(fig2, dpi=150)
            plt.close(fig2)
            logger.debug("Лист 2 сохранен")

        # Проверяем, что файл создан
        if os.path.exists(report_filename):
            file_size = os.path.getsize(report_filename)
            logger.info("=" * 80)
            logger.info("PDF-ОТЧЕТ УСПЕШНО СОЗДАН")
            logger.info("=" * 80)
            logger.info(f"Файл: {report_filename}")
            logger.info(f"Размер файла: {file_size} байт ({file_size/1024:.2f} KB)")
            logger.info(f"Количество листов: 2")
            logger.info(f"  - Лист 1: Общие HR-показатели")
            logger.info(f"  - Лист 2: HR-аналитика ({current_month_name} {TARGET_YEAR})")
            logger.info("=" * 80)
        else:
            logger.error(f"Файл не был создан: {report_filename}")
            raise FileNotFoundError(f"PDF файл не был создан: {report_filename}")
    
    except Exception as e:
        logger.error(f"Ошибка при создании PDF: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        raise
    
    return report_filename


# Запуск функции только при прямом выполнении скрипта
if __name__ == "__main__":
    generate_report()
