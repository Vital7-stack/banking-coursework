import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, cast
import json


def _clean_text(val: Any) -> str | Any:
    if isinstance(val, str):
        return " ".join(val.split()).strip()
    return val


def load_transactions(file_path: str | Path) -> pd.DataFrame:
    df = pd.read_excel(file_path)

    df.columns = df.columns.astype(str).str.strip()

    if "Дата операции" not in df.columns:
        print("Доступные колонки в файле:", list(df.columns))
        raise KeyError('Колонка "Дата операция" не найдена в Excel.')

    text_cols = ["Категория", "Описание", "Статус"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(_clean_text)

    key_cols = ["Дата операции", "Сумма операции", "Категория", "Описание"]
    missing_cols = [c for c in key_cols if c not in df.columns]
    if missing_cols:
        print("Не хватает колонок для дедупликации:", missing_cols)
        print("Доступные колонки:", list(df.columns))
        raise KeyError(f"Отсутствуют колонки: {missing_cols}")

    df = df.drop_duplicates(subset=key_cols, keep="first")

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")

    if "Статус" in df.columns:
        df = df[df["Статус"].astype(str) == "OK"]

    return df


def normalize_transactions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        amount = float(row["Сумма операции"])
        if amount < 0:
            amount = abs(amount)

        if pd.isna(row["Дата операции"]):
            continue

        records.append(
            {
                "date": row["Дата операции"].strftime("%Y-%m-%d"),
                "amount": amount,
                "category": str(row["Категория"]).strip(),
                "description": str(row.get("Описание", "")).strip(),
            }
        )
    return records


def load_settings(file_path: str | Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # cast говорит mypy: "я гарантирую, что тут Dict[str, Any]"
        return cast(Dict[str, Any], data)
