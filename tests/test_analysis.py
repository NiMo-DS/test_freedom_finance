import pandas as pd
import pytest
from src.analysis import get_column_info, get_summary_statistics, sort_dataframe, group_data, get_top_bottom

@pytest.fixture
def sample_df():
    """Фикстура: искусственный датасет для тестирования."""
    data = {
        'Category': ['A', 'B', 'A', 'B', 'C'],
        'Revenue': [100.0, 200.0, 150.0, 300.0, 50.0],
        'Quantity': [10, 20, 15, 30, 5]
    }
    return pd.DataFrame(data)

def test_get_column_info(sample_df):
    info = get_column_info(sample_df)
    assert len(info) == 3
    assert 'Column' in info.columns
    assert 'Missing Values' in info.columns

def test_sort_dataframe(sample_df):
    sorted_df = sort_dataframe(sample_df, 'Revenue', ascending=False)
    assert sorted_df.iloc[0]['Revenue'] == 300.0
    assert sorted_df.iloc[-1]['Revenue'] == 50.0

def test_group_data(sample_df):
    grouped = group_data(sample_df, 'Category', 'Revenue', 'sum')
    assert len(grouped) == 3
    # Проверяем, что категория A в сумме дает 250 (100 + 150)
    a_revenue = grouped[grouped['Category'] == 'A']['Revenue_sum'].values[0]
    assert a_revenue == 250.0

def test_get_top_bottom(sample_df):
    top_2, bottom_2 = get_top_bottom(sample_df, 'Revenue', n=2)
    assert len(top_2) == 2
    assert top_2.iloc[0]['Revenue'] == 300.0
    assert len(bottom_2) == 2