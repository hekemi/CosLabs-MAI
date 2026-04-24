from django.contrib import admin
from django.db.models.base import ModelBase

from . import models


def register_app_models():
    for attr_name in dir(models):
        model = getattr(models, attr_name)

        if (
            isinstance(model, ModelBase)
            and model._meta.app_label == "main"
            and not model._meta.abstract
        ):
            class DynamicAdmin(admin.ModelAdmin):
                list_display = [field.name for field in model._meta.fields]
                search_fields = [
                    field.name
                    for field in model._meta.fields
                    if field.get_internal_type()
                    in {
                        "CharField",
                        "TextField",
                        "EmailField",
                        "SlugField",
                        "UUIDField",
                    }
                ]

            try:
                admin.site.register(model, DynamicAdmin)
            except admin.sites.AlreadyRegistered:
                pass


register_app_models()
