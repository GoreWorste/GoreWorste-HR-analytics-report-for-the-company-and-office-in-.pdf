import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

print("=" * 80)
print("ПРОВЕРКА ЦИФР В HR-ОТЧЕТЕ")
print("=" * 80)

# URL файла
DATA_FILE_URL = "https://storage.yandexcloud.net/sds-hr/sds-hr/%D0%A0%D0%B5%D0%B5%D1%81%D1%82%D1%80_%D1%81%D0%BE%D1%82%D1%80%D1%83%D0%B4%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2.xlsx"

# Загружаем данные
print("\nЗагрузка данных из URL...")
response = requests.get(DATA_FILE_URL, timeout=30)
response.raise_for_status()
data_source = BytesIO(response.content)

# Загружаем листы
print("\nЗагрузка листов...")
df_main = pd.read_excel(data_source, sheet_name="Список сотрудников", header=2)
df_term1 = pd.read_excel(data_source, sheet_name="Увольнение", header=2)
df_term2 = pd.read_excel(data_source, sheet_name=2, header=0)  # "Увольнения Склад и Торги"

print(f"Лист 'Список сотрудников': {len(df_main)} строк")
print(f"Лист 'Увольнение': {len(df_term1)} строк")
print(f"Лист 'Увольнения Склад и Торги': {len(df_term2)} строк")

# Целевой год и месяц
TARGET_YEAR = 2025
TARGET_MONTH = 12  # Декабрь
year_start = datetime(TARGET_YEAR, 1, 1)
year_end = datetime(TARGET_YEAR, 12, 31)
month_start = datetime(TARGET_YEAR, TARGET_MONTH, 1)
month_end = datetime(TARGET_YEAR, TARGET_MONTH, 31)

print(f"\nПериод анализа: {TARGET_YEAR} год, {TARGET_MONTH} месяц")

# Фильтруем данные (исключаем служебные строки)
service_keywords = ["итого", "всего", "сумма", "total", "summary", "итог", "заголовок", "header"]
df_main_clean = df_main[
    (df_main["ФИО"].notna()) & 
    (~df_main["ФИО"].astype(str).str.strip().str.lower().isin(service_keywords))
].copy()

df_term1_clean = df_term1[
    (df_term1["ФИО"].notna()) & 
    (~df_term1["ФИО"].astype(str).str.strip().str.lower().isin(service_keywords))
].copy()

df_term2_clean = df_term2[
    (df_term2["ФИО"].notna()) & 
    (~df_term2["ФИО"].astype(str).str.strip().str.lower().isin(service_keywords))
].copy()

print("\n" + "=" * 80)
print("МЕТРИКА 1: ЧИСЛЕННОСТЬ СОТРУДНИКОВ (на конец декабря 2025)")
print("=" * 80)
total_employees = len(df_main_clean)
print(f"Всего сотрудников: {total_employees}")

print("\n" + "=" * 80)
print("МЕТРИКА 2: ПРИНЯТО С НАЧАЛА ГОДА")
print("=" * 80)

df_main_clean["hire_date"] = pd.to_datetime(df_main_clean["Дата трудоустройства"], errors="coerce")
hired_ytd = df_main_clean[
    (df_main_clean["hire_date"].notna()) &
    (df_main_clean["hire_date"] >= year_start) &
    (df_main_clean["hire_date"] <= year_end)
].shape[0]
print(f"Принято в {TARGET_YEAR} году: {hired_ytd}")

print("\n" + "=" * 80)
print("МЕТРИКА 3: УВОЛЕНО С НАЧАЛА ГОДА (ИЗ ОБОИХ ЛИСТОВ)")
print("=" * 80)

# Лист 1: Увольнение
df_term1_clean["termination_date"] = pd.to_datetime(df_term1_clean["Дата увольнения"], errors="coerce")
terminated_ytd_1 = df_term1_clean[
    (df_term1_clean["termination_date"].notna()) &
    (df_term1_clean["termination_date"] >= year_start) &
    (df_term1_clean["termination_date"] <= year_end)
].shape[0]
print(f"Лист 'Увольнение': {terminated_ytd_1} увольнений в {TARGET_YEAR}")

# Лист 2: Увольнения Склад и Торги
df_term2_clean["termination_date"] = pd.to_datetime(df_term2_clean["Дата увольнения"], errors="coerce")
terminated_ytd_2 = df_term2_clean[
    (df_term2_clean["termination_date"].notna()) &
    (df_term2_clean["termination_date"] >= year_start) &
    (df_term2_clean["termination_date"] <= year_end)
].shape[0]
print(f"Лист 'Увольнения Склад и Торги': {terminated_ytd_2} увольнений в {TARGET_YEAR}")

# Объединяем увольнения
df_term_all = pd.concat([df_term1_clean, df_term2_clean], ignore_index=True)
df_term_all["termination_date"] = pd.to_datetime(df_term_all["Дата увольнения"], errors="coerce")

