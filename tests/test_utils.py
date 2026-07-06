import os
from unittest.mock import patch
import pandas as pd
from src.utils import load_transactions, normalize_transactions, load_settings

@patch("pandas.read_excel")
def test_load_transactions_calls_read_excel(mock_read_excel):
    # Вот тут мы реально используем pd, чтобы сделать фейковый DataFrame
    mock_df = pd.DataFrame({
        "Дата операции": ["21.03.2019"],
        "Сумма операции": [100.0],
        "Категория": ["Переводы"],
        "Описание": ["Перевод"],
        "Статус": ["OK"]
    })
    mock_read_excel.return_value = mock_df

    df = load_transactions("dummy_path.xlsx")

    mock_read_excel.assert_called_once()
    assert len(df) == 1
    assert "Дата операции" in df.columns


def test_normalize_transactions_converts_negative_to_positive():
    # И тут тоже используем pd для создания данных
    mock_date = pd.Timestamp("2019-03-21")
    df = pd.DataFrame({
        "Дата операции": [mock_date],
        "Сумма операции": [-150.5],
        "Категория": ["Переводы"],
        "Описание": ["Перевод"]
    })

    result = normalize_transactions(df)
    assert len(result) == 1
    assert result[0]["amount"] == 150.5
    assert result[0]["date"] == "2019-03-21"


def test_load_settings_reads_json():
    settings_path = "user_settings.json"
    # Если файла нет — создадим пустой для теста
    if not os.path.exists(settings_path):
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write("{}")

    settings = load_settings(settings_path)
    assert isinstance(settings, dict)

