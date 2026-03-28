from django.urls import path

from exchange.views import dashboard

urlpatterns = [
    path("", dashboard, name="exchange-dashboard"),
]