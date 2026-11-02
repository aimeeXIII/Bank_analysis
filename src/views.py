"""Генерация JSON-ответов для веб-страниц."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from .utils import (
    filter_by_range,
    get_month_range,
    get_week_range,
    get_year_range,
    greeting_by_time,
    load_user_settings,
    parse_input_date,
)

logger = logging.getLogger(__name__)


# ---------- Внешние API ----------
def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Курсы валют с ЦБ РФ (XML)."""
    import requests

    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    result: List[Dict[str, Any]] = []
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        import xml.etree.ElementTree as ET

        root = ET.fromstring(resp.content)
        rates = {v.find("CharCode").text: float(v.find("Value").text.replace(",", ".")) for v in root.findall("Valute")}
        for cur in currencies:
            rate = rates.get(cur)
            if rate is not None:
                result.append({"currency": cur, "rate": float(rate)})
    except Exception as e:
        logger.error("Ошибка получения курсов валют: %s", e)
    return result


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Цены акций через Yahoo Finance."""
    import requests

    result: List[Dict[str, Any]] = []
    for symbol in stocks:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            data = resp.json()
            price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
            result.append({"stock": symbol, "price": float(price)})
        except Exception as e:
            logger.error("Ошибка получения цены %s: %s", symbol, e)
    return result


# ---------- Главная страница ----------
def _cards_summary(df: pd.DataFrame) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for last4, group in df.groupby("Номер карты"):
        if not last4 or last4 == "nan":
            continue
        spent = group.loc[group["Сумма операции"] < 0, "Сумма операции"].sum()
        spent = abs(float(spent))
        cashback = round(spent / 100, 2)
        cards.append({"last_digits": last4, "total_spent": round(spent, 2), "cashback": cashback})
    return cards


def _top_transactions(df: pd.DataFrame, n: int = 5) -> List[Dict[str, Any]]:
    df_sorted = df.sort_values("Сумма операции", ascending=False).head(n)
    out: List[Dict[str, Any]] = []
    for _, row in df_sorted.iterrows():
        out.append({
            "date": row["Дата операции"].strftime("%d.%m.%Y") if pd.notna(row["Дата операции"]) else "",
            "amount": float(row["Сумма операции"]),
            "category": str(row.get("Категория", "")),
            "description": str(row.get("Описание", "")),
        })
    return out


def main_page(date_str: str, transactions: pd.DataFrame) -> Dict[str, Any]:
    """Главная страница: приветствие, карты, топ-5, курсы, акции."""
    dt = parse_input_date(date_str)
    start, end = get_month_range(dt)
    df = filter_by_range(transactions, start, end)

    settings = load_user_settings()
    return {
        "greeting": greeting_by_time(dt),
        "cards": _cards_summary(df),
        "top_transactions": _top_transactions(df, 5),
        "currency_rates": get_currency_rates(settings.get("user_currencies", [])),
        "stock_prices": get_stock_prices(settings.get("user_stocks", [])),
    }


# ---------- Страница «События» ----------
def _split_main_and_other(series: "pd.Series[float]") -> List[Dict[str, Any]]:
    s = series.abs().groupby(series.index).sum().sort_values(ascending=False)
    top7 = s.head(7)
    rest = s.iloc[7:].sum() if len(s) > 7 else 0.0
    out = [{"category": k, "amount": int(round(v))} for k, v in top7.items()]
    if rest > 0:
        out.append({"category": "Остальное", "amount": int(round(rest))})
    return out


def events_page(date_str: str, transactions: pd.DataFrame, period: str = "M") -> Dict[str, Any]:
    dt = parse_input_date(date_str)
    if period == "W":
        start, end = get_week_range(dt)
    elif period == "Y":
        start, end = get_year_range(dt)
    elif period == "ALL":
        start = transactions["Дата операции"].min()
        end = dt
    else:
        start, end = get_month_range(dt)

    df = filter_by_range(transactions, start, end)

    expenses_df = df[df["Сумма операции"] < 0].copy()
    income_df = df[df["Сумма операции"] > 0].copy()

    transfers_cash = expenses_df[expenses_df["Категория"].isin(["Наличные", "Переводы"])]
    main_exp = expenses_df[~expenses_df["Категория"].isin(["Наличные", "Переводы"])]

    settings = load_user_settings()

    return {
        "expenses": {
            "total_amount": int(round(abs(expenses_df["Сумма операции"].sum()))),
            "main": _split_main_and_other(main_exp.groupby("Категория")["Сумма операции"].sum()),
            "transfers_and_cash": [
                {"category": k, "amount": int(round(abs(v)))}
                for k, v in transfers_cash.groupby("Категория")["Сумма операции"].sum().sort_values(ascending=False).items()
            ],
        },
        "income": {
            "total_amount": int(round(income_df["Сумма операции"].sum())),
            "main": [
                {"category": k, "amount": int(round(v))}
                for k, v in income_df.groupby("Категория")["Сумма операции"].sum().sort_values(ascending=False).items()
            ],
        },
        "currency_rates": get_currency_rates(settings.get("user_currencies", [])),
        "stock_prices": get_stock_prices(settings.get("user_stocks", [])),
    }