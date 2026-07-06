from datetime import datetime
import math
import re
from typing import List, Dict, Any

PHONE_PATTERN = re.compile(r"(?:\+7|8)\s*(?:\(?\d{3}\)?|\d{3})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")
NAME_PATTERN = re.compile(r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.")


def get_cashback_categories(transactions: List[Dict[str, Any]], year: int, month: int) -> Dict[str, float]:
    """Кешбэк по категориям за месяц (сумма amount)."""
    result: Dict[str, float] = {}
    for t in transactions:
        dt = datetime.strptime(t["date"], "%Y-%m-%d")
        if dt.year == year and dt.month == month:
            cat = t["category"]
            result[cat] = result.get(cat, 0.0) + float(t["amount"])
    return result


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Инвесткопилка: округление до ближайшего кратного limit, разница — в копилку."""
    target_year, target_month = map(int, month.split("-"))
    total_saved: float = 0.0
    for t in transactions:
        dt = datetime.strptime(t["date"], "%Y-%m-%d")
        if dt.year != target_year or dt.month != target_month:
            continue
        amount = float(t["amount"])
        if amount <= 0:
            continue
        # Округляем вверх до ближайшего кратного limit
        rounded = math.ceil(amount / limit) * limit
        total_saved += rounded - amount
    return total_saved


def search_transactions(transactions: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Простой поиск по подстроке (регистронезависимый) в description и category."""
    q = query.lower()
    result: List[Dict[str, Any]] = []
    for t in transactions:
        desc = str(t.get("description", "")).lower()
        cat = str(t.get("category", "")).lower()
        if q in desc or q in cat:
            result.append(t)
    return result


def find_transactions_with_phones(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Поиск транзакций с телефонными номерами в описании."""
    result: List[Dict[str, Any]] = []
    for t in transactions:
        desc = str(t.get("description", ""))
        if PHONE_PATTERN.search(desc):
            result.append(t)
    return result


def find_person_transfers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Переводы физлицам: категория «Переводы» + имя в формате «Имя Ф.» в описании."""
    result: List[Dict[str, Any]] = []
    for t in transactions:
        if t.get("category") != "Переводы":
            continue
        desc = str(t.get("description", ""))
        if NAME_PATTERN.search(desc):
            result.append(t)
    return result
