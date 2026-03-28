from django.core.management.base import BaseCommand

from exchange.services import build_excel_visualization


class Command(BaseCommand):
    help = "Программа-визуализатор: выгрузка результатов в Excel + диаграмма"

    def add_arguments(self, parser):
        parser.add_argument("--in", dest="input_path", required=True, help="Путь к processed JSON")
        parser.add_argument("--out", default="data/profit_chart.xlsx", help="Путь к выходному XLSX")

    def handle(self, *args, **options):
        out = build_excel_visualization(options["input_path"], options["out"])
        self.stdout.write(self.style.SUCCESS(f"Excel-файл сформирован: {out}"))