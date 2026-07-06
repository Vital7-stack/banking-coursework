from collections import defaultdict
from typing import List, Dict, Any, Tuple, Optional, Callable
import json
from functools import wraps


def log_report(filename: Optional[str] = None) -> Callable:
    """Декоратор: пишет результат функции-отчёта в JSON-файл."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            default_name = f"report_{func.__name__}.json"
            target_file = filename if filename else default_name
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            return result

        return wrapper

    return decorator


def aggregate_by_category(transactions: List[Dict[str, Any]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Агрегирует транзакции по категориям и отдельно выделяет «Переводы» и «Наличные».
    Возвращает кортеж: (по всем категориям, только переводы и наличные).
    """
    by_category: Dict[str, float] = defaultdict(float)
    transfers_and_cash: Dict[str, float] = defaultdict(float)

    for t in transactions:
        cat = t.get("category")
        if cat is None:
            continue

        amount_raw = t.get("amount")
        if amount_raw is None:
            continue

        try:
            amount = float(amount_raw)
        except (ValueError, TypeError):
            continue

        by_category[cat] += amount
        if cat in ("Переводы", "Наличные"):
            transfers_and_cash[cat] += amount

    by_category_int: Dict[str, int] = {k: int(round(v)) for k, v in by_category.items()}
    transfers_and_cash_int: Dict[str, int] = {k: int(round(v)) for k, v in transfers_and_cash.items()}

    return by_category_int, transfers_and_cash_int


def top_7_with_rest(by_category: Dict[str, int]) -> Dict[str, int]:
    """
    Оставляет топ‑7 категорий по сумме, остальное складывает в «Остальное».
    """
    sorted_items: List[Tuple[str, int]] = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    top_7: Dict[str, int] = dict(sorted_items[:7])
    rest_sum: int = sum(v for _, v in sorted_items[7:])

    if rest_sum > 0:
        top_7["Остальное"] = rest_sum

    return top_7
