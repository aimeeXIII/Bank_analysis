"""Точка входа: демонстрация работы приложения."""
from __future__ import annotations

from .reports import spending_by_category, spending_by_weekday, spending_by_workday
from .services import (
    cashback_categories,
    investment_bank,
    search_by_phone,
    search_person_transfers,
    simple_search,
)
from .utils import load_transactions, setup_logging
from .views import events_page, main_page


def main() -> None:
    setup_logging()
    df = load_transactions()

    print("=== Главная страница (20.05.2020) ===")
    print(main_page("2020-05-20 14:30:00", df))

    print("\n=== Страница События (M) ===")
    print(events_page("2020-05-20", df, "M"))

    print("\n=== Топ категории кешбэка (2020, 5) ===")
    print(cashback_categories(df, 2020, 5))

    print("\n=== Инвесткопилка (шаг 100) ===")
    txs = df[["Дата операции", "Сумма операции"]].to_dict("records")
    print(investment_bank("2020-05", txs, 100))

    print("\n=== Поиск 'Лента' ===")
    print(simple_search(df, "Лента"))

    print("\n=== Поиск по телефонам ===")
    print(search_by_phone(df))

    print("\n=== Переводы физлицам ===")
    print(search_person_transfers(df))

    print("\n=== Отчёты ===")
    spending_by_category(df, "Супермаркеты", "2020-05-20")
    spending_by_weekday(df, "2020-05-20")
    spending_by_workday(df, "2020-05-20")


if __name__ == "__main__":
    main()