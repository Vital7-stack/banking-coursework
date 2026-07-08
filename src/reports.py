from typing import List, Dict, Any, Tuple, Optional


def is_transfer_category(cat: str) -> bool:
    """
    Определяет, является ли категория переводом.

    Логика для курсовой (прозрачная и простая):
    1. Приводим к нижнему регистру.
    2. Если фраза — это "не перевод" или начинается с "не ", считаем, что это НЕ перевод.
    3. Иначе, если в фразе есть слово "перевод", считаем это переводом.
       (Используем простой поиск подстроки, чтобы поймать "Перевод между...", "Обычный перевод" и т.д.)
    """
    if not cat:
        return False

    c = cat.strip().lower()

    # Явно исключаем "Не перевод" и всё, что начинается с "не "
    if c == "не перевод" or c.startswith("не "):
        return False

    # Если здесь есть слово "перевод", значит, это перевод
    # Это поймает: "перевод", "переводы", "Перевод между счетами", "Обычный перевод"
    return "перевод" in c


def aggregate_by_category(
    transactions: List[Dict[str, Any]],
) -> Tuple[Dict[str, float], Dict[str, float]]:
    by_cat: Dict[str, float] = {}
    transfers_total: float = 0.0

    for t in transactions:
        cat_raw: Optional[str] = t.get("category")
        amount_raw = t.get("amount")

        if cat_raw is None or amount_raw is None:
            continue

        cat = str(cat_raw).strip()

        try:
            amount: float = float(amount_raw)
        except (ValueError, TypeError):
            continue

        # Агрегация по всем категориям
        by_cat[cat] = by_cat.get(cat, 0.0) + amount

        # Проверка на перевод
        if is_transfer_category(cat):
            transfers_total += amount

    transfers: Dict[str, float] = {"Переводы": transfers_total}
    return by_cat, transfers


def top_7_with_rest(data: Dict[str, float]) -> Dict[str, float]:
    sorted_items = sorted(data.items(), key=lambda x: abs(x[1]), reverse=True)

    result: Dict[str, float] = {}
    rest_sum: float = 0.0

    for i, (cat, amount) in enumerate(sorted_items):
        if i < 7:
            result[cat] = amount
        else:
            rest_sum += amount

    if rest_sum != 0:
        result["Остальное"] = rest_sum

    return result
