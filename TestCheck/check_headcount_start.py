import pandas as pd
from datetime import datetime

DATA_FILE_PATH = r"C:\Users\hellt\Downloads\dataEmployees.xlsx"

# Загрузка данных
df_main_raw = pd.read_excel(DATA_FILE_PATH, sheet_name=0, header=2)
df_term_raw = pd.read_excel(DATA_FILE_PATH, sheet_name=2, header=0)

# Нормализация
df_main = df_main_raw.copy()
df_main["hire_date"] = pd.to_datetime(df_main["Дата трудоустройства"], errors="coerce")
df_main["termination_date_hr"] = pd.NaT
df_main["ФИО_clean"] = df_main["ФИО"]

df_term = df_term_raw.copy()
df_term["hire_date"] = pd.to_datetime(df_term["Дата трудоустройства"], errors="coerce")
df_term["termination_date"] = pd.to_datetime(df_term["Дата увольнения"], errors="coerce")
df_term["ФИО_clean"] = df_term["ФИО"]

# Объединенный датафрейм
df_all = pd.concat([
    pd.DataFrame({
        "ФИО": df_main["ФИО_clean"],
        "hire_date": df_main["hire_date"],
        "termination_date": df_main["termination_date_hr"],
    }),
    pd.DataFrame({
        "ФИО": df_term["ФИО_clean"],
        "hire_date": df_term["hire_date"],
        "termination_date": df_term["termination_date"],
    }),
], ignore_index=True)

df_all = df_all.drop_duplicates(subset=["ФИО", "hire_date"], keep="first")

print("=== ПРОВЕРКА ЧИСЛЕННОСТИ НА РАЗНЫЕ ДАТЫ ===\n")

# Проверяем разные даты
dates_to_check = [
    ("31.12.2024 23:59", datetime(2024, 12, 31, 23, 59)),
    ("01.01.2025 00:00", datetime(2025, 1, 1, 0, 0)),
    ("01.01.2025 23:59", datetime(2025, 1, 1, 23, 59)),
    ("30.11.2025", datetime(2025, 11, 30)),
]

for label, check_date in dates_to_check:
    count = df_all[
        (df_all["hire_date"] <= check_date)
        & (df_all["termination_date"].isna() | (df_all["termination_date"] > check_date))
    ].shape[0]
    print(f"Численность на {label}: {count}")

# Проверяем увольнения в январе 2025
jan_start = datetime(2025, 1, 1)
jan_end = datetime(2025, 1, 31, 23, 59)

jan_terminations = df_all[
    (df_all["termination_date"].notna())
    & (df_all["termination_date"] >= jan_start)
    & (df_all["termination_date"] <= jan_end)
]

print(f"\nУволено в январе 2025: {len(jan_terminations)}")

# Принято в январе 2025
jan_hires = df_all[
    (df_all["hire_date"].notna())
    & (df_all["hire_date"] >= jan_start)
    & (df_all["hire_date"] <= jan_end)
    & (df_all["termination_date"].isna() | (df_all["termination_date"] > jan_end))
]

print(f"Принято в январе 2025: {len(jan_hires)}")

# Рекомендуемый расчет
year_start_date = datetime(2024, 12, 31, 23, 59, 59)  # Конец 2024 = начало 2025
year_end_date = datetime(2025, 11, 30, 23, 59, 59)

headcount_start = df_all[
    (df_all["hire_date"] <= year_start_date)
    & (df_all["termination_date"].isna() | (df_all["termination_date"] > year_start_date))
].shape[0]

headcount_end = df_all[
    (df_all["hire_date"] <= year_end_date)
    & (df_all["termination_date"].isna() | (df_all["termination_date"] > year_end_date))
].shape[0]

print(f"\n=== РЕКОМЕНДУЕМЫЙ РАСЧЕТ ===")
print(f"Штат на начало периода (31.12.2024): {headcount_start}")
print(f"Штат на конец периода (30.11.2025): {headcount_end}")
print(f"Средняя численность: {(headcount_start + headcount_end) / 2:.1f}")

# Уволено за период
terminated_ytd = df_term[
    (df_term["termination_date"].notna())
    & (df_term["termination_date"] >= datetime(2025, 1, 1))
    & (df_term["termination_date"] <= datetime(2025, 11, 30))
].shape[0]

avg_headcount = (headcount_start + headcount_end) / 2
turnover = terminated_ytd / avg_headcount * 100

print(f"Уволено в 2025 (до 30.11): {terminated_ytd}")
print(f"Текучесть: {turnover:.2f}%")

# Сохраняем
with open("headcount_check.txt", "w", encoding="utf-8") as f:
    f.write(f"Штат на начало периода (31.12.2024): {headcount_start}\n")
    f.write(f"Штат на конец периода (30.11.2025): {headcount_end}\n")
    f.write(f"Средняя численность: {(headcount_start + headcount_end) / 2:.1f}\n")
    f.write(f"Уволено в 2025: {terminated_ytd}\n")
    f.write(f"Текучесть: {turnover:.2f}%\n")

print("\n[OK] Результаты сохранены в headcount_check.txt")


