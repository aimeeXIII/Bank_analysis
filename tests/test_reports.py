import pandas as pd
import pytest

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday


@pytest.fixture
def df():
    return pd.DataFrame({
        "Дата операции": pd.to_datetime(["2020-03-10", "2020-04-15", "2020-05-20"]),
        "Сумма операции": [-1000.0, -500.0, -200.0],
        "Категория": ["Супермаркеты", "Супермаркеты", "Кафе"],
        "Описание": ["A", "B", "C"],
    })


def test_spending_by_category(df, tmp_path, monkeypatch):
    monkeypatch.setattr("src.reports.OUTPUT_DIR", tmp_path)
    res = spending_by_category(df, "Супермаркеты", "2020-05-20")
    assert len(res) == 2


def test_spending_by_weekday(df, tmp_path, monkeypatch):
    monkeypatch.setattr("src.reports.OUTPUT_DIR", tmp_path)
    res = spending_by_weekday(df, "2020-05-20")
    assert "weekday" in res.columns and "avg_spending" in res.columns


def test_spending_by_workday(df, tmp_path, monkeypatch):
    monkeypatch.setattr("src.reports.OUTPUT_DIR", tmp_path)
    res = spending_by_workday(df, "2020-05-20")
    assert set(res["day_type"]) <= {"Рабочий день", "Выходной день"}