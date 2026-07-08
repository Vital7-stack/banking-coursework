from unittest.mock import patch, MagicMock
import pandas as pd

from src.utils import (
    load_transactions,
    normalize_transactions,

    filter_transactions_by_date,
)


@patch("pandas.read_excel")
def test_load_transactions_calls_read_excel(mock_read_excel: MagicMock) -> None:
    mock_df = pd.DataFrame(
        {
            "Дата операции": ["21.03.2019"],
            "Сумма операции": [100.0],
            "Категория": ["Переводы"],
            "Описание": ["Перевод"],
            "Статус": ["OK"],
        }
    )
    mock_read_excel.return_value = mock_df

    df = load_transactions("dummy_path.xlsx")

    mock_read_excel.assert_called_once()
    assert len(df) == 1
    assert "Дата операции" in df.columns  # оставь только тот вариант, который реально есть


def test_normalize_transactions_keeps_negative_sign() -> None:
    """Проверяет, что функция normalize_transactions сохраняет знак суммы."""
    mock_date = pd.Timestamp("2019-03-21")
    df = pd.DataFrame(
        {
            "Дата операции": [mock_date],
            "Сумма операции": [-150.5],
            "Категория": ["Переводы"],
            "Описание": ["Перевод"],
        }
    )

    result = normalize_transactions(df)

    assert len(result) == 1
    assert result[0]["amount"] == -150.5
    assert result[0]["date"] == "2019-03-21"


def test_normalize_transactions_preserves_sign() -> None:
    """Комплексный тест: проверяет сохранение знаков для разных типов транзакций."""
    data = [
        {"Дата операции": "2026-07-01", "Сумма операции": 50000, "Категория": "Зарплата", "Описание": ""},
        {"Дата операции": "2026-07-02", "Сумма операции": -3000, "Категория": "Продукты", "Описание": ""},
        {"Дата операции": "2026-07-03", "Сумма операции": -800, "Категория": "Такси", "Описание": ""},
    ]
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=False)

    normalized = normalize_transactions(df)

    assert len(normalized) == 3
    assert normalized[0]["amount"] == 50000
    assert normalized[1]["amount"] == -3000
    assert normalized[2]["amount"] == -800


def test_normalize_transactions_empty_dataframe() -> None:
    """Проверяет, что функция возвращает пустой список, если на вход пришёл пустой DataFrame."""
    columns = ["Дата операции", "Сумма операции", "Категория", "Описание"]
    df = pd.DataFrame(columns=columns)
    result = normalize_transactions(df)

    assert result == []


def test_filter_transactions_by_date() -> None:
    """Проверяет фильтрацию DataFrame по диапазону дат."""
    df = pd.DataFrame(
        {
            "Дата операции": ["01.01.2024", "15.01.2024", "31.01.2024"],
            "Сумма операции": [100, 200, 300],
            "Категория": ["Еда", "Транспорт", "Еда"],
            "Описание": ["", "", ""],
        }
    )
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    result = filter_transactions_by_date(df, "2024-01-10", "2024-01-20")

    assert len(result) == 1

    filtered_date = result["Дата операции"].iloc[0]
    assert filtered_date == pd.Timestamp("2024-01-15")


def test_load_transactions_filters_by_status_ok() -> None:
    """Проверяет ветку фильтрации по статусу 'OK'."""
    df_raw = pd.DataFrame(
        {
            "Дата операции": ["01.01.2024", "02.01.2024", "03.01.2024"],
            "Сумма операции": [100, 200, 300],
            "Категория": ["Еда", "Транспорт", "Еда"],
            "Описание": ["", "", ""],
            "Статус": ["OK", "ERROR", "OK"],
        }
    )

    with patch("pandas.read_excel", return_value=df_raw):
        df = load_transactions("dummy.xlsx")

    assert len(df) == 2
    assert set(df["Статус"].astype(str)) == {"OK"}
