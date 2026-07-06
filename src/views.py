from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
from pathlib import Path
from src.utils import normalize_transactions, load_settings
from src.reports import aggregate_by_category, top_7_with_rest


def get_greeting() -> str:
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def build_dashboard(raw_df: pd.DataFrame, settings_path: str | Path) -> Dict[str, Any]:
    transactions = normalize_transactions(raw_df)
    settings = load_settings(settings_path)

    greeting = get_greeting()

    # Убираем зеркальные дубли по (дата + модуль суммы)
    seen = set()
    unique_transactions: List[Dict[str, Any]] = []

    # Сортируем по убыванию модуля суммы
    sorted_transactions = sorted(transactions, key=lambda t: abs(t["amount"]), reverse=True)

    for transaction in sorted_transactions:
        key = (transaction["date"], abs(transaction["amount"]))

        if key not in seen:
            seen.add(key)
            unique_transactions.append(transaction)

    top_5 = unique_transactions[:5]

    for transaction in top_5:
        transaction["date"] = datetime.strptime(transaction["date"], "%Y-%m-%d").strftime("%d.%m.%Y")

    by_category, transfers_and_cash = aggregate_by_category(transactions)
    expenses_by_category = top_7_with_rest(by_category)

    currency_rates = [{"currency": cur, "rate": rate} for cur, rate in settings["currency_rates"].items()]

    stock_prices = settings["stock_prices"]

    return {
        "greeting": greeting,
        "top_5_transactions": top_5,
        "expenses_by_category": expenses_by_category,
        "transfers_and_cash": transfers_and_cash,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
