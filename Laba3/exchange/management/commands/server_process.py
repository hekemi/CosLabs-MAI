from django.core.management.base import BaseCommand

from exchange.services import process_profit_by_group


class Command(BaseCommand):
    help = "Программа-сервер: загрузка данных источника и обработка"

    def add_arguments(self, parser):
        parser.add_argument("--in", dest="input_path", required=True, help="Путь к source JSON")
        parser.add_argument("--out", default="data/processed_payload.json", help="Путь выходного processed JSON")

    def handle(self, *args, **options):
        out = process_profit_by_group(options["input_path"], options["out"])
        self.stdout.write(self.style.SUCCESS(f"Сервер обработал данные: {out}"))