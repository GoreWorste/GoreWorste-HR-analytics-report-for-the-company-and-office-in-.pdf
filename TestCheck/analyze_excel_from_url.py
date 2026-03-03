import pandas as pd
import os
import sys
import requests
from io import BytesIO

# URL файла на сервере
DATA_FILE_URL = "https://storage.yandexcloud.net/sds-hr/sds-hr/%D0%A0%D0%B5%D0%B5%D1%81%D1%82%D1%80_%D1%81%D0%BE%D1%82%D1%80%D1%83%D0%B4%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2.xlsx"

print("=" * 80)
print("АНАЛИЗ СТРУКТУРЫ EXCEL ФАЙЛА")
print("=" * 80)

# Загружаем данные
try:
    print(f"\nЗагрузка данных из URL: {DATA_FILE_URL}")
    response = requests.get(DATA_FILE_URL, timeout=30)
    response.raise_for_status()
    file_size = len(response.content)
    print(f"Файл успешно загружен, размер: {file_size} байт ({file_size/1024:.2f} KB)")
    data_source = BytesIO(response.content)
except Exception as e:
    print(f"ОШИБКА при загрузке файла: {e}")
    sys.exit(1)

# Загружаем Excel файл
xl = pd.ExcelFile(data_source)
print(f"\nВсего листов в файле: {len(xl.sheet_names)}")
print(f"Названия листов:")
for idx, name in enumerate(xl.sheet_names):
    print(f"  {idx}: {name}")

print("\n" + "=" * 80)
print("ПОДРОБНЫЙ АНАЛИЗ КАЖДОГО ЛИСТА")
print("=" * 80)

all_termination_sheets = []

for idx, sheet_name in enumerate(xl.sheet_names):
    print(f"\n{'='*60}")
    print(f"ЛИСТ #{idx}: '{sheet_name}'")
    print(f"{'='*60}")
    
    # Пробуем разные варианты header
    for header_idx in [0, 1, 2]:
        try:
            df = pd.read_excel(data_source, sheet_name=sheet_name, header=header_idx)
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
                    
                    # Подсчет увольнений в 2025
                    term_2025 = df_term_copy[
                        (df_term_copy["termination_date_parsed"].notna())
                        & (df_term_copy["termination_date_parsed"].dt.year == 2025)
                    ]
                    print(f"    + Увольнений в 2025 году: {len(term_2025)}")
                    
                    # Сохраняем информацию о листе с увольнениями
                    all_termination_sheets.append({
                        "sheet_idx": idx,
                        "sheet_name": sheet_name,
                        "header": header_idx,
                        "total_terminations": non_empty_term,
                        "terminations_2025": len(term_2025)
                    })
                    
                    # Показываем пример ФИО
                    if len(term_2025) > 0 and "ФИО" in df_term_copy.columns:
                        sample_fio = term_2025["ФИО"].dropna().head(3).tolist()
                        print(f"    + Пример ФИО уволенных: {sample_fio}")
                    
                    # Статистика по месяцам 2025
                    if len(term_2025) > 0:
                        term_2025_copy = term_2025.copy()
                        term_2025_copy["month"] = term_2025_copy["termination_date_parsed"].dt.month
                        month_counts = term_2025_copy["month"].value_counts().sort_index()
                        print(f"    + Увольнения по месяцам 2025:")
                        month_names = {1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 
                                     5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
                                     9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"}
                        for month, count in month_counts.items():
                            print(f"      {month_names.get(month, month)}: {count}")
            
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
print("РЕЗЮМЕ: ЛИСТЫ С УВОЛЬНЕНИЯМИ")
print("=" * 80)

if all_termination_sheets:
    print(f"\nНайдено {len(all_termination_sheets)} листов с данными об увольнениях:")
    for sheet_info in all_termination_sheets:
        print(f"\n  Лист #{sheet_info['sheet_idx']}: '{sheet_info['sheet_name']}'")
        print(f"    Header: {sheet_info['header']}")
        print(f"    Всего увольнений: {sheet_info['total_terminations']}")
        print(f"    Увольнений в 2025: {sheet_info['terminations_2025']}")
else:
    print("\nЛистов с увольнениями не найдено.")

print("\n" + "=" * 80)
print("РЕКОМЕНДАЦИИ")
print("=" * 80)

if len(all_termination_sheets) > 1:
    print("\nВНИМАНИЕ: Обнаружено несколько листов с увольнениями!")
    print("В текущем коде main.py загружается только лист 'Увольнение'.")
    print("Необходимо модифицировать код для загрузки всех листов с увольнениями:")
    for sheet_info in all_termination_sheets:
        if sheet_info['sheet_name'] != "Увольнение":
            print(f"  - Добавить загрузку листа '{sheet_info['sheet_name']}' (header={sheet_info['header']})")
elif len(all_termination_sheets) == 1:
    print("\nОбнаружен только один лист с увольнениями.")
    print("Текущий код должен работать корректно.")
else:
    print("\nЛистов с увольнениями не обнаружено - проверьте структуру файла.")

print("\n" + "=" * 80)

