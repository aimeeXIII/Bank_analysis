"""Сервисы: кешбэк, инвесткопилка, поисковые функции."""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

PHONE_REGEX = re.compile(r"(?:\+?7|8)[\s\-()]?\d{3}[\s\-()]?\d{3}[\s\-()]?\d{2}[\s\-()]?\d{2}")
PERSON_TRANSFER_REGEX = re.compile(r"^[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.$", re.UNICODE)


# ---------- Выгодные категории кешбэка ----------
def cashback_categories(
    transactions: pd.DataFrame, year: int, month: int
) -> Dict[str, float]:
    """Сумма, которую можно было бы заработать кешбэком по каждой категории."""
    df = transactions.copy()
    mask = (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
    df = df.loc[mask]
    expenses = df[df["Сумма операции"] < 0]
    result = {
        cat: round(float(abs(grp["Сумма операции"].sum()) / 100), 2)
        for cat, grp in expenses.groupby("Категория")
    }
    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


# ---------- Инвесткопилка ----------
def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Сумма, которую удалось бы отложить в Инвесткопилку за месяц."""
    y, m = map(int, month.split("-"))
    total = 0.0
    for t in transactions:
        dt = pd.to_datetime(t["Дата операции"])
        if dt.year != y or dt.month != m:
            continue
        amount = abs(float(t["Сумма операции"]))
        if amount <= 0:
            continue
        rounded = ((int(amount) // limit) + 1) * limit
        total += rounded - amount
    return round(total, 2)


# ---------- Простой поиск ----------
def simple_search(transactions: pd.DataFrame, query: str) -> List[Dict[str, Any]]:
    q = query.lower()
    mask = (
        transactions["Описание"].fillna("").str.lower().str.contains(q, regex=False)
        | transactions["Категория"].fillna("").str.lower().str.contains(q, regex=False)
    )
    return transactions.loc[mask].to_dict(orient="records")


# ---------- Поиск по телефонным номерам ----------
def search_by_phone(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    mask = transactions["Описание"].fillna("").str.contains(PHONE_REGEX, regex=True)
    return transactions.loc[mask].to_dict(orient="records")


# ---------- Поиск переводов физлицам ----------
def search_person_transfers(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    mask = (
        (transactions["Категория"].fillna("") == "Переводы")
        & transactions["Описание"].fillna("").str.match(PERSON_TRANSFER_REGEX)
    )
    return transactions.loc[mask].to_dict(orient="records")