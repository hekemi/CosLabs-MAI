from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Max, Sum
from django.shortcuts import render

from .forms import ReportDateForm
from .models import StockEntry


def inventory_report(request):
    form = ReportDateForm(request.GET or None)
    rows = []
    grand_total = Decimal('0')
    report_date = None

    if form.is_valid():
        report_date = form.cleaned_data['report_date']
        base_qs = StockEntry.objects.filter(delivery_date__lte=report_date)

        rows = (
            base_qs.values('product_id', 'product__name')
            .annotate(
                total_quantity=Sum('quantity'),
                total_cost=Sum(
                    ExpressionWrapper(
                        F('quantity') * F('unit_price'),
                        output_field=DecimalField(max_digits=14, decimal_places=2),
                    )
                ),
                last_delivery_date=Max('delivery_date'),
            )
            .order_by('product__name')
        )

        grand_total = rows.aggregate(total=Sum('total_cost'))['total'] or Decimal('0')

    return render(
        request,
        'inventory_report/report.html',
        {
            'form': form,
            'rows': rows,
            'grand_total': grand_total,
            'report_date': report_date,
        },
    )