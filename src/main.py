import json
from pathlib import Path

from src.utils import load_transactions
from src.views import build_dashboard


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "data" / "operations.xlsx"
    settings_path = base_dir / "user_settings.json"

    df = load_transactions(data_path)
    dashboard = build_dashboard(df, settings_path)

    print(json.dumps(dashboard, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
