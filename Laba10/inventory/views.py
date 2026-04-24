from datetime import date
from django.db.models import Sum
from django.shortcuts import redirect, render
from .forms import ProductStockForm
from .models import ProductStock


def stock_report(request):
    if request.method == "POST":
        form = ProductStockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventory:report")
    else:
        form = ProductStockForm()

    date_str = request.GET.get("date")
    try:
        report_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        report_date = date.today()

    # Детализация по товарам/завозам на выбранную дату
    entries = ProductStock.objects.filter(arrival_date__lte=report_date).order_by("product_name", "arrival_date")
    grand_total = entries.aggregate(total=Sum("total_cost"))["total"] or 0

    return render(
        request,
        "inventory/report.html",
        {
            "form": form,
            "entries": entries,
            "report_date": report_date,
            "grand_total": grand_total,
        },
    )
