import random
from datetime import date, timedelta


PRODUCTS = [
    ("Молоко", "Продукты"),
    ("Хлеб", "Продукты"),
    ("Сок", "Напитки"),
    ("Чай", "Напитки"),
    ("Мыло", "Бытовая химия"),
    ("Порошок", "Бытовая химия"),
]


def generate_random_rows(count: int) -> list[dict]:
    rows: list[dict] = []
    for _ in range(count):
        name, group = random.choice(PRODUCTS)
        qty = random.randint(1, 20)
        purchase = round(random.uniform(20, 200), 2)
        sale = round(purchase * random.uniform(1.05, 1.6), 2)
        discount = round(random.uniform(0, 15), 2)
        sale_date = (date.today() - timedelta(days=random.randint(0, 30))).isoformat()

        rows.append(
            {
                "product_name": name,
                "product_group": group,
                "sold_qty": qty,
                "sale_price": sale,
                "purchase_price": purchase,
                "discount": discount,
                "sale_date": sale_date,
            }
        )
    return rows