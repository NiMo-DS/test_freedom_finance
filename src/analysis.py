import pandas as pd


def get_column_info(df: pd.DataFrame) -> pd.DataFrame:
    info = pd.DataFrame({
        "Колонка": df.columns,
        "Тип данных": [str(dtype) for dtype in df.dtypes],
        "Пропущенные значения": df.isnull().sum().values,
        "% пропусков": (df.isnull().sum().values / len(df) * 100).round(2),
    })
    return info


def get_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.describe().T


def get_column_types(df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    datetime_cols = []
    categorical_cols = []

    for col in df.columns:
        if col in numeric_cols:
            continue
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        else:
            sample = df[col].dropna().head(50)
            try:
                pd.to_datetime(sample)
                datetime_cols.append(col)
            except Exception:
                categorical_cols.append(col)

    return numeric_cols, categorical_cols, datetime_cols


# --- ВСПОМОГАТЕЛЬНЫЕ ОПЕРАЦИИ С ДАННЫМИ ---


def sort_dataframe(
    df: pd.DataFrame, column: str, ascending: bool
) -> pd.DataFrame:
    """Сортирует датафрейм по выбранной колонке."""
    if column:
        return df.sort_values(by=column, ascending=ascending)
    return df


def group_data(
    df: pd.DataFrame, category_col: str, metric_col: str, agg_func: str
) -> pd.DataFrame:
    """Группирует данные по категории и метрике."""
    if not category_col or not metric_col:
        return pd.DataFrame()

    grouped = df.groupby(category_col)[metric_col].agg(agg_func).reset_index()
    grouped.columns = [category_col, f"{metric_col}_{agg_func}"]
    return grouped.sort_values(by=f"{metric_col}_{agg_func}", ascending=False)


def get_top_bottom(df: pd.DataFrame, metric_col: str, n: int = 10):
    """Возвращает Top-N и Bottom-N записей по выбранной метрике."""
    if not metric_col:
        return pd.DataFrame(), pd.DataFrame()

    sorted_df = df.sort_values(by=metric_col, ascending=False)
    top_n = sorted_df.head(n)
    bottom_n = sorted_df.tail(n).iloc[::-1]  # переворачиваем для удобства
    return top_n, bottom_n