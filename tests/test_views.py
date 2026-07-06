from unittest.mock import patch
import pandas as pd
from src.views import build_dashboard

@patch("src.views.load_settings")                 # <-- ВАЖНО: патчим в views, а не в utils
@patch("src.views.normalize_transactions")         # <-- и normalize_transactions тоже в views
def test_build_dashboard_returns_expected_structure(
    mock_normalize, mock_load_settings
):
    # Настраиваем моки
    mock_normalize.return_value = [
        {"date": "2019-03-21", "amount": 100.0, "category": "Переводы", "description": "Перевод"},
        {"date": "2019-03-21", "amount": 100.0, "category": "Переводы", "description": "Возврат"},
    ]
    mock_load_settings.return_value = {
        "currency_rates": {"USD": 90.5},
        "stock_prices": [{"stock": "YNDX", "price": 3500.5}]
    }

    fake_df = pd.DataFrame()
    # Путь можно передать любой — он не будет использоваться, потому что load_settings замокан в views
    dashboard = build_dashboard(fake_df, "любой/путь/к/файлу.json")

    # Проверяем структуру
    assert "top_5_transactions" in dashboard
    assert "expenses_by_category" in dashboard
    assert "currency_rates" in dashboard
    assert "stock_prices" in dashboard

    top_5 = dashboard["top_5_transactions"]
    # Проверка дедупликации: не должно быть дублей по (дата, сумма)
    seen = set()
    for t in top_5:
        key = (t["date"], t["amount"])
        assert key not in seen, f"Обнаружен дубль: {t}"
        seen.add(key)

