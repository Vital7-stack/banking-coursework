import pytest
from typing import List, Dict, Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services import (
        get_cashback_categories,
        investment_bank,
        search_transactions,
        find_transactions_with_phones,
        find_person_transfers,
    )
else:
    from src.services import (
        get_cashback_categories,
        investment_bank,
        search_transactions,
        find_transactions_with_phones,
        find_person_transfers,
    )


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        # Июнь 2024: Такси
        {"date": "2024-06-01", "amount": 1000.0, "category": "Такси", "description": "Поездка в аэропорт"},
        {"date": "2024-06-02", "amount": 2000.0, "category": "Такси", "description": "+7 (900) 111-22-33"},
        # Июль 2024: не должен попасть в июньский кешбэк
        {"date": "2024-07-01", "amount": 500.0, "category": "Такси", "description": "Валерий А."},
        # Июнь 2024: Продукты
        {"date": "2024-06-10", "amount": 1712.0, "category": "Продукты", "description": ""},
        # Июнь 2024: Переводы (для теста переводов)
        {"date": "2024-06-15", "amount": 300.0, "category": "Переводы", "description": "Сергей З."},
        {"date": "2024-06-20", "amount": 450.0, "category": "Переводы", "description": "Анна П."},
    ]


def test_get_cashback_categories(sample_transactions: List[Dict[str, Any]]) -> None:
    res = get_cashback_categories(sample_transactions, 2024, 6)
    # Все категории за июнь: Такси, Продукты, Переводы
    assert res == {"Такси": 3000.0, "Продукты": 1712.0, "Переводы": 750.0}


def test_investment_bank(sample_transactions: List[Dict[str, Any]]) -> None:
    # Покупка 1712 ₽, лимит 50 ₽ → округляем до 1750 ₽, разница 38 ₽
    res = investment_bank("2024-06", sample_transactions, 50)
    assert pytest.approx(res, 0.1) == 38.0


def test_search_transactions(sample_transactions: List[Dict[str, Any]]) -> None:
    res = search_transactions(sample_transactions, "такси")
    assert len(res) == 3
    res2 = search_transactions(sample_transactions, "аэропорт")
    assert len(res2) == 1


def test_find_transactions_with_phones(sample_transactions: List[Dict[str, Any]]) -> None:
    res = find_transactions_with_phones(sample_transactions)
    assert len(res) == 1  # одна запись с телефоном


def test_find_person_transfers(sample_transactions: List[Dict[str, Any]]) -> None:
    res = find_person_transfers(sample_transactions)
    assert len(res) == 2  # Сергей З. и Анна П.


def test_empty_list_search() -> None:
    assert search_transactions([], "любой запрос") == []
