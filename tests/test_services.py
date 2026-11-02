import pandas as pd
import pytest

from src.services import (
    cashback_categories,
    investment_bank,
    search_by_phone,
    search_person_transfers,
    simple_search,
)


@pytest.fixture
def df():
    return pd.DataFrame({
        "Дата операции": pd.to_datetime(["2020-05-10", "2020-05-15", "2020-05-20", "2020-05-21"]),
        "Сумма операции": [-1000.0, -500.0, -200.0, 100.0],
        "Категория": ["Супермаркеты", "Переводы", "Кафе", "Кэшбэк"],
        "Описание": ["Пятёрочка", "Валерий А.", "+7 921 112 23 33 МТС", "Кэшбэк"],
    })


def test_cashback_categories(df):
    res = cashback_categories(df, 2020, 5)
    assert "Супермаркеты" in res
    assert res["Супермаркеты"] == 10.0


def test_investment_bank():
    txs = [{"Дата операции": "2020-05-10", "Сумма операции": -1712}]
    assert investment_bank("2020-05", txs, 50) == 38.0


def test_simple_search(df):
    res = simple_search(df, "пятёр")
    assert len(res) == 1


def test_search_by_phone(df):
    res = search_by_phone(df)
    assert len(res) == 1 and "+7 921" in res[0]["Описание"]


def test_search_person_transfers(df):
    res = search_person_transfers(df)
    assert len(res) == 1 and res[0]["Описание"] == "Валерий А."