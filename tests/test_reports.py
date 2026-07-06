
from src.reports import aggregate_by_category, top_7_with_rest


class TestAggregateByCategory:
    def test_basic_aggregation(self) -> None:
        transactions = [
            {"category": "Продукты", "amount": 100},
            {"category": "Переводы", "amount": 50},
            {"category": "Продукты", "amount": 200},
            {"category": "Транспорт", "amount": 30},
        ]
        by_cat, transfers = aggregate_by_category(transactions)
        assert by_cat == {"Продукты": 300, "Переводы": 50, "Транспорт": 30}
        assert transfers == {"Переводы": 50}

    def test_empty_list(self) -> None:
        by_cat, transfers = aggregate_by_category([])
        assert by_cat == {}
        assert transfers == {}

    def test_invalid_amount_skipped(self) -> None:
        transactions = [
            {"category": "Продукты", "amount": "не_число"},
            {"category": "Продукты", "amount": None},
            {"category": "Продукты", "amount": 100},
        ]
        by_cat, _ = aggregate_by_category(transactions)
        assert by_cat == {"Продукты": 100}


class TestTop7WithRest:
    def test_less_than_7_categories(self) -> None:
        data = {"A": 10, "B": 20}
        result = top_7_with_rest(data)
        assert result == {"B": 20, "A": 10}
        assert "Остальное" not in result

    def test_more_than_7_categories_with_rest(self) -> None:
        data = {f"Cat{i}": i for i in range(1, 11)}
        result = top_7_with_rest(data)
        assert len(result) == 8
        assert "Остальное" in result
        assert result["Остальное"] == 6

    def test_no_rest_when_sum_is_zero(self) -> None:
        data = {f"Cat{i}": 10 for i in range(1, 6)}
        result = top_7_with_rest(data)
        assert "Остальное" not in result