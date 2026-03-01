from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clients/', views.clients_list, name='clients_list'),   # база клиентов
    path('products/', views.products_list, name='products_list'),# база товаров
    path('products/new/', views.product_create, name='product_create'),# создать продукт
    path('orders/new/', views.order_create, name='order_create'),# новый заказ
    path('report/clients-orders/', views.clients_orders_report, name='clients_orders_report'),# база заказов
    path('orders/barter/', views.barter_create, name='barter_create'),# бартер
]
