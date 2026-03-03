import pandas as pd
import os
import sys

# Путь к файлу
DATA_FILE_PATH = os.getenv("DATA_FILE_PATH") or (sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\hellt\Downloads\dataEmployees.xlsx")

print("=" * 80)
print("АНАЛИЗ СТРУКТУРЫ EXCEL ФАЙЛА")
print("=" * 80)
print(f"\nФайл: {DATA_FILE_PATH}")

# Проверяем существование файла
if not os.path.exists(DATA_FILE_PATH):
    print(f"\nОШИБКА: Файл не найден: {DATA_FILE_PATH}")
    sys.exit(1)

# Загружаем Excel файл
xl = pd.ExcelFile(DATA_FILE_PATH)
print(f"\nВсего листов в файле: {len(xl.sheet_names)}")
print(f"Названия листов: {xl.sheet_names}")

print("\n" + "=" * 80)
print("ПОДРОБНЫЙ АНАЛИЗ КАЖДОГО ЛИСТА")
print("=" * 80)

for idx, sheet_name in enumerate(xl.sheet_names):
    print(f"\n{'='*60}")
    print(f"ЛИСТ #{idx}: '{sheet_name}'")
    print(f"{'='*60}")
    
    # Пробуем разные варианты header
    for header_idx in [0, 1, 2]:
        try:
            df = pd.read_excel(DATA_FILE_PATH, sheet_name=sheet_name, header=header_idx)
            cols = list(df.columns)
            
            print(f"\n  [header={header_idx}]")
            print(f"    Строк: {len(df)}")
            print(f"    Столбцов: {len(cols)}")
            print(f"    Первые 10 столбцов: {cols[:10]}")
            
            # Проверяем ключевые столбцы
            if "ФИО" in cols:
                non_empty_fio = df["ФИО"].notna().sum()
                print(f"    + Столбец 'ФИО': {non_empty_fio} заполненных записей")
            
            if "Дата трудоустройства" in cols:
                non_empty_hire = df["Дата трудоустройства"].notna().sum()
                print(f"    + Столбец 'Дата трудоустройства': {non_empty_hire} заполненных записей")
            
            if "Дата увольнения" in cols:
                non_empty_term = df["Дата увольнения"].notna().sum()
                print(f"    + Столбец 'Дата увольнения': {non_empty_term} заполненных записей")
                
                # Если есть даты увольнения, анализируем их
                if non_empty_term > 0:
                    df_term_copy = df.copy()
                    df_term_copy["termination_date_parsed"] = pd.to_datetime(
                        df_term_copy["Дата увольнения"], errors="coerce"
                    )
                    term_2025 = df_term_copy[
                        (df_term_copy["termination_date_parsed"].notna())
                        & (df_term_copy["termination_date_parsed"].dt.year == 2025)
                    ]
                    print(f"    + Увольнений в 2025 году: {len(term_2025)}")
                    
                    # Показываем пример ФИО
                    if len(term_2025) > 0 and "ФИО" in df_term_copy.columns:
                        sample_fio = term_2025["ФИО"].dropna().head(3).tolist()
                        print(f"    + Пример ФИО уволенных: {sample_fio}")
            
            if "ОтделФакт" in cols or "Отдел" in cols:
                dept_col = "ОтделФакт" if "ОтделФакт" in cols else "Отдел"
                unique_depts = df[dept_col].dropna().nunique()
                print(f"    + Уникальных отделов: {unique_depts}")
                # Показываем примеры отделов
                sample_depts = df[dept_col].dropna().unique()[:5].tolist()
                print(f"    + Примеры отделов: {sample_depts}")
                
        except Exception as e:
            print(f"\n  [header={header_idx}] ОШИБКА: {e}")
            continue

print("\n" + "=" * 80)
print("РЕЗЮМЕ")
print("=" * 80)

# Определяем листы с увольнениями
print("\nЛисты с данными об увольнениях:")
for idx, sheet_name in enumerate(xl.sheet_names):
    for header_idx in [0, 1, 2]:
        try:
            df = pd.read_excel(DATA_FILE_PATH, sheet_name=sheet_name, header=header_idx)
            if "Дата увольнения" in df.columns:
                term_count = df["Дата увольнения"].notna().sum()
                if term_count > 0:
                    print(f"  + Лист #{idx} '{sheet_name}' (header={header_idx}): {term_count} увольнений")
        except:
            continue

print("\n" + "=" * 80)