# Убираем дубликаты
before_dedup = df_term_all.shape[0]
df_term_all_dedup = df_term_all.drop_duplicates(subset=["ФИО", "termination_date"], keep="first")
after_dedup = df_term_all_dedup.shape[0]
if before_dedup != after_dedup:
    print(f"\nНайдено дубликатов: {before_dedup - after_dedup}")

terminated_ytd_total = df_term_all_dedup[
    (df_term_all_dedup["termination_date"].notna()) &
    (df_term_all_dedup["termination_date"] >= year_start) &
    (df_term_all_dedup["termination_date"] <= year_end)
].shape[0]

print(f"\nИТОГО уволено в {TARGET_YEAR}: {terminated_ytd_total} (после удаления дубликатов)")

print("\n" + "=" * 80)
print("МЕТРИКА 4: ПРИНЯТО ЗА ДЕКАБРЬ")
print("=" * 80)

hired_month = df_main_clean[
    (df_main_clean["hire_date"].notna()) &
    (df_main_clean["hire_date"] >= month_start) &
    (df_main_clean["hire_date"] <= month_end)
].shape[0]
print(f"Принято в декабре {TARGET_YEAR}: {hired_month}")

print("\n" + "=" * 80)
print("МЕТРИКА 5: УВОЛЕНО ЗА ДЕКАБРЬ (ИЗ ОБОИХ ЛИСТОВ)")
print("=" * 80)

terminated_month_1 = df_term1_clean[
    (df_term1_clean["termination_date"].notna()) &
    (df_term1_clean["termination_date"] >= month_start) &
    (df_term1_clean["termination_date"] <= month_end)
].shape[0]
print(f"Лист 'Увольнение': {terminated_month_1} увольнений в декабре")

terminated_month_2 = df_term2_clean[
    (df_term2_clean["termination_date"].notna()) &
    (df_term2_clean["termination_date"] >= month_start) &
    (df_term2_clean["termination_date"] <= month_end)
].shape[0]
print(f"Лист 'Увольнения Склад и Торги': {terminated_month_2} увольнений в декабре")

terminated_month_total = df_term_all_dedup[
    (df_term_all_dedup["termination_date"].notna()) &
    (df_term_all_dedup["termination_date"] >= month_start) &
    (df_term_all_dedup["termination_date"] <= month_end)
].shape[0]

print(f"\nИТОГО уволено в декабре: {terminated_month_total} (после удаления дубликатов)")

print("\n" + "=" * 80)
print("МЕТРИКА 6: ТЕКУЧЕСТЬ ЗА ГОД")
print("=" * 80)

# Численность на начало года (оценка)
headcount_year_end = total_employees
headcount_year_start = headcount_year_end - hired_ytd + terminated_ytd_total
avg_headcount_ytd = (headcount_year_start + headcount_year_end) / 2

turnover_ytd = (terminated_ytd_total / avg_headcount_ytd * 100) if avg_headcount_ytd > 0 else 0

print(f"Численность на начало года (оценка): {headcount_year_start}")
print(f"Численность на конец года: {headcount_year_end}")
print(f"Средняя численность: {avg_headcount_ytd:.2f}")
print(f"Текучесть за год: {turnover_ytd:.2f}%")

print("\n" + "=" * 80)
print("МЕТРИКА 7: ТЕКУЧЕСТЬ ЗА ПЕРИОД (ПОСЛЕДНИЕ 30 ДНЕЙ)")
print("=" * 80)

period_end = datetime(TARGET_YEAR, TARGET_MONTH, 31)
period_start = datetime(TARGET_YEAR, TARGET_MONTH, 1)

# Активные на начало периода
active_period_start = df_main_clean[
    (df_main_clean["hire_date"].notna()) &
    (df_main_clean["hire_date"] <= period_start)
].shape[0]

# Уволенные за период
terminated_period = df_term_all_dedup[
    (df_term_all_dedup["termination_date"].notna()) &
    (df_term_all_dedup["termination_date"] >= period_start) &
    (df_term_all_dedup["termination_date"] <= period_end)
].shape[0]

turnover_period = (terminated_period / active_period_start * 100) if active_period_start > 0 else 0

print(f"Активных сотрудников на начало периода: {active_period_start}")
print(f"Уволено за период: {terminated_period}")
print(f"Текучесть за период: {turnover_period:.2f}%")

print("\n" + "=" * 80)
print("РЕЗЮМЕ")
print("=" * 80)

print("\nЦифры для проверки с отчетом:")
print(f"  1. Численность: {total_employees}")
print(f"  2. Принято с начала года: {hired_ytd}")
print(f"  3. Уволено с начала года: {terminated_ytd_total}")
print(f"  4. Принято за декабрь: {hired_month}")
print(f"  5. Уволено за декабрь: {terminated_month_total}")
print(f"  6. Текучесть за год: {turnover_ytd:.2f}%")
print(f"  7. Текучесть за период: {turnover_period:.2f}%")

print("\n" + "=" * 80)

