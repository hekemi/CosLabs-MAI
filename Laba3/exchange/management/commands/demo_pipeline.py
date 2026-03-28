from datetime import date, timedelta
import random

from django.core.management.base import BaseCommand

from exchange.services import (
    DEFAULT_SCHEMA,
    build_excel_visualization,
    export_source_payload,
    process_profit_by_group,
)
from exchange.utils import generate_random_rows


PRODUCTS = [
    ("Молоко", "Продукты"),
    ("Хлеб", "Продукты"),
    ("Сок", "Напитки"),
    ("Чай", "Напитки"),
    ("Мыло", "Бытовая химия"),
    ("Порошок", "Бытовая химия"),
]


class Command(BaseCommand):
    help = "Полная демонстрация: источник -> сервер -> визуализатор"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=30)
        parser.add_argument("--source-out", default="data/source_payload.json")
        parser.add_argument("--processed-out", default="data/processed_payload.json")
        parser.add_argument("--excel-out", default="data/profit_chart.xlsx")

    def handle(self, *args, **options):
        rows = generate_random_rows(options["count"])
        src = export_source_payload(DEFAULT_SCHEMA, rows, options["source_out"])
        processed = process_profit_by_group(src, options["processed_out"])
        xlsx = build_excel_visualization(processed, options["excel_out"])

        self.stdout.write(self.style.SUCCESS(f"Источник: {src}"))
        self.stdout.write(self.style.SUCCESS(f"Сервер: {processed}"))
        self.stdout.write(self.style.SUCCESS(f"Визуализатор: {xlsx}"))