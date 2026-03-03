import pandas as pd
from datetime import datetime

DATA_FILE_PATH = r"C:\Users\hellt\Downloads\dataEmployees.xlsx"

# Загрузка данных
print("Загрузка данных из Excel...")
df_term_raw = pd.read_excel(DATA_FILE_PATH, sheet_name=2, header=0)

print(f"\nВсего записей в таблице увольнений: {len(df_term_raw)}")
print(f"\nСтолбцы: {list(df_term_raw.columns)}")

# Нормализация дат
df_term = df_term_raw.copy()
df_term["hire_date"] = pd.to_datetime(df_term["Дата трудоустройства"], errors="coerce")
df_term["termination_date"] = pd.to_datetime(df_term["Дата увольнения"], errors="coerce")

# Проверяем даты увольнения
print(f"\n=== АНАЛИЗ ДАТ УВОЛЬНЕНИЯ ===")
print(f"Записей с датой увольнения: {df_term['termination_date'].notna().sum()}")
print(f"Записей БЕЗ даты увольнения: {df_term['termination_date'].isna().sum()}")

# Статистика по годам
print(f"\n=== УВОЛЬНЕНИЯ ПО ГОДАМ ===")
term_with_dates = df_term[df_term["termination_date"].notna()].copy()
term_with_dates["year"] = term_with_dates["termination_date"].dt.year
print(term_with_dates["year"].value_counts().sort_index())

# За 2025 год
year_start = datetime(2025, 1, 1)
year_end = datetime(2025, 12, 31)

term_2025 = df_term[
    (df_term["termination_date"].notna())
    & (df_term["termination_date"] >= year_start)
    & (df_term["termination_date"] <= year_end)
]

print(f"\n=== УВОЛЬНЕНИЯ В 2025 ГОДУ ===")
print(f"Всего уволено в 2025: {len(term_2025)}")

# По месяцам 2025
print(f"\nПо месяцам 2025 года:")
if not term_2025.empty:
    term_2025_copy = term_2025.copy()
    term_2025_copy["month"] = term_2025_copy["termination_date"].dt.month
    month_names = {1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 
                   5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
                   9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"}
    
    for month in range(1, 13):
        count = (term_2025_copy["month"] == month).sum()
        if count > 0:
            print(f"  {month_names[month]}: {count}")

# Показываем первые и последние записи 2025
print(f"\n=== ПЕРВЫЕ 5 УВОЛЬНЕНИЙ 2025 ===")
if not term_2025.empty:
    for idx, row in term_2025.head(5).iterrows():
        print(f"  {row['ФИО']}: {row['termination_date'].strftime('%d.%m.%Y')}")

print(f"\n=== ПОСЛЕДНИЕ 5 УВОЛЬНЕНИЙ 2025 ===")
if not term_2025.empty:
    for idx, row in term_2025.tail(5).iterrows():
        print(f"  {row['ФИО']}: {row['termination_date'].strftime('%d.%m.%Y')}")

# Проверяем ноябрь отдельно
nov_start = datetime(2025, 11, 1)
nov_end = datetime(2025, 11, 30)

term_nov = df_term[
    (df_term["termination_date"].notna())
    & (df_term["termination_date"] >= nov_start)
    & (df_term["termination_date"] <= nov_end)
]

print(f"\n=== НОЯБРЬ 2025 ===")
print(f"Уволено в ноябре 2025: {len(term_nov)}")
if not term_nov.empty:
    for idx, row in term_nov.iterrows():
        print(f"  {row['ФИО']}: {row['termination_date'].strftime('%d.%m.%Y')}")

# Сохраняем результаты
with open("terminations_check.txt", "w", encoding="utf-8") as f:
    f.write(f"Всего записей в таблице увольнений: {len(df_term_raw)}\n")
    f.write(f"Записей с датой увольнения: {df_term['termination_date'].notna().sum()}\n")
    f.write(f"Уволено в 2025 году: {len(term_2025)}\n")
    f.write(f"Уволено в ноябре 2025: {len(term_nov)}\n")

print("\n✓ Результаты сохранены в terminations_check.txt")


