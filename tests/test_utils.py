from datetime import datetime

import pandas as pd
import pytest

from src.utils import (
    filter_by_range,
    get_month_range,
    greeting_by_time,
    parse_input_date,
)


def test_greeting():
    assert greeting_by_time(datetime(2024, 1, 1, 8)) == "Доброе утро"
    assert greeting_by_time(datetime(2024, 1, 1, 13)) == "Добрый день"
    assert greeting_by_time(datetime(2024, 1, 1, 20)) == "Добрый вечер"
    assert greeting_by_time(datetime(2024, 1, 1, 23)) == "Доброй ночи"


def test_parse_input_date():
    dt = parse_input_date("2020-05-20 14:30:00")
    assert dt.year == 2020 and dt.month == 5 and dt.day == 20


def test_get_month_range():
    start, end = get_month_range(datetime(2020, 5, 20))
    assert start.day == 1 and end.day == 20


def test_filter_by_range():
    df = pd.DataFrame({"Дата операции": pd.to_datetime(["2020-05-01", "2020-04-15"])})
    filtered = filter_by_range(df, datetime(2020, 5, 1), datetime(2020, 5, 31))
    assert len(filtered) == 1