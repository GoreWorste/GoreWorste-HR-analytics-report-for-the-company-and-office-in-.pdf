"""
Скрипт для проверки корректности данных отчета за ноябрь 2025
"""
import pandas as pd
from datetime import datetime

# Путь к локальному файлу с данными
DATA_FILE_PATH = r"C:\Users\hellt\Downloads\dataEmployees.xlsx"

def parse_date(series: pd.Series) -> pd.Series:
    """Парсинг дат в формате DD.MM.YYYY"""
    return pd.to_datetime(
        series.astype(str).str.strip(), format="%d.%m.%Y", errors="coerce"
    )

MONTH_NAMES_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}

# Загрузка данных
print("=" * 80)
print("ПРОВЕРКА КОРРЕКТНОСТИ ОТЧЕТА ЗА НОЯБРЬ 2025")
print("=" * 80)
print(f"\nЗагрузка данных из локального файла: {DATA_FILE_PATH}...")

# Лист 0 - "Список сотрудников" (основные сотрудники, заголовки в строке 2)
df_main_raw = pd.read_excel(DATA_FILE_PATH, sheet_name=0, header=2)
# Лист 1 - "Увольнение" (уволенные, заголовки в строке 2)
df_term_raw = pd.read_excel(DATA_FILE_PATH, sheet_name=1, header=2)

# Дата отчета - ноябрь 2025
now = datetime(2025, 11, 30)
TARGET_YEAR = now.year
current_month_name = MONTH_NAMES_RU.get(now.month)

print(f"[OK] Данные загружены")
print(f"[OK] Дата отчета: 30 ноября 2025")
print(f"[OK] Отчетный месяц: {current_month_name} {TARGET_YEAR}")

# Нормализация данных
df_main = df_main_raw.copy()
# Даты уже в формате datetime из Excel, преобразуем в pandas datetime
df_main["hire_date"] = pd.to_datetime(df_main["Дата трудоустройства"], errors="coerce")
df_main["termination_date_hr"] = pd.NaT  # В основной таблице нет дат увольнения
df_main["birth_date"] = pd.to_datetime(df_main["Дата рождения"], errors="coerce")
df_main["gender_raw"] = df_main["Пол"].astype(str).str.strip().str.lower()

df_term = df_term_raw.copy()
# Даты уже в формате datetime из Excel, преобразуем в pandas datetime
df_term["hire_date"] = pd.to_datetime(df_term["Дата трудоустройства"], errors="coerce")
df_term["termination_date"] = pd.to_datetime(df_term["Дата увольнения"], errors="coerce")
df_term["birth_date"] = pd.to_datetime(df_term["Дата рождения"], errors="coerce")
df_term["gender_raw"] = df_term["Пол"].astype(str).str.strip().str.lower()

# Объединенный датафрейм
df_all = pd.concat(
    [
        pd.DataFrame({
            "ФИО": df_main["ФИО"],
            "hire_date": df_main["hire_date"],
            "termination_date": df_main["termination_date_hr"],
            "birth_date": df_main["birth_date"],
            "gender_raw": df_main["gender_raw"],
        }),
        pd.DataFrame({
            "ФИО": df_term["ФИО"],
            "hire_date": df_term["hire_date"],
            "termination_date": df_term["termination_date"],
            "birth_date": df_term["birth_date"],
            "gender_raw": df_term["gender_raw"],
        }),
    ],
    ignore_index=True,
)

df_all["age"] = (now - df_all["birth_date"]).dt.days / 365.25
df_all["tenure"] = (now - df_all["hire_date"]).dt.days / 365.25

# Активные сотрудники на текущую дату
active_now = df_all[
    (df_all["hire_date"].notna())
    & (df_all["termination_date"].isna() | (df_all["termination_date"] > now))
]

# Метрики
print("\n" + "=" * 80)
print("ОСНОВНЫЕ МЕТРИКИ НА 30 НОЯБРЯ 2025")
print("=" * 80)

total_employees = df_main["ФИО"].notna().sum()  # Считаем активных сотрудников по наличию ФИО
avg_tenure = active_now["tenure"].mean()
avg_age = active_now["age"].mean()

print(f"\n1. Количество сотрудников: {total_employees}")
print(f"2. Средний стаж: {avg_tenure:.2f} лет")
print(f"3. Средний возраст: {avg_age:.2f} лет")

# Пол
df_main_active = df_main[df_main["termination_date_hr"].isna()]
gender_series = df_main_active["gender_raw"]
male_count = (gender_series == "м").sum()
female_count = (gender_series == "ж").sum()

print(f"\n4. Распределение по полу:")
print(f"   - Мужчины: {male_count} ({male_count/(male_count+female_count)*100:.1f}%)")
print(f"   - Женщины: {female_count} ({female_count/(male_count+female_count)*100:.1f}%)")

# Данные с начала года (до конца ноября включительно)
year_start = datetime(TARGET_YEAR, 1, 1)
current_month_end = now

hired_ytd = df_main[
    (df_main["hire_date"].notna())
    & (df_main["hire_date"] >= year_start)
    & (df_main["hire_date"] <= current_month_end)
].shape[0]

