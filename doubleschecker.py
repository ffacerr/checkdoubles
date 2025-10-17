import streamlit as st
import pandas as pd
import re

def normalize_phone(phone):
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 10:
        return '+1' + digits
    elif len(digits) == 11 and digits.startswith('1'):
        return '+' + digits
    return digits

st.title("🔍 Поиск дублей в выгрузке из CRM")

uploaded_file = st.file_uploader("Загрузите .xlsx файл", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=0)

    # Проверка количества столбцов
    if df.shape[1] < 50:
        st.error("Ошибка: в файле должно быть как минимум 50 столбцов.")
    else:
        # Извлекаем нужные колонки
        df_extracted = pd.DataFrame()
        df_extracted["A"] = df.iloc[:, 0]   # A
        df_extracted["H"] = df.iloc[:, 7]   # H
        df_extracted["D"] = df.iloc[:, 3]   # D
        df_extracted["AU"] = df.iloc[:, 49] # AU
        df_extracted["AX"] = df.iloc[:, 52] # AX
        df_extracted["AX_normalized"] = df_extracted["AX"].apply(normalize_phone)

        duplicates = pd.DataFrame()

        for column, label in [('D', 'D'), ('AU', 'AU'), ('AX_normalized', 'AX (нормализован)')]:
            # Только строки с непустыми значениями в этом столбце
            non_empty = df_extracted[df_extracted[column].notna() & df_extracted[column].ne('')]

            dupes = non_empty[non_empty.duplicated(column, keep=False)].copy()
            if not dupes.empty:
                dupes['Дубликат по'] = label
                dupes['Группа'] = dupes[column]  # Для сортировки
                duplicates = pd.concat([duplicates, dupes])

        if duplicates.empty:
            st.success("✅ Дубликаты не найдены")
        else:
            duplicates = duplicates.drop_duplicates(subset=["A", "D", "AU", "AX_normalized", "Дубликат по"])
            duplicates = duplicates.sort_values(by=["Дубликат по", "Группа"])

            st.warning(f"🔁 Найдено дубликатов: {len(duplicates)} строк")
            st.dataframe(duplicates[["A", "H", "D", "AU", "AX", "AX_normalized", "Дубликат по"]])

            csv = duplicates.to_csv(index=False)
            st.download_button("📥 Скачать CSV", csv, "дубликаты.csv", "text/csv")
