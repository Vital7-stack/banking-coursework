import json
from pathlib import Path
from typing import Any, Dict, List, cast

import pandas as pd


def _clean_text(val: Any) -> str | Any:
    if isinstance(val, str):
        return " ".join(val.split()).strip()
    return val


def load_transactions(file_path: str | Path) -> pd.DataFrame:
    df = pd.read_excel(file_path)

    df.columns = df.columns.astype(str).str.strip()

    required_date_column = "Дата операции"
    if required_date_column not in df.columns:
        print("Доступные колонки в файле:", list(df.columns))
        raise KeyError(f'Колонка "{required_date_column}" не найдена в Excel.')

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

    # dayfirst=True нужен, если в Excel даты в формате ДД.ММ.ГГГГ
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"],
        dayfirst=True,
        errors="coerce",
    )

    if "Статус" in df.columns:
        status_col = df["Статус"].astype(str)
        df = df[status_col == "OK"]

    return df


def filter_transactions_by_date(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Фильтрует DataFrame по колонке 'Дата операции' в диапазоне [start_date, end_date].
    Даты в формате YYYY-MM-DD.
    Работает быстрее, чем фильтрация после конвертации в список.
    """
    if df.empty:
        return df

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    mask = (df["Дата операции"] >= start) & (df["Дата операции"] <= end)
    return df.loc[mask].copy()


def normalize_transactions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Конвертирует DataFrame в список словарей.
    ВАЖНО: знак суммы сохраняется (минус = расход, плюс = доход).

    Теперь работает и с datetime (из файла), и со строками (из тестов).
    """
    records: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        amount_raw = row["Сумма операции"]
        date_val = row["Дата операции"]

        # Пропускаем строки с некорректной датой
        if pd.isna(date_val):
            continue

        # Безопасное приведение суммы к float
        try:
            amount = float(amount_raw)
        except (ValueError, TypeError):
            continue

        # ГЛАВНОЕ ИСПРАВЛЕНИЕ: универсально обрабатываем дату
        if isinstance(date_val, str):
            # Если дата пришла строкой (как в тестах) — просто берём её
            date_str = date_val
        else:
            # Если это datetime (как после pd.to_datetime в load_transactions) — конвертируем
            try:
                date_str = date_val.strftime("%Y-%m-%d")
            except AttributeError:
                # На всякий случай: если вдруг что-то совсем странное
                date_str = str(date_val)

        records.append(
            {
                "date": date_str,
                "amount": amount,
                "category": str(row["Категория"]).strip(),
                "description": str(row.get("Описание", "")).strip(),
            }
        )
    return records


def filter_by_date_range(
    transactions: List[Dict[str, Any]],
    start_date: str,
    end_date: str,
) -> List[Dict[str, Any]]:
    """
    Фильтрует список транзакций (словарей) по диапазону дат.
    Формат даты: YYYY-MM-DD (такой формат мы получаем из strftime).
    Используется, если данные уже в виде списка.
    """
    filtered: List[Dict[str, Any]] = []
    for t in transactions:
        tx_date = t.get("date")
        if not isinstance(tx_date, str):
            continue
        if start_date <= tx_date <= end_date:
            filtered.append(t)
    return filtered


def load_settings(file_path: str | Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return cast(Dict[str, Any], data)
