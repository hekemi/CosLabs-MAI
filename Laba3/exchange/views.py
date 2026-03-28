import json
from pathlib import Path

from django.contrib import messages
from django.shortcuts import render

from exchange.services import (
    DEFAULT_SCHEMA,
    build_excel_visualization,
    export_source_payload,
    process_profit_by_group,
)
from exchange.utils import generate_random_rows


def dashboard(request):
    default_count = 30
    schema_json = json.dumps(DEFAULT_SCHEMA, ensure_ascii=False, indent=2)
    rows_json = json.dumps(generate_random_rows(default_count), ensure_ascii=False, indent=2)

    source_out = "data/source_payload.json"
    processed_out = "data/processed_payload.json"
    excel_out = "data/profit_chart.xlsx"
    source_in = source_out
    processed_in = processed_out

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        schema_json = request.POST.get("schema_json", schema_json)
        rows_json = request.POST.get("rows_json", rows_json)

        source_out = request.POST.get("source_out", source_out).strip() or source_out
        source_in = request.POST.get("source_in", source_in).strip() or source_in
        processed_out = request.POST.get("processed_out", processed_out).strip() or processed_out
        processed_in = request.POST.get("processed_in", processed_in).strip() or processed_in
        excel_out = request.POST.get("excel_out", excel_out).strip() or excel_out

        try:
            count = int(request.POST.get("count", default_count))
        except ValueError:
            count = default_count

        try:
            if action == "generate_rows":
                rows_json = json.dumps(generate_random_rows(count), ensure_ascii=False, indent=2)
                messages.success(request, f"Сгенерировано строк: {count}")

            elif action == "export_source":
                schema = json.loads(schema_json)
                rows = json.loads(rows_json)
                out = export_source_payload(schema=schema, rows=rows, out_path=source_out)
                source_in = str(out)
                messages.success(request, f"Источник выгрузил данные: {out}")

            elif action == "process_server":
                out = process_profit_by_group(source_payload_path=source_in, out_path=processed_out)
                processed_in = str(out)
                messages.success(request, f"Сервер обработал данные: {out}")

            elif action == "visualize":
                out = build_excel_visualization(processed_payload_path=processed_in, out_xlsx_path=excel_out)
                messages.success(request, f"Визуализатор сформировал Excel: {out}")

            elif action == "run_all":
                schema = json.loads(schema_json)
                rows = json.loads(rows_json)
                src = export_source_payload(schema=schema, rows=rows, out_path=source_out)
                processed = process_profit_by_group(source_payload_path=src, out_path=processed_out)
                xlsx = build_excel_visualization(processed_payload_path=processed, out_xlsx_path=excel_out)
                source_in = str(src)
                processed_in = str(processed)
                messages.success(request, f"Готово: {src} → {processed} → {xlsx}")

            else:
                messages.warning(request, "Неизвестное действие.")
        except Exception as exc:
            messages.error(request, f"Ошибка: {exc}")

    context = {
        "schema_json": schema_json,
        "rows_json": rows_json,
        "source_out": source_out,
        "source_in": source_in,
        "processed_out": processed_out,
        "processed_in": processed_in,
        "excel_out": excel_out,
        "count": default_count,
        "source_exists": Path(source_in).exists(),
        "processed_exists": Path(processed_in).exists(),
        "excel_exists": Path(excel_out).exists(),
    }
    return render(request, "exchange/dashboard.html", context)