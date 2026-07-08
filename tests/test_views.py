from typing import Any
from unittest.mock import patch
import pandas as pd

from src.views import build_dashboard
from src.utils import filter_transactions_by_date


@patch("src.views.load_settings", return_value={"currency_rates": {}, "stock_prices": []})
def test_build_dashboard_filters_by_date_range(_: Any) -> None:
    df = pd.DataFrame(
        [
            {"Дата операции": "2024-01-01", "Сумма операции": 100, "Категория": "Еда", "Описание": ""},
            {"Дата операции": "2024-01-15", "Сумма операции": 200, "Категория": "Транспорт", "Описание": ""},
            {"Дата операции": "2024-01-30", "Сумма операции": 300, "Категория": "Еда", "Описание": ""},
        ]
    )
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=False)

    filtered_df = filter_transactions_by_date(df, "2024-01-10", "2024-01-20")
    result = build_dashboard(filtered_df, "dummy.json")

    assert len(result["top_5_transactions"]) == 1
    assert result["top_5_transactions"][0]["category"] == "Транспорт"


@patch(
    "src.views.load_settings",
    return_value={"currency_rates": {"USD": 90}, "stock_prices": [{"stock": "YNDX", "price": 3500}]},
)
def test_build_dashboard_empty_after_filter(_: Any) -> None:
    df = pd.DataFrame(
        [
            {"Дата операции": "2024-01-01", "Сумма операции": 100, "Категория": "Еда", "Описание": ""},
        ]
    )
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=False)

    filtered_df = filter_transactions_by_date(df, "2024-02-01", "2024-02-28")
    result = build_dashboard(filtered_df, "dummy.json")

    assert len(result["top_5_transactions"]) == 0
    assert isinstance(result["expenses_by_category"], dict)
    assert len(result["expenses_by_category"]) == 0
