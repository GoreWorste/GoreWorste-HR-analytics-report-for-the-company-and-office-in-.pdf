import pandas as pd
from datetime import datetime

DATA_FILE_PATH = r"C:\Users\hellt\Downloads\dataEmployees.xlsx"

# Загрузка данных
df_main_raw = pd.read_excel(DATA_FILE_PATH, sheet_name=0, header=2)
df_term_raw = pd.read_excel(DATA_FILE_PATH, sheet_name=2, header=0)

now = datetime(2025, 11, 30)

# Нормализация
df_main = df_main_raw.copy()
df_main["hire_date"] = pd.to_datetime(df_main["Дата трудоустройства"], errors="coerce")
df_main["termination_date_hr"] = pd.NaT
df_main["birth_date"] = pd.to_datetime(df_main["Дата рождения"], errors="coerce")
df_main["department"] = df_main["ОтделФакт"]

df_term = df_term_raw.copy()
df_term["hire_date"] = pd.to_datetime(df_term["Дата трудоустройства"], errors="coerce")
df_term["termination_date"] = pd.to_datetime(df_term["Дата увольнения"], errors="coerce")
df_term["birth_date"] = pd.to_datetime(df_term["Дата рождения"], errors="coerce")
df_term["department"] = df_term["ОтделФакт"]

# Объединенный датафрейм
df_all = pd.concat([
    pd.DataFrame({
        "ФИО": df_main["ФИО"],
        "hire_date": df_main["hire_date"],
        "termination_date": df_main["termination_date_hr"],
        "birth_date": df_main["birth_date"],
        "department": df_main["department"],
    }),
    pd.DataFrame({
        "ФИО": df_term["ФИО"],
        "hire_date": df_term["hire_date"],
        "termination_date": df_term["termination_date"],
        "birth_date": df_term["birth_date"],
        "department": df_term["department"],
    }),
], ignore_index=True)

df_all = df_all.drop_duplicates(subset=["ФИО", "hire_date"], keep="first")

print("=== РАСЧЕТ ТЕКУЧЕСТИ ЗА 2025 ГОД ===\n")

# Численность на начало 2025 года (1 января 2025)
year_start = datetime(2025, 1, 1)
employees_start_2025 = df_all[
    (df_all["hire_date"] <= year_start)
    & (df_all["termination_date"].isna() | (df_all["termination_date"] > year_start))
].shape[0]

print(f"1. Численность на 01.01.2025: {employees_start_2025}")

# Численность на конец ноября 2025 (30.11.2025)
employees_end_nov = df_all[
    (df_all["hire_date"] <= now)
    & (df_all["termination_date"].isna() | (df_all["termination_date"] > now))
].shape[0]

print(f"2. Численность на 30.11.2025: {employees_end_nov}")

# Средняя численность
avg_headcount = (employees_start_2025 + employees_end_nov) / 2
print(f"3. Средняя численность: {avg_headcount:.1f}")

# Принято и уволено в 2025
year_end = now

hired_2025 = df_main[
    (df_main["hire_date"].notna())
    & (df_main["hire_date"] >= year_start)
    & (df_main["hire_date"] <= year_end)
].shape[0]

terminated_2025 = df_term[
    (df_term["termination_date"].notna())
    & (df_term["termination_date"] >= year_start)
    & (df_term["termination_date"] <= year_end)
].shape[0]

print(f"\n4. Принято в 2025: {hired_2025}")
print(f"5. Уволено в 2025: {terminated_2025}")

# Проверка баланса
balance_check = employees_start_2025 + hired_2025 - terminated_2025
print(f"\n6. Проверка баланса:")
print(f"   {employees_start_2025} (начало) + {hired_2025} (принято) - {terminated_2025} (уволено) = {balance_check}")
print(f"   Фактически на конец: {employees_end_nov}")
print(f"   Разница: {balance_check - employees_end_nov}")

# ТЕКУЩАЯ формула (из кода)
total_employees = df_main["ФИО"].notna().sum()
turnover_current = terminated_2025 / (total_employees + terminated_2025) * 100

print(f"\n=== ФОРМУЛЫ РАСЧЕТА ТЕКУЧЕСТИ ===\n")
print(f"ТЕКУЩАЯ формула (из кода):")
print(f"  {terminated_2025} / ({total_employees} + {terminated_2025}) * 100 = {turnover_current:.2f}%")
print(f"  Проблема: использует текущую численность ({total_employees}), а не начальную")

# ПРАВИЛЬНАЯ формула 1: от численности на начало года
turnover_from_start = terminated_2025 / employees_start_2025 * 100
print(f"\nВариант 1 - от численности на начало года:")
print(f"  {terminated_2025} / {employees_start_2025} * 100 = {turnover_from_start:.2f}%")

# ПРАВИЛЬНАЯ формула 2: от средней численности
turnover_from_avg = terminated_2025 / avg_headcount * 100
print(f"\nВариант 2 - от средней численности (РЕКОМЕНДУЕТСЯ):")
print(f"  {terminated_2025} / {avg_headcount:.1f} * 100 = {turnover_from_avg:.2f}%")

# Сохраняем результаты
with open("turnover_analysis.txt", "w", encoding="utf-8") as f:
    f.write("АНАЛИЗ ТЕКУЧЕСТИ ЗА 2025 ГОД\n")
    f.write("="*60 + "\n\n")
    f.write(f"Численность на 01.01.2025: {employees_start_2025}\n")
    f.write(f"Численность на 30.11.2025: {employees_end_nov}\n")
    f.write(f"Средняя численность: {avg_headcount:.1f}\n\n")
    f.write(f"Принято в 2025: {hired_2025}\n")
    f.write(f"Уволено в 2025: {terminated_2025}\n\n")
    f.write(f"ТЕКУЩАЯ формула: {turnover_current:.2f}%\n")
    f.write(f"Вариант 1 (от начальной): {turnover_from_start:.2f}%\n")
    f.write(f"Вариант 2 (от средней): {turnover_from_avg:.2f}%\n")

print("\n[OK] Результаты сохранены в turnover_analysis.txt")


