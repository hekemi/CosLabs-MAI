from django.urls import path

from .views import *

urlpatterns = [
    path('',index, name='home'),
    path('car/',CarListView.as_view(), name='car'),
    path('driver/',DriverListView.as_view(), name='driver'),
    path('trip/',TripListView.as_view(), name='trip'),
]