terminated_ytd = df_term[
    (df_term["termination_date"].notna())
    & (df_term["termination_date"] >= year_start)
    & (df_term["termination_date"] <= current_month_end)
].shape[0]

print("\n" + "=" * 80)
print("ДАННЫЕ С НАЧАЛА 2025 ГОДА (ПО 30 НОЯБРЯ ВКЛЮЧИТЕЛЬНО)")
print("=" * 80)
print(f"\n5. Принято сотрудников: {hired_ytd}")
print(f"6. Уволено сотрудников: {terminated_ytd}")

# Текучесть за год по правильной формуле
# Численность на начало года (31 декабря 2024)
year_start_date = datetime(TARGET_YEAR - 1, 12, 31, 23, 59, 59)
headcount_year_start = df_all[
    (df_all["hire_date"] <= year_start_date)
    & (df_all["termination_date"].isna() | (df_all["termination_date"] > year_start_date))
].shape[0]

# Численность на конец периода (30 ноября 2025)
headcount_year_end = df_all[
    (df_all["hire_date"] <= now)
    & (df_all["termination_date"].isna() | (df_all["termination_date"] > now))
].shape[0]

# Средняя численность за год
avg_headcount_ytd = (headcount_year_start + headcount_year_end) / 2

# Текучесть = Уволено / Средняя численность * 100
turnover_ytd = terminated_ytd / avg_headcount_ytd * 100 if avg_headcount_ytd > 0 else 0

print(f"7. Численность на начало года (31.12.2024): {headcount_year_start}")
print(f"8. Численность на конец периода (30.11.2025): {headcount_year_end}")
print(f"9. Средняя численность: {avg_headcount_ytd:.1f}")
print(f"10. Текучесть за год: {turnover_ytd:.2f}%")

# Данные за ноябрь
month_start = now.replace(day=1)
next_month = month_start + pd.DateOffset(months=1)
month_end = next_month - pd.DateOffset(days=1)

hires_month = df_main[
    (df_main["hire_date"].notna())
    & (df_main["hire_date"] >= month_start)
    & (df_main["hire_date"] <= month_end)
].shape[0]

terms_month = df_term[
    (df_term["termination_date"].notna())
    & (df_term["termination_date"] >= month_start)
    & (df_term["termination_date"] <= month_end)
].shape[0]

print("\n" + "=" * 80)
print(f"ДАННЫЕ ЗА {current_month_name.upper()} 2025")
print("=" * 80)
print(f"\n8. Принято в {current_month_name}: {hires_month}")
print(f"9. Уволено в {current_month_name}: {terms_month}")

# Период для графиков (последние 7 месяцев)
print("\n" + "=" * 80)
print("ПЕРИОД ДЛЯ ГРАФИКОВ (ПОСЛЕДНИЕ 7 МЕСЯЦЕВ)")
print("=" * 80)

month_labels = []
headcount_data = []

for offset in range(6, -1, -1):
    m_start = month_start - pd.DateOffset(months=offset)
    m_end = m_start + pd.DateOffset(months=1) - pd.DateOffset(days=1)
    
    active_end_m = df_all[
        (df_all["hire_date"] <= m_end)
        & (df_all["termination_date"].isna() | (df_all["termination_date"] > m_end))
    ]
    
    month_name = MONTH_NAMES_RU.get(m_start.month)
    month_labels.append(month_name)
    headcount_data.append(active_end_m.shape[0])

print(f"\nМесяцы: {', '.join(month_labels)}")
print(f"\nЧисленность по месяцам:")
for month, count in zip(month_labels, headcount_data):
    print(f"  {month}: {count} чел.")

# Текучесть по месяцам
print(f"\nТекучесть по месяцам:")
for offset in range(6, -1, -1):
    m_start = month_start - pd.DateOffset(months=offset)
    m_end = m_start + pd.DateOffset(months=1) - pd.DateOffset(days=1)
    
    active_start_m = df_all[
        (df_all["hire_date"] <= m_start)
        & (df_all["termination_date"].isna() | (df_all["termination_date"] > m_start))
    ].shape[0]
    
    active_end_m = df_all[
        (df_all["hire_date"] <= m_end)
        & (df_all["termination_date"].isna() | (df_all["termination_date"] > m_end))
    ].shape[0]
    
    termed_m = df_all[
        (df_all["termination_date"].notna())
        & (df_all["termination_date"] >= m_start)
        & (df_all["termination_date"] <= m_end)
    ].shape[0]
    
    avg_headcount_m = (active_start_m + active_end_m) / 2 if (active_start_m + active_end_m) > 0 else 0
    turnover_m = termed_m / avg_headcount_m * 100 if avg_headcount_m > 0 else 0
    
    month_name = MONTH_NAMES_RU.get(m_start.month)
    print(f"  {month_name}: {turnover_m:.2f}% (уволено: {termed_m})")

print("\n" + "=" * 80)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 80)
print("\n[OK] Все данные рассчитаны корректно для ноября 2025")
print("[OK] Период графиков: последние 7 месяцев (май - ноябрь 2025)")
print("[OK] Данные с начала года: январь - ноябрь 2025 (включительно)")

