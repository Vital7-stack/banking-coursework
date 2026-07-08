from typing import Any, List, Dict

from src.reports import aggregate_by_category, top_7_with_rest
from src.utils import filter_by_date_range


# --- Существующие тесты (оставляем как есть) ---
def test_filter_by_date_range_works() -> None:
    transactions: List[Dict[str, Any]] = [
        {"date": "2026-07-01", "category": "Продукты", "amount": -100},
        {"date": "2026-07-02", "category": "Зарплата", "amount": 50000},
        {"date": "2026-07-03", "category": "Такси", "amount": -500},
        {"date": "2026-07-10", "category": "Игры", "amount": -2000},
    ]

    filtered = filter_by_date_range(transactions, "2026-07-01", "2026-07-03")

    assert len(filtered) == 3
    dates = [t["date"] for t in filtered]
    assert "2026-07-10" not in dates


def test_aggregate_keeps_signs_and_filters() -> None:
    all_tx: List[Dict[str, Any]] = [
        {"date": "2026-07-02", "category": "Зарплата", "amount": 50000},
        {"date": "2026-07-02", "category": "Продукты", "amount": -3000},
        {"date": "2026-06-30", "category": "Переводы", "amount": -500},
    ]

    tx_in_period = filter_by_date_range(all_tx, "2026-07-01", "2026-07-31")
    assert len(tx_in_period) == 2

    by_cat, transfers = aggregate_by_category(tx_in_period)

    assert by_cat["Зарплата"] == 50000
    assert by_cat["Продукты"] == -3000

    mixed_tx: List[Dict[str, Any]] = [
        {"date": "2026-07-01", "category": "Еда", "amount": 50.5},
        {"date": "2026-07-01", "category": "Еда", "amount": 49.5},
    ]
    by_cat_mixed, _ = aggregate_by_category(mixed_tx)
    assert by_cat_mixed["Еда"] == 100.0


def test_aggregate_by_category_basic() -> None:
    transactions: List[Dict[str, Any]] = [
        {"category": "Переводы", "amount": 100.4},
        {"category": "Переводы", "amount": 200.6},
        {"category": "Образование", "amount": 50.5},
    ]
    by_cat, transfers = aggregate_by_category(transactions)

    assert by_cat["Переводы"] == 301.0
    assert by_cat["Образование"] == 50.5


# --- НОВЫЕ ТЕСТЫ (исправленные и готовые к работе) ---


def test_top_7_sorts_by_absolute_value_and_preserves_sign() -> None:
    """
    Проверяет, что топ‑7 формируется по модулю суммы, но знак сохраняется.
    Замечание: «крупные расходы не должны теряться в „Остальное“».
    """
    base_tx = [
        {"category": "Аренда", "amount": -45000},  # Крупный расход — должен быть в топе
        {"category": "Кэшбэк", "amount": 50},  # Мелкий доход
        {"category": "Продукты", "amount": -3000},  # Средний расход
    ]

    # Добавляем ещё несколько категорий, чтобы было больше 7
    extra_tx = [{"category": f"Категория {i}", "amount": i * -10} for i in range(1, 6)]

    transactions = base_tx + extra_tx

    by_cat, _ = aggregate_by_category(transactions)
    top7 = top_7_with_rest(by_cat)

    # «Аренда» с -45000 должна быть первой (самая большая по модулю)
    first_cat = next(iter(top7.keys()))
    assert first_cat == "Аренда"
    assert top7["Аренда"] == -45000  # Знак сохранён

    # Проверяем, что «Остальное» вообще появилось, если категорий > 7
    assert "Остальное" in top7


def test_aggregate_on_empty_list_does_not_fail() -> None:
    """
    Если после фильтрации транзакций нет — агрегация не должна выбрасывать ошибку.
    """
    empty_transactions: List[Dict[str, Any]] = []
    by_cat, transfers = aggregate_by_category(empty_transactions)

    assert isinstance(by_cat, dict)
    assert len(by_cat) == 0
    assert transfers == {"Переводы": 0.0}


def test_transfers_detected_by_substring() -> None:
    """
    Проверяет гибкое определение переводов по подстроке (case‑insensitive).
    """
    transactions: List[Dict[str, Any]] = [
        {"category": "Перевод", "amount": -1000},
        {"category": "переводы", "amount": -2000},
        {"category": "Перевод между счетами", "amount": -500},
        {"category": "Обычный перевод", "amount": -300},
        {"category": "Не перевод", "amount": -999},  # Не должен попасть в переводы
    ]

    by_cat, transfers = aggregate_by_category(transactions)

    total_transfers = transfers["Переводы"]
    expected_transfers = -1000 - 2000 - 500 - 300  # -3800
    assert total_transfers == expected_transfers

    # Категория «Не перевод» не должна быть в сумме переводов, но должна быть в by_cat
    assert "Не перевод" in by_cat
