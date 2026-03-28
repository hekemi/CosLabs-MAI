from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Employee


@receiver(post_migrate)
def create_roles(sender, app_config=None, **kwargs):
    # Выполняем только после миграций приложения employees
    if app_config is None or app_config.label != "employees":
        return

    ct = ContentType.objects.get_for_model(Employee)
    perms = {
        p.codename: p
        for p in Permission.objects.filter(
            content_type=ct,
            codename__in=[
                "view_employee",
                "add_employee",
                "change_employee",
                "delete_employee",
            ],
        )
    }

    required = {"view_employee", "add_employee", "change_employee", "delete_employee"}
    if not required.issubset(perms.keys()):
        return

    director, _ = Group.objects.get_or_create(name="Директор")
    deputy, _ = Group.objects.get_or_create(name="Заместитель директора")
    secretary, _ = Group.objects.get_or_create(name="Секретарь")

    director.permissions.set(
        [
            perms["view_employee"],
            perms["add_employee"],
            perms["change_employee"],
            perms["delete_employee"],
        ]
    )
    deputy.permissions.set([perms["view_employee"], perms["change_employee"]])
    secretary.permissions.set([perms["view_employee"]])