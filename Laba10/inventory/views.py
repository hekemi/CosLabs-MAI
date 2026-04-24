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

    qs = ProductStock.objects.filter(arrival_date__lte=report_date)

    rows = (
        qs.values("product_name")
        .annotate(total_quantity=Sum("quantity"), total_value=Sum("total_cost"))
        .order_by("product_name")
    )

    grand_total = rows.aggregate(total=Sum("total_value"))["total"] or 0

    return render(
        request,
        "inventory/report.html",
        {
            "form": form,
            "rows": rows,
            "report_date": report_date,
            "grand_total": grand_total,
        },
    )
