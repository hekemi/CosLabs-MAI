from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView

from .models import Product


class Home(ListView):
    model = Product
    template_name = 'main/index.html'
    context_object_name = 'prod'

    def get_context_data(self, *, object_list=None, **kwargs):
        params = [
            'lowblue', 'highblue',
            'lowgreen', 'highgreen',
            'loworange', 'highorange',
            'lowred', 'highred',
            'multiplicity',
        ]

        context = super().get_context_data(**kwargs)

        for key in params:
            raw = self.request.GET.get(key)
            if raw in (None, ''):
                context[key] = ''
            else:
                try:
                    context[key] = int(raw)
                except (TypeError, ValueError):
                    context[key] = ''

        return context
