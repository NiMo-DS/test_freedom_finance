import pandas as pd
import streamlit as st

def load_data(uploaded_file):
    """
    Загружает CSV или XLSX файл и возвращает pandas DataFrame.
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Неподдерживаемый формат файла. Пожалуйста, загрузите файл CSV или Excel.")
            return None
        return df
    except Exception as e:
        st.error(f"Ошибка при прочтении файла: {e}")
        return None