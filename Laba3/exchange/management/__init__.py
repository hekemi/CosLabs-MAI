import json
import random
from datetime import date, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand

from exchange.services import DEFAULT_SCHEMA, export_source_payload


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

        rows.append({
            "product_name": name,
            "product_group": group,
            "sold_qty": qty,
            "sale_price": sale,
            "purchase_price": purchase,
            "discount": discount,
            "sale_date": sale_date,
        })
    return rows


class Command(BaseCommand):
    help = "Программа-источник: формирование структуры и выгрузка данных во внешний JSON"

    def add_arguments(self, parser):
        parser.add_argument("--out", default="data/source_payload.json", help="Путь выходного JSON")
        parser.add_argument("--count", type=int, default=30, help="Количество случайных записей")
        parser.add_argument("--schema", help="Путь к JSON-схеме (если не указан, берется стандартная)")
        parser.add_argument("--rows", help="Путь к JSON-массиву строк (если не указан, генерируется случайно)")
        parser.add_argument("--dump-default-schema", help="Сохранить шаблон схемы и завершить")

    def handle(self, *args, **options):
        if options["dump_default_schema"]:
            p = Path(options["dump_default_schema"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(DEFAULT_SCHEMA, ensure_ascii=False, indent=2), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Шаблон схемы сохранен: {p}"))
            return

        if options["schema"]:
            schema = json.loads(Path(options["schema"]).read_text(encoding="utf-8"))
        else:
            schema = DEFAULT_SCHEMA

        if options["rows"]:
            rows = json.loads(Path(options["rows"]).read_text(encoding="utf-8"))
        else:
            rows = _random_rows(options["count"])

        out = export_source_payload(schema=schema, rows=rows, out_path=options["out"])
        self.stdout.write(self.style.SUCCESS(f"Источник выгрузил данные: {out}"))