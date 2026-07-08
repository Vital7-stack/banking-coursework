import json
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils import load_transactions, filter_transactions_by_date
from src.views import build_dashboard


def main(
    data_path: Optional[str | Path] = None,
    settings_path: Optional[str | Path] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    base_dir = Path(__file__).resolve().parent.parent

    if data_path is None:
        data_path = base_dir / "data" / "operations.xlsx"
    if settings_path is None:
        settings_path = base_dir / "user_settings.json"

    df = load_transactions(data_path)

    # Фильтрация по периоду (если даты переданы)
    if start_date and end_date:
        df = filter_transactions_by_date(df, start_date, end_date)

    dashboard = build_dashboard(df, settings_path)
    return dashboard


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))
