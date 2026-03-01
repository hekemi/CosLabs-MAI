from django.shortcuts import render, redirect
from django.db import transaction
from decimal import Decimal
from .models import Client, Product, Order, OrderItem
from .forms import ProductForm
from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import Coalesce


CREDIT_WARNING_THRESHOLD = Decimal("0.9")

def home(request):
    # просто страница с 3 кнопками
    return render(request, "sales/home.html")


def clients_list(request):
    clients = Client.objects.all()
    return render(request, "sales/clients_list.html", {"clients": clients})


def products_list(request):
    products = Product.objects.all()
    return render(request, "sales/products_list.html", {"products": products})

def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products_list')
    else:
        form = ProductForm()
    return render(request, "sales/product_form.html", {"form": form})

from django.db.models import Sum, Count, F
from django.db.models.functions import Coalesce

def clients_orders_report(request):
    clients = (
        Client.objects
        .annotate(
            total_orders_sum=Sum('orders__total_amount', default=0),
            orders_count=Count('orders', distinct=True),
        )
    )


    clients_data = []
    for c in clients:
        product_names = (
            Product.objects
            .filter(orderitem__order__client=c)
            .distinct()
            .values_list('name', flat=True)
        )
        clients_data.append({
            "client": c,
            "total_orders_sum": c.total_orders_sum,
            "orders_count": c.orders_count,
            "product_names": ", ".join(product_names),
        })

    return render(request, "sales/clients_orders_report.html", {
        "clients_data": clients_data
    })


@transaction.atomic
def order_create(request):
    clients = Client.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        client_id = request.POST.get("client")
        payment_type = request.POST.get("payment_type")

        client = Client.objects.select_for_update().get(pk=client_id)

        # собираем товары из формы: item-0-product, item-0-qty, item-1-product...
        items = []
        index = 0
        total = Decimal("0")
        while True:
            product_id = request.POST.get(f"item-{index}-product")
            qty_str = request.POST.get(f"item-{index}-qty")
            if not product_id:
                break
            qty = Decimal(qty_str or "0")
            if qty <= 0:
                index += 1
                continue

            product = Product.objects.select_for_update().get(pk=product_id)
            price = product.price
            line_total = price * qty

            # проверка склада (кроме бартера)
            if payment_type != "barter" and qty > product.stock_qty:
                return render(request, "sales/order_form.html", {
                    "clients": clients,
                    "products": products,
                    "error": f"Недостаточно товара {product.name} на складе",
                })

            items.append((product, qty, price, line_total))
            total += line_total
            index += 1

        if not items:
            return render(request, "sales/order_form.html", {
                "clients": clients,
                "products": products,
                "error": "Добавьте хотя бы одну строку с товаром",
            })

        order = Order.objects.create(client=client, payment_type=payment_type)
        for product, qty, price, line_total in items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=price,
                line_total=line_total,
            )
            if payment_type in ("cash", "noncash", "credit"):
                product.stock_qty -= qty
            elif payment_type == "offset":
                product.stock_qty += qty
            product.save()

        order.total_amount = total
        order.save()

        # логика по типам оплаты (упрощенно)
        if payment_type == "cash":
            client.total_purchases += total
        elif payment_type == "noncash":
            client.total_purchases += total
            client.current_balance -= total
        elif payment_type == "credit":
            to_use_from_balance = min(client.current_balance, total)
            remaining_to_credit = total - to_use_from_balance
            client.current_balance -= to_use_from_balance
            client.total_purchases += total
            client.current_debt += remaining_to_credit
            if client.current_debt > client.credit_limit:
                raise ValueError("Превышен кредитный лимит клиента")
        elif payment_type == "offset":
            client.current_debt -= total
            if client.current_debt < 0:
                client.current_debt = 0
        client.save()
        return redirect("order_create")

    return render(request, "sales/order_form.html", {
        "clients": clients,
        "products": products,
    })

@transaction.atomic
def barter_create(request):
    clients = Client.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        client_id = request.POST.get("client")
        client = Client.objects.select_for_update().get(pk=client_id)

        # товары, которые ОТДАЁМ
        give_product_id = request.POST.get("give_product")
        give_qty_str = request.POST.get("give_qty")

        # товары, которые ПОЛУЧАЕМ
        receive_product_id = request.POST.get("receive_product")
        receive_qty_str = request.POST.get("receive_qty")

        if not (give_product_id and receive_product_id and give_qty_str and receive_qty_str):
            return render(request, "sales/barter_form.html", {
                "clients": clients,
                "products": products,
                "error": "Заполните оба товара и их количество.",
            })

        give_product = Product.objects.select_for_update().get(pk=give_product_id)
        receive_product = Product.objects.select_for_update().get(pk=receive_product_id)

        give_qty = Decimal(give_qty_str or "0")
        receive_qty = Decimal(receive_qty_str or "0")

        if give_qty <= 0 or receive_qty <= 0:
            return render(request, "sales/barter_form.html", {
                "clients": clients,
                "products": products,
                "error": "Количество товаров должно быть больше 0.",
            })

        # проверка склада: можем ли отдать
        if give_qty > give_product.stock_qty:
            return render(request, "sales/barter_form.html", {
                "clients": clients,
                "products": products,
                "error": f"Недостаточно товара «{give_product.name}» на складе для бартера.",
            })

        # стоимость отдаем / получаем
        give_total = give_product.price * give_qty
        receive_total = receive_product.price * receive_qty

        if give_total != receive_total:
            return render(request, "sales/barter_form.html", {
                "clients": clients,
                "products": products,
                "error": "Стоимость отдаваемых и получаемых товаров должна совпадать.",
                "give_total": give_total,
                "receive_total": receive_total,
            })

        # создаем заказ с типом "barter"
        order = Order.objects.create(
            client=client,
            payment_type="barter",
            total_amount=give_total,  # можно хранить сумму бартерной сделки
        )

        # позиция: что отдаем (кол-во отрицательное для наглядности)
        OrderItem.objects.create(
            order=order,
            product=give_product,
            quantity=-give_qty,
            price=give_product.price,
            line_total=-give_total,
        )

        # позиция: что получаем
        OrderItem.objects.create(
            order=order,
            product=receive_product,
            quantity=receive_qty,
            price=receive_product.price,
            line_total=receive_total,
        )

        # обновление склада
        give_product.stock_qty -= give_qty
        receive_product.stock_qty += receive_qty
        give_product.save()
        receive_product.save()

        # счета клиента при бартере не меняем
        return redirect("home")

    return render(request, "sales/barter_form.html", {
        "clients": clients,
        "products": products,
    })