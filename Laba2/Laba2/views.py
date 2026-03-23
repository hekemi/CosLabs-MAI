import base64
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


def _extract_numeric_values(raw):
    values = []
    if isinstance(raw, dict):
        if "values" in raw and isinstance(raw["values"], list):
            raw = raw["values"]
        else:
            for v in raw.values():
                if isinstance(v, (int, float)):
                    values.append(float(v))
            return values

    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, (int, float)):
                values.append(float(item))
            elif isinstance(item, dict) and isinstance(item.get("value"), (int, float)):
                values.append(float(item["value"]))
    return values


def _load_values():
    p = Path(settings.BASE_DIR) / "random_values.json"
    if not p.exists():
        return []
    with open(p, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return _extract_numeric_values(raw)


def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _plot_all_values(seen):
    fig, ax = plt.subplots(figsize=(7, 3))
    if len(seen):
        x = np.arange(1, len(seen) + 1)
        ax.plot(x, seen, linewidth=2)
    ax.set_title("Поступающие данные")
    ax.set_xlabel("№")
    ax.set_ylabel("Значение")
    ax.grid(True, alpha=0.3)
    return _fig_to_base64(fig)


def _plot_selected_line(selected):
    fig, ax = plt.subplots(figsize=(7, 3))
    if len(selected):
        x = np.arange(1, len(selected) + 1)
        m = float(np.mean(selected))
        ax.plot(x, selected, linewidth=2, label="Выборочные значения")
        ax.plot(x, np.full_like(x, m, dtype=float), "r--", linewidth=2, label="Среднее")
        ax.legend()
    ax.set_title("Выборочные значения + среднее")
    ax.set_xlabel("№")
    ax.set_ylabel("Значение")
    ax.grid(True, alpha=0.3)
    return _fig_to_base64(fig)


def _plot_selected_bar(selected):
    fig, ax = plt.subplots(figsize=(7, 3))
    if len(selected):
        x = np.arange(1, len(selected) + 1)
        ax.bar(x, selected)
    ax.set_title("Диаграмма выборочных значений")
    ax.set_xlabel("№")
    ax.set_ylabel("Значение")
    return _fig_to_base64(fig)


def _apply_filter(seen, filter_type, filter_value):
    arr = np.array(seen, dtype=float)
    if arr.size == 0:
        return arr

    if filter_type == "gt":
        return arr[arr > filter_value]
    if filter_type == "lt":
        return arr[arr < filter_value]
    if filter_type == "multiple":
        if filter_value == 0:
            return np.array([], dtype=float)
        # допуск для float
        rem = np.mod(arr, filter_value)
        mask = np.isclose(rem, 0.0, atol=1e-9) | np.isclose(rem, abs(filter_value), atol=1e-9)
        return arr[mask]
    return arr


def dashboard(request):
    values = _load_values()

    # Параметры интерфейса
    n1 = int(request.GET.get("n1", 5))
    n1 = max(2, min(10, n1))

    n2 = float(request.GET.get("n2", 15))
    n2 = max(5, min(40, n2))

    lower = float(request.GET.get("lower", 1))
    upper = float(request.GET.get("upper", 9))

    filter_type = request.GET.get("filter_type", "gt")
    filter_value = float(request.GET.get("filter_value", 0))

    action = request.GET.get("action", "")

    # Состояние в сессии
    idx = int(request.session.get("arm_idx", 0))
    seen = request.session.get("arm_seen", [])
    running = bool(request.session.get("arm_running", False))

    if action == "reset":
        idx, seen, running = 0, [], False
    elif action == "start":
        running = True
    elif action == "stop":
        running = False
    elif action == "next":
        running = False
        if idx < len(values):
            seen.append(float(values[idx]))
            idx += 1

    # Авто-режим: по 1 значению за запрос
    if running and idx < len(values):
        seen.append(float(values[idx]))
        idx += 1
    if idx >= len(values):
        running = False

    request.session["arm_idx"] = idx
    request.session["arm_seen"] = seen
    request.session["arm_running"] = running

    current = seen[-1] if seen else None
    prev = seen[-2] if len(seen) > 1 else None
    prev_values = seen[-(n1 + 1):-1][::-1] if len(seen) > 1 else []

    # Статус
    status = "ok"
    status_text = "Норма"
    delta_pct = None
    if current is not None and (current < lower or current > upper):
        status = "alarm"
        status_text = "Тревога: выход за допустимую область"
    elif current is not None and prev is not None and prev != 0:
        delta_pct = abs((current - prev) / prev) * 100.0
        if delta_pct > n2:
            status = "warn"
            status_text = f"Предупреждение: изменение {delta_pct:.1f}%"

    selected = _apply_filter(seen, filter_type, filter_value)
    selected_mean = float(np.mean(selected)) if selected.size else None

    context = {
        "n1": n1,
        "n2": n2,
        "lower": lower,
        "upper": upper,
        "filter_type": filter_type,
        "filter_value": filter_value,
        "current": current,
        "prev_values": prev_values,
        "selected_mean": selected_mean,
        "status": status,
        "status_text": status_text,
        "running": running,
        "all_chart": _plot_all_values(np.array(seen, dtype=float)),
        "selected_line_chart": _plot_selected_line(selected),
        "selected_bar_chart": _plot_selected_bar(selected),
    }
    return render(request, "dashboard.html", context)


def values_api(request):
    return JsonResponse({"values": _load_values()})