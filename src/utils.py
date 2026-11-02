"""Утилиты: загрузка данных, парсинг дат, работа с настройками."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "operations.xls"  # <-- .xls
SETTINGS_PATH = PROJECT_ROOT / "user_settings.json"


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def load_transactions(path: Optional[Path] = None) -> pd.DataFrame:
    """Читает Excel-файл (.xls) с транзакциями и возвращает DataFrame."""
    path = path or DATA_PATH
    logger.info("Загрузка транзакций из %s", path)

    # Явно указываем engine='xlrd' для старых форматов .xls
    df = pd.read_excel(path, engine='xlrd')

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")
    df["Сумма операции"] = pd.to_numeric(df["Сумма операции"], errors="coerce").fillna(0)
    df["Сумма платежа"] = pd.to_numeric(df["Сумма платежа"], errors="coerce").fillna(0)
    df["Кешбэк"] = pd.to_numeric(df["Кэшбэк"], errors="coerce").fillna(0)
    df["Бонусы (включая кэшбэк)"] = pd.to_numeric(df["Бонусы (включая кэшбэк)"], errors="coerce").fillna(0)

    # Обработка возможного отсутствия колонки или разных названий
    invest_col = "Округление на инвесткопилку" if "Округление на инвесткопилку" in df.columns else "Округление на инвесткопилку"
    df["Округление на инвесткопилку"] = pd.to_numeric(df.get(invest_col, 0), errors="coerce").fillna(0)

    df["Номер карты"] = df["Номер карты"].astype(str).str.replace(r"\D", "", regex=True).str[-4:]
    return df


def load_user_settings(path: Optional[Path] = None) -> Dict[str, List[str]]:
    path = path or SETTINGS_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_input_date(date_str: str) -> datetime:
    """Принимает 'YYYY-MM-DD HH:MM:SS' или 'YYYY-MM-DD'."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Неверный формат даты: {date_str}")


def greeting_by_time(dt: datetime) -> str:
    h = dt.hour
    if 6 <= h <= 11:
        return "Доброе утро"
    if 12 <= h <= 17:
        return "Добрый день"
    if 18 <= h <= 22:
        return "Добрый вечер"
    return "Доброй ночи"


def get_month_range(dt: datetime) -> tuple[datetime, datetime]:
    start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start, dt


def get_week_range(dt: datetime) -> tuple[datetime, datetime]:
    start = dt - pd.Timedelta(days=dt.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, dt


def get_year_range(dt: datetime) -> tuple[datetime, datetime]:
    start = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return start, dt


def filter_by_range(df: pd.DataFrame, start: datetime, end: datetime) -> pd.DataFrame:
    mask = (df["Дата операции"] >= start) & (df["Дата операции"] <= end)
    return df.loc[mask].copy()