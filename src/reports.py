"""Отчёты + декоратор сохранения результата в файл."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "reports_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def report_to_file(filename: Optional[str] = None):
    """Декоратор: сохраняет результат отчёта в JSON-файл."""
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            name = filename or f"{func.__name__}_{datetime.now():%Y%m%d_%H%M%S}.json"
            path = OUTPUT_DIR / name
            try:
                if isinstance(result, pd.DataFrame):
                    result.to_json(path, orient="records", force_ascii=False, indent=2, date_format="iso")
                else:
                    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
                logger.info("Отчёт сохранён: %s", path)
            except Exception as e:
                logger.error("Ошибка сохранения отчёта: %s", e)
            return result
        return wrapper
    return decorator


@report_to_file()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """Траты по категории за последние 3 месяца."""
    dt = pd.to_datetime(date) if date else pd.Timestamp.now()
    start = dt - pd.DateOffset(months=3)
    mask = (
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= start)
        & (transactions["Дата операции"] <= dt)
        & (transactions["Сумма операции"] < 0)
    )
    return transactions.loc[mask, ["Дата операции", "Сумма операции", "Категория", "Описание"]].copy()


@report_to_file()
def spending_by_weekday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> pd.DataFrame:
    """Средние траты по дням недели за последние 3 месяца."""
    dt = pd.to_datetime(date) if date else pd.Timestamp.now()
    start = dt - pd.DateOffset(months=3)
    df = transactions[
        (transactions["Дата операции"] >= start)
        & (transactions["Дата операции"] <= dt)
        & (transactions["Сумма операции"] < 0)
    ].copy()
    df["weekday"] = df["Дата операции"].dt.day_name()
    grouped = df.groupby("weekday")["Сумма операции"].mean().abs().reset_index()
    grouped.columns = ["weekday", "avg_spending"]
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    grouped["weekday"] = pd.Categorical(grouped["weekday"], categories=order, ordered=True)
    return grouped.sort_values("weekday").reset_index(drop=True)


@report_to_file()
def spending_by_workday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> pd.DataFrame:
    """Средние траты в рабочий и выходной день за последние 3 месяца."""
    dt = pd.to_datetime(date) if date else pd.Timestamp.now()
    start = dt - pd.DateOffset(months=3)
    df = transactions[
        (transactions["Дата операции"] >= start)
        & (transactions["Дата операции"] <= dt)
        & (transactions["Сумма операции"] < 0)
    ].copy()
    df["is_workday"] = df["Дата операции"].dt.weekday < 5
    grouped = df.groupby("is_workday")["Сумма операции"].mean().abs().reset_index()
    grouped["day_type"] = grouped["is_workday"].map({True: "Рабочий день", False: "Выходной день"})
    return grouped[["day_type", "Сумма операции"]].rename(columns={"Сумма операции": "avg_spending"})