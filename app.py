import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_data
from src.analysis import (
    get_column_info, 
    get_summary_statistics, 
    get_column_types,
    sort_dataframe,
    group_data,
    get_top_bottom
)
from src.insights import generate_insights
from src.export import convert_df_to_csv
from src.export import convert_df_to_csv, convert_df_to_excel

st.set_page_config(
    page_title="Data Analysis Tool",
    page_icon="📊",
    layout="wide"
)

st.title("Data Analysis Tool")

uploaded_file = st.file_uploader("Загрузите CSV или Excel файл", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        st.success("Файл успешно загружен")
        
        # Определение типов колонок
        numeric_cols, categorical_cols, datetime_cols = get_column_types(df)
        
        # --- Боковая панель: Фильтрация, Сортировка и Экспорт ---
        st.sidebar.header("Динамические фильтры")
        filtered_df = df.copy()
        
        # 1. Категориальный фильтр
        if categorical_cols:
            cat_col = st.sidebar.selectbox("Фильтр по категориальным колонкам", ["None"] + categorical_cols)
            if cat_col != "None":
                selected_vals = st.sidebar.multiselect(f"Выберите значения для {cat_col}", df[cat_col].unique().tolist())
                if selected_vals:
                    filtered_df = filtered_df[filtered_df[cat_col].isin(selected_vals)]
                    
        # 2. Числовой фильтр
        if numeric_cols:
            num_col = st.sidebar.selectbox("Фильтр по числовым колонкам", ["None"] + numeric_cols)
            if num_col != "None":
                min_val = float(df[num_col].min())
                max_val = float(df[num_col].max())
                selected_range = st.sidebar.slider(f"Диапазон для {num_col}", min_val, max_val, (min_val, max_val))
                filtered_df = filtered_df[(filtered_df[num_col] >= selected_range[0]) & (filtered_df[num_col] <= selected_range[1])]

        # 3. Сортировка
        st.sidebar.markdown("---")
        st.sidebar.header("Сортировка данных")
        sort_col = st.sidebar.selectbox("Сортировать по колонке", ["None"] + list(df.columns))
        if sort_col != "None":
            sort_order = st.sidebar.radio("Порядок", ["По возрастанию", "По убыванию"])
            filtered_df = sort_dataframe(filtered_df, sort_col, ascending=(sort_order == "Ascending"))

        # 4. Скачивание отфильтрованного CSV или XLSX
        st.sidebar.markdown("---")
        st.sidebar.header("Экспорт результатов")
        
        csv_data = convert_df_to_csv(filtered_df)
        excel_data = convert_df_to_excel(filtered_df)
        
        col_exp1, col_exp2 = st.sidebar.columns(2)
        
        with col_exp1:
            st.download_button(
                label="CSV",
                data=csv_data,
                file_name="filtered_data.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with col_exp2:
            st.download_button(
                label="Excel",
                data=excel_data,
                file_name="filtered_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # --- MAIN OVERVIEW ---
        total_rows = len(filtered_df)
        total_cols = len(filtered_df.columns)
        total_missing = filtered_df.isnull().sum().sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Отфильтрованные строки (транзакции)", f"{total_rows:,}")
        col2.metric("Количество колонок (параметров)", f"{total_cols:,}")
        col3.metric("Количество пропущенных значений", f"{total_missing:,}")
        
        st.markdown("---")
        
        # --- TABS ---
        tab_preview, tab_columns, tab_summary, tab_grouping, tab_top_bottom, tab_charts, tab_insights = st.tabs([
            "Предпросмотр данных",
            "Информация о колонках",
            "Описательная статистика",
            "Группировка и агрегаты",
            "Лучшие и худшие",
            "Визуализации",
            "Авто-инсайты"
        ])
        
        with tab_preview:
            st.subheader("Предпросмотр данных")
            st.dataframe(filtered_df.head(100), use_container_width=True)
            
        with tab_columns:
            st.subheader("Метаданные колонок")
            st.dataframe(get_column_info(filtered_df), use_container_width=True)
            
        with tab_summary:
            st.subheader("Статистика по числовым показателям")
            summary_df = get_summary_statistics(filtered_df)
            if not summary_df.empty:
                st.dataframe(summary_df, use_container_width=True)
            else:
                st.info("Числовые колонки не найдены")

        with tab_grouping:
            st.subheader("Группировка по категориям")
            if categorical_cols and numeric_cols:
                g_col1, g_col2, g_col3 = st.columns(3)
                group_cat = g_col1.selectbox("Выбрать категорию", categorical_cols, key="g_cat")
                group_num = g_col2.selectbox("Выбрать метрику", numeric_cols, key="g_num")
                agg_func = g_col3.selectbox("Агрегация", ["sum", "mean", "count", "min", "max"], key="g_agg")
                
                grouped_res = group_data(filtered_df, group_cat, group_num, agg_func)
                st.dataframe(grouped_res, use_container_width=True)
                
                # Дополнительный график для группировки
                fig_bar = px.bar(
                    grouped_res.head(20), 
                    x=group_cat, 
                    y=f"{group_num}_{agg_func}", 
                    title=f"Топ категорий по {group_num} ({agg_func})"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("Для группировки нужна хотя бы одна категориальная и одна числовая колонка.")

        with tab_top_bottom:
            st.subheader("Топ & Bottom показатели")
            if numeric_cols:
                tb_col1, tb_col2 = st.columns(2)
                top_metric = tb_col1.selectbox("Выберите метрику для ранжирования", numeric_cols, key="tb_metric")
                top_n = tb_col2.slider("Количество записей (транзакций)", 3, 50, 10)
                
                top_df, bottom_df = get_top_bottom(filtered_df, top_metric, top_n)
                
                col_t, col_b = st.columns(2)
                with col_t:
                    st.write(f"### Top {top_n}")
                    st.dataframe(top_df, use_container_width=True)
                with col_b:
                    st.write(f"### Bottom {top_n}")
                    st.dataframe(bottom_df, use_container_width=True)
            else:
                st.warning("Числовые колонки для анализа лучших и худших показателей не найдены.")
        
              
        with tab_charts:
            st.subheader("Интерактивные визуализации")

            # 1. Time Series Chart (если есть дата)
            if datetime_cols and numeric_cols:
                st.write("### Динамика во времени")
                c_date = st.selectbox("Колонка даты", datetime_cols)
                c_metric = st.selectbox(
                    "Числовая метрика", numeric_cols, key="ts_metric"
                )

                # Конвертируем в datetime для корректного графика
                chart_df = filtered_df.copy()
                chart_df[c_date] = pd.to_datetime(chart_df[c_date], errors="coerce")
                chart_df = chart_df.dropna(subset=[c_date]).sort_values(c_date)

                fig_line = px.line(
                    chart_df, x=c_date, y=c_metric, title=f"Динамика {c_metric}"
                )
                st.plotly_chart(fig_line, use_container_width=True)
            elif numeric_cols:
                st.info(
                    "Колонки с датой не найдены. Отображается гистограмма распределения."
                )
                dist_metric = st.selectbox(
                    "Метрика для распределения", numeric_cols, key="dist_metric"
                )
                fig_hist = px.histogram(
                    filtered_df,
                    x=dist_metric,
                    title=f"Распределение показателей: {dist_metric}",
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.warning("Нет подходящих колонок для построения графиков.")

        with tab_insights:
            st.subheader("Автоматические выводы")
            insights_list = generate_insights(
                filtered_df, numeric_cols, categorical_cols, datetime_cols
            )
            for insight in insights_list:
                st.write(f"• {insight}")