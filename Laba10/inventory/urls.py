from django.urls import path
from .views import stock_report

app_name = "inventory"

urlpatterns = [
    path("", stock_report, name="report"),
]