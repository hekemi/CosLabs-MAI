from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_roles(sender, **kwargs):
    Employee = apps.get_model("employees", "Employee")
    ct = Employee._meta.app_label, Employee._meta.model_name

    perms = {
        "view": Permission.objects.get_by_natural_key("view_employee", *ct),
        "add": Permission.objects.get_by_natural_key("add_employee", *ct),
        "change": Permission.objects.get_by_natural_key("change_employee", *ct),
        "delete": Permission.objects.get_by_natural_key("delete_employee", *ct),
    }

    director, _ = Group.objects.get_or_create(name="Директор")
    deputy, _ = Group.objects.get_or_create(name="Заместитель директора")
    secretary, _ = Group.objects.get_or_create(name="Секретарь")

    director.permissions.set([perms["view"], perms["add"], perms["change"], perms["delete"]])
    deputy.permissions.set([perms["view"], perms["change"]])
    secretary.permissions.set([perms["view"]])