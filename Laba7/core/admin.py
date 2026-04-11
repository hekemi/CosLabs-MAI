from django.contrib import admin
from .models import Department, Asset, Counterparty

admin.site.register(Department)
admin.site.register(Asset)
admin.site.register(Counterparty)