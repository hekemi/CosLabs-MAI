from django.urls import path
from .views import (
    HomeView,
    AssetListView,
    AssetCreateView,
    CounterpartyListView,
    CounterpartyCreateView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('assets/', AssetListView.as_view(), name='assets_list'),
    path('assets/new/', AssetCreateView.as_view(), name='assets_new'),
    path('counterparties/', CounterpartyListView.as_view(), name='counterparties_list'),
    path('counterparties/new/', CounterpartyCreateView.as_view(), name='counterparties_new'),
]