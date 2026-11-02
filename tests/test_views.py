import pandas as pd
import pytest

from src import views
from src.views import events_page, main_page


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Дата операции": pd.to_datetime(["2020-05-10", "2020-05-15", "2020-05-20"]),
        "Номер карты": ["1234", "1234", "5678"],
        "Сумма операции": [-1000.0, -500.0, 200.0],
        "Категория": ["Супермаркеты", "Переводы", "Кэшбэк"],
        "Описание": ["Пятёрочка", "Иван И.", "Кэшбэк"],
    })


def test_main_page_structure(sample_df, monkeypatch):
    monkeypatch.setattr(views, "get_currency_rates", lambda c: [{"currency": "USD", "rate": 70.0}])
    monkeypatch.setattr(views, "get_stock_prices", lambda s: [{"stock": "AAPL", "price": 150.0}])
    res = main_page("2020-05-20 14:00:00", sample_df)
    assert res["greeting"] == "Добрый день"
    assert isinstance(res["cards"], list)
    assert len(res["top_transactions"]) <= 5
    assert res["currency_rates"][0]["currency"] == "USD"


def test_events_page_structure(sample_df, monkeypatch):
    monkeypatch.setattr(views, "get_currency_rates", lambda c: [])
    monkeypatch.setattr(views, "get_stock_prices", lambda s: [])
    res = events_page("2020-05-20", sample_df, "M")
    assert "expenses" in res and "income" in res
    assert res["expenses"]["total_amount"] >= 0