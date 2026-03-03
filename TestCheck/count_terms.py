import pandas as pd
import os
import sys

from datetime import datetime


# Путь к файлу можно передать через переменную окружения или аргумент командной строки
DATA_FILE_PATH = os.getenv("DATA_FILE_PATH") or (sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\hellt\Downloads\dataEmployees.xlsx")

df = pd.read_excel(DATA_FILE_PATH, sheet_name=2, header=0)
df["termination_date"] = pd.to_datetime(df["Дата увольнения"], errors="coerce")
term = df[df["termination_date"].notna()].copy()
term["year"] = term["termination_date"].dt.year
term["month"] = term["termination_date"].dt.month

print("termination_date notna:", term.shape[0])
print("missing termination_date:", df["termination_date"].isna().sum())
print("term in 2025:", (term["year"] == 2025).sum())
print("by year:", term["year"].value_counts().sort_index().to_dict())
print("2025 months:", term[term["year"] == 2025]["month"].value_counts().sort_index().to_dict())

# Проверим лист 1 (header=2) — если там тоже есть увольнения
try:
    df1 = pd.read_excel(DATA_FILE_PATH, sheet_name=1, header=2)
    if "Дата увольнения" in df1.columns:
        df1["termination_date"] = pd.to_datetime(df1["Дата увольнения"], errors="coerce")
        term1 = df1[df1["termination_date"].notna()].copy()
        term1["year"] = term1["termination_date"].dt.year
        print("\n[Sheet 1] termination_date notna:", term1.shape[0])
        print("[Sheet 1] term in 2025:", (term1["year"] == 2025).sum())
        print("[Sheet 1] by year:", term1["year"].value_counts().sort_index().to_dict())
    else:
        print("\n[Sheet 1] Столбец 'Дата увольнения' не найден")
except Exception as e:
    print("\n[Sheet 1] Ошибка чтения:", e)

