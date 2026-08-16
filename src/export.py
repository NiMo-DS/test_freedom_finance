import io
import pandas as pd

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Конвертирует DataFrame в CSV."""
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """Конвертирует DataFrame в Excel (.xlsx)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered_Data')
    return output.getvalue()