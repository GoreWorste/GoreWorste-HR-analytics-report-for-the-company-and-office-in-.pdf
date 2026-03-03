import pandas as pd

DATA_FILE_PATH = r"C:\Users\hellt\Downloads\dataEmployees.xlsx"

xl = pd.ExcelFile(DATA_FILE_PATH)
print("Sheets:", xl.sheet_names)

for name in xl.sheet_names:
    for header in [0, 1, 2]:
        try:
            df = pd.read_excel(DATA_FILE_PATH, sheet_name=name, header=header, nrows=5)
        except Exception:
            continue
        cols = set(df.columns.astype(str))
        if {"ФИО", "Дата увольнения"} <= cols:
            print(f"Sheet '{name}' header={header} -> Увольнения. First cols: {list(df.columns[:8])}")
        if {"ФИО", "Дата трудоустройства"} <= cols and "Дата увольнения" not in cols:
            print(f"Sheet '{name}' header={header} -> Список сотрудников. First cols: {list(df.columns[:8])}")


