import pandas as pd


def generate_insights(
    df: pd.DataFrame,
    numeric_cols: list,
    categorical_cols: list,
    datetime_cols: list,
) -> list:
    """Генерирует список автоматических текстовых инсайтов по данным."""
    insights = []

    if df.empty:
        return ["Датасет пуст. Загрузите данные для получения аналитики."]

    # 1. Инсайт по пропускам
    total_cells = df.size
    total_missing = df.isnull().sum().sum()
    if total_missing > 0:
        missing_pct = (total_missing / total_cells) * 100
        insights.append(
            f"**Пропущенные данные**: датасет содержит {total_missing:,}"
            f" пропущенных значений ({missing_pct:.1f}% от общего объема"
            " ячеек)."
        )
    else:
        insights.append(
            "**Данные полны**: пропущенных значений в датасете не обнаружено."
        )

    # 2. Инсайт по самой крупной категории
    for cat in categorical_cols[:2]:  # Проверяем первые две категории
        top_val = df[cat].mode()
        if not top_val.empty:
            count = (df[cat] == top_val[0]).sum()
            pct = (count / len(df)) * 100
            insights.append(
                f"**Преобладающая категория**: в колонке `{cat}` наиболее часто"
                f" встречается **'{top_val[0]}'** ({pct:.1f}% строк)."
            )

    # 3. Инсайт по числовым метрикам (вариативность / выбросы)
    for num in numeric_cols[:2]:
        mean_val = df[num].mean()
        std_val = df[num].std()
        max_val = df[num].max()
        min_val = df[num].min()

        insights.append(
            f"**Обзор метрики `{num}`**: значения от {min_val:,.2f} до"
            f" {max_val:,.2f} со средним **{mean_val:,.2f}**."
        )

        # Высокий разброс
        if mean_val != 0 and (std_val / abs(mean_val)) > 1:
            insights.append(
                f"**Высокая изменчивость**: колонка `{num}` имеет высокий"
                " разброс относительно своего среднего значения."
            )

    return insights