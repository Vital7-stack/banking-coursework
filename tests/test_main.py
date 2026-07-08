import pandas as pd
from typing import Any
from unittest.mock import patch
from src.main import main


@patch("src.main.load_transactions")
@patch("src.main.build_dashboard")
def test_main_calls_load_and_build(mock_build: Any, mock_load: Any) -> None:
    mock_load.return_value = pd.DataFrame()
    mock_build.return_value = {"total": 0, "by_category": {}}

    result = main(start_date="2024-01-01", end_date="2024-01-31")

    mock_load.assert_called_once()
    mock_build.assert_called_once()

    assert isinstance(result, dict)
    assert "total" in result
