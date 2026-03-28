from datetime import date, timedelta
import random

from django.core.management.base import BaseCommand

from exchange.services import (
    DEFAULT_SCHEMA,
    build_excel_visualization,
    export_source_payload,
    process_profit_by_group,
)


PRODUCTS = [
    ("Молоко", "Продукты"),
    ("Хлеб", "Продукты"),
    ("Сок", "Напитки"),
    ("Чай", "Напитки"),
    ("Мыло", "Бытовая химия"),
    ("Порошок", "Бытовая химия"),
]


def _random_rows(count: int) -> list[dict]:
    rows = []
    for _ in range(count):
        name, group = random.choice(PRODUCTS)
        qty = random.randint(1, 20)
        purchase = round(random.uniform(20, 200), 2)
        sale = round(purchase * random.uniform(1.05, 1.6), 2)
        discount = round(random.uniform(0, 15), 2)
        sale_date = (date.today() - timedelta(days=random.randint(0, 30))).isoformat()

        rows.append(
            {
                "product_name": name,
                "product_group": group,
                "sold_qty": qty,
                "sale_price": sale,
                "purchase_price": purchase,
                "discount": discount,
                "sale_date": sale_date,
            }
        )
    return rows


class Command(BaseCommand):
    help = "Полная демонстрация: источник -> сервер -> визуализатор"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=30)
        parser.add_argument("--source-out", default="data/source_payload.json")
        parser.add_argument("--processed-out", default="data/processed_payload.json")
        parser.add_argument("--excel-out", default="data/profit_chart.xlsx")

    def handle(self, *args, **options):
        rows = _random_rows(options["count"])
        src = export_source_payload(DEFAULT_SCHEMA, rows, options["source_out"])
        processed = process_profit_by_group(src, options["processed_out"])
        xlsx = build_excel_visualization(processed, options["excel_out"])

        self.stdout.write(self.style.SUCCESS(f"Источник: {src}"))
        self.stdout.write(self.style.SUCCESS(f"Сервер: {processed}"))
        self.stdout.write(self.style.SUCCESS(f"Визуализатор: {xlsx}"